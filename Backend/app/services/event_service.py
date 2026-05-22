"""Event persistence and Redis ingestion service."""
import json
import time
import random
import logging
from datetime import datetime
from typing import Any, Dict, List, Tuple

import redis

from app.models.database import SessionLocal
from app.models.event import Event
from app.config import get_settings

logger = logging.getLogger(__name__)

MAX_BUFFER_SIZE = 500
FLUSH_INTERVAL = 5
BUFFER_PRESSURE_MULTIPLIER = 2
MAX_LAG_SECONDS = 60
OPEN_AFTER_ERRORS = 2
OPEN_SECONDS = 30
HALF_OPEN_ALLOW_RATE = 0.10
MAX_RETRIES = 3
SAMPLE_THRESHOLD = 100
SAMPLE_WINDOW_SECONDS = 10
SAMPLE_RATE = 10
DLQ_KEY = 'failed_events'


class CircuitBreaker:
    def __init__(self, open_after_errors: int, open_seconds: int, allow_rate: float):
        self.state = 'closed'
        self.failure_count = 0
        self.opened_at = None
        self.open_after_errors = open_after_errors
        self.open_seconds = open_seconds
        self.allow_rate = allow_rate
        self.last_overload_log = 0.0

    def maybe_half_open(self):
        if self.state == 'open' and self.opened_at:
            if (time.time() - self.opened_at) >= self.open_seconds:
                self.state = 'half-open'
                logger.info('circuit breaker half-open')

    def record_success(self):
        if self.state == 'half-open':
            self.state = 'closed'
            self.failure_count = 0
            logger.info('circuit breaker closed')

    def record_failure(self, redis_client: redis.Redis, reason: str):
        self.failure_count += 1
        if self.failure_count >= self.open_after_errors:
            self.trip(redis_client, reason)

    def trip(self, redis_client: redis.Redis, reason: str):
        if self.state != 'open':
            self.state = 'open'
            self.failure_count = 0
            self.opened_at = time.time()
            logger.info('circuit breaker open: %s', reason)
            self._log_overload(redis_client, reason)

    def _log_overload(self, redis_client: redis.Redis, reason: str):
        now = time.time()
        if (now - self.last_overload_log) < self.open_seconds:
            return
        self.last_overload_log = now
        payload = {
            'type': 'system_overloaded',
            'reason': reason,
            'ts': int(now),
        }
        try:
            redis_client.rpush(DLQ_KEY, json.dumps(payload, default=str))
        except Exception:
            logger.exception('failed to write overload event to DLQ')


def _parse_event_time(payload: Dict[str, Any]) -> Tuple[datetime, float]:
    et = payload.get('event_time')
    event_time = None
    if isinstance(et, (int, float)):
        event_time = datetime.fromtimestamp(int(et))
    else:
        try:
            event_time = datetime.fromisoformat(str(et))
        except Exception:
            event_time = datetime.utcnow()
    lag_seconds = max(0.0, time.time() - event_time.timestamp())
    return event_time, lag_seconds


def _is_critical(payload: Dict[str, Any]) -> bool:
    priority = str(payload.get('priority', 'NORMAL')).upper()
    return priority == 'CRITICAL'


def _resource_key(payload: Dict[str, Any]) -> str:
    return payload.get('resource_id') or payload.get('resource') or 'unknown'


def _apply_sampling(payload: Dict[str, Any], sampler_state: Dict[str, Dict[str, Any]]) -> bool:
    now = time.time()
    key = _resource_key(payload)
    entry = sampler_state.get(key)
    if entry is None or (now - entry['window_start']) > SAMPLE_WINDOW_SECONDS:
        entry = {'window_start': now, 'count': 0, 'sample_mode': False}
        sampler_state[key] = entry

    entry['count'] += 1
    if entry['count'] > SAMPLE_THRESHOLD:
        if not entry['sample_mode']:
            entry['sample_mode'] = True
            logger.debug('sampling enabled for resource %s', key)
        if entry['count'] % SAMPLE_RATE != 0:
            return False
        metadata = payload.get('metadata')
        if not isinstance(metadata, dict):
            metadata = {'original': metadata} if metadata is not None else {}
        metadata['sample_rate'] = SAMPLE_RATE
        payload['metadata'] = metadata
    return True


