"""Runner script to start Redis ingestion loop which persists Event rows."""
from app.services.event_service import redis_subscribe_and_persist


def main():
    import argparse
    from app.config import get_settings

    parser = argparse.ArgumentParser()
    parser.add_argument('--redis-url', default=None)
    parser.add_argument('--channel', default='events')
    parser.add_argument('--buffer-size', type=int, default=500)
    parser.add_argument('--flush-interval', type=int, default=5)
    parser.add_argument('--max-lag-seconds', type=int, default=60)
    parser.add_argument('--open-after-errors', type=int, default=2)
    parser.add_argument('--open-seconds', type=int, default=30)
    parser.add_argument('--half-open-allow-rate', type=float, default=0.10)
    args = parser.parse_args()

    settings = get_settings()
    redis_url = args.redis_url or settings.redis_url
    redis_subscribe_and_persist(
        redis_url,
        args.channel,
        max_buffer_size=args.buffer_size,
        flush_interval=args.flush_interval,
        max_lag_seconds=args.max_lag_seconds,
        open_after_errors=args.open_after_errors,
        open_seconds=args.open_seconds,
        half_open_allow_rate=args.half_open_allow_rate,
    )


if __name__ == '__main__':
    main()
