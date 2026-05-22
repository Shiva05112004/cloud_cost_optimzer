"""CloudWatch Log streamer -> Redis Pub/Sub (Phase 1)

Provides a simple poller for CloudWatch Log Groups and a test-mode that
reads events from a local JSON file and publishes them to the configured
Redis channel.
"""
import time
import json
import logging
from typing import Optional

import redis

from app.cloud_api.ec2_client import get_boto3_session
from app.config import get_settings

logger = logging.getLogger(__name__)


def publish_messages(redis_url: str, channel: str, messages: list):
    r = redis.from_url(redis_url)
    for msg in messages:
        try:
            r.publish(channel, json.dumps(msg, default=str))
        except Exception:
            logger.exception('failed to publish message')


def stream_log_group(role_arn: Optional[str], account_id: int, log_group: str, redis_channel: str, poll_interval: int = 15, test_file: Optional[str] = None):
    settings = get_settings()
    redis_url = settings.redis_url

    if test_file:
        with open(test_file, 'r', encoding='utf8') as fh:
            data = json.load(fh)
        # Expecting a list of CloudWatch-style events or normalized payloads
        publish_messages(redis_url, redis_channel, data)
        return

    session = get_boto3_session(role_arn)
    logs = session.client('logs', region_name=settings.aws_default_region)

    next_token = None
    # start from recent hour
    start_time = int((time.time() - 60 * 60) * 1000)

    while True:
        kwargs = dict(logGroupName=log_group, startTime=start_time, limit=100)
        if next_token:
            kwargs['nextToken'] = next_token

        try:
            resp = logs.filter_log_events(**kwargs)
        except Exception:
            logger.exception('CloudWatch filter_log_events failed, backing off')
            time.sleep(poll_interval)
            continue

        events = resp.get('events', []) or []
        if events:
            payloads = []
            for e in events:
                # normalize the event into a small payload
                ts = e.get('timestamp')
                try:
                    message = json.loads(e.get('message', '') or '{}')
                except Exception:
                    message = {'message': e.get('message', '')}

                payload = {
                    'account_id': account_id,
                    'event_time': int(ts / 1000) if ts else None,
                    'metric_name': message.get('metric') or message.get('metric_name') or 'log',
                    'value': message.get('value'),
                    'resource': message.get('resource'),
                    'service': message.get('service'),
                    'metadata': message,
                }
                payloads.append(payload)

            publish_messages(redis_url, redis_channel, payloads)

        next_token = resp.get('nextToken')
        time.sleep(poll_interval)


if __name__ == '__main__':
    import argparse

    logging.basicConfig(level=logging.INFO)
    p = argparse.ArgumentParser()
    p.add_argument('--role-arn', default=None)
    p.add_argument('--account-id', type=int, required=True)
    p.add_argument('--log-group', required=True)
    p.add_argument('--redis-channel', default='events')
    p.add_argument('--poll-interval', type=int, default=15)
    p.add_argument('--test-file', default=None)
    args = p.parse_args()
    stream_log_group(args.role_arn, args.account_id, args.log_group, args.redis_channel, args.poll_interval, args.test_file)