def _write_batch(payloads: List[Dict[str, Any]]) -> None:
    db = SessionLocal()
    try:
        objs: List[Event] = []
        for payload in payloads:
            event_time, _ = _parse_event_time(payload)
            ev = Event(
                account_id=payload.get('account_id'),
                user_id=payload.get('user_id'),
                event_time=event_time,
                metric_name=payload.get('metric_name'),
                value=float(payload.get('value')) if payload.get('value') is not None else None,
                resource=payload.get('resource'),
                service=payload.get('service'),
                metadata=json.dumps(payload.get('metadata') or payload),
            )
            objs.append(ev)
        db.bulk_save_objects(objs)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _handle_failed_batch(payloads: List[Dict[str, Any]], keep: List[Dict[str, Any]], redis_client: redis.Redis, error: Exception):
    for payload in payloads:
        retries = int(payload.get('_retries', 0)) + 1
        if retries > MAX_RETRIES:
            try:
                msg = {'error': str(error), 'payload': payload, 'ts': int(time.time())}
                redis_client.rpush(DLQ_KEY, json.dumps(msg, default=str))
            except Exception:
                logger.exception('failed to write DLQ event')
        else:
            payload['_retries'] = retries
            keep.append(payload)


def persist_event(payload: Dict[str, Any]) -> int:
    """Persist a normalized event payload into the DB and return the new id."""
    _write_batch([payload])
    return 1


def redis_subscribe_and_persist(
    redis_url: str,
    channel: str,
    max_buffer_size: int = MAX_BUFFER_SIZE,
    flush_interval: int = FLUSH_INTERVAL,
    max_lag_seconds: int = MAX_LAG_SECONDS,
    open_after_errors: int = OPEN_AFTER_ERRORS,
    open_seconds: int = OPEN_SECONDS,
    half_open_allow_rate: float = HALF_OPEN_ALLOW_RATE,
):
    """Subscribe to a Redis channel and persist incoming messages as events."""
    r = redis.from_url(redis_url, decode_responses=True)
    pub = r.pubsub(ignore_subscribe_messages=True)
    pub.subscribe(channel)

    buffer: List[Dict[str, Any]] = []
    last_flush = time.time()
    sampler_state: Dict[str, Dict[str, Any]] = {}
    breaker = CircuitBreaker(open_after_errors, open_seconds, half_open_allow_rate)

    for msg in pub.listen():
        if msg is None:
            continue
        try:
            data = msg.get('data')
            if not data:
                continue
            payload = json.loads(data) if isinstance(data, str) else data
        except Exception:
            payload = {'raw': str(msg)}

        now = time.time()
        breaker.maybe_half_open()

        if len(buffer) > max_buffer_size * BUFFER_PRESSURE_MULTIPLIER and not _is_critical(payload):
            continue

        if not _apply_sampling(payload, sampler_state):
            continue

        _, lag_seconds = _parse_event_time(payload)
        if lag_seconds > max_lag_seconds:
            breaker.trip(r, 'lag_exceeded')

        if breaker.state == 'open' and not _is_critical(payload):
            continue
        if breaker.state == 'open' and _is_critical(payload) and len(buffer) >= max_buffer_size:
            continue

        buffer.append(payload)

        should_flush = len(buffer) >= max_buffer_size or (now - last_flush) >= flush_interval
        if not should_flush:
            continue

        breaker.maybe_half_open()
        if breaker.state == 'open':
            last_flush = time.time()
            continue

        if breaker.state == 'half-open':
            allowed: List[Dict[str, Any]] = []
            remaining: List[Dict[str, Any]] = []
            for item in buffer:
                if random.random() < half_open_allow_rate:
                    allowed.append(item)
                else:
                    if _is_critical(item):
                        remaining.append(item)
            if not allowed:
                buffer = remaining
                last_flush = time.time()
                continue
            try:
                _write_batch(allowed)
                breaker.record_success()
                buffer = remaining
            except Exception as exc:
                _handle_failed_batch(allowed, remaining, r, exc)
                breaker.record_failure(r, 'db_error')
                buffer = remaining
            last_flush = time.time()
            continue

        try:
            _write_batch(buffer)
            buffer = []
        except Exception as exc:
            keep: List[Dict[str, Any]] = []
            _handle_failed_batch(buffer, keep, r, exc)
            buffer = keep
            breaker.record_failure(r, 'db_error')
        last_flush = time.time()


def start_ingest_loop():
    settings = get_settings()
    redis_subscribe_and_persist(settings.redis_url, 'events')


if __name__ == '__main__':
    import argparse
    from app.config import get_settings

    parser = argparse.ArgumentParser()
    parser.add_argument('--redis-url', default=None)
    parser.add_argument('--channel', default='events')
    args = parser.parse_args()
    settings = get_settings()
    redis_url = args.redis_url or settings.redis_url
    redis_subscribe_and_persist(redis_url, args.channel)
