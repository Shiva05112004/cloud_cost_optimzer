"""Runner script for the CloudWatch log streamer (test-file mode supported)."""
from app.cloud_api.log_streamer import stream_log_group


def main():
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument('--role-arn', default=None)
    p.add_argument('--account-id', type=int, required=True)
    p.add_argument('--log-group', default='/aws/lambda/example')
    p.add_argument('--redis-channel', default='events')
    p.add_argument('--poll-interval', type=int, default=15)
    p.add_argument('--test-file', default=None)
    args = p.parse_args()

    stream_log_group(args.role_arn, args.account_id, args.log_group, args.redis_channel, args.poll_interval, args.test_file)


if __name__ == '__main__':
    main()
