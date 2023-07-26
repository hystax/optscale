import argparse
import logging
import os
from datetime import datetime
from generate_demo_preset import PresetGenerator, GeneratorSettings

DEFAULT_ETCD_HOST = 'etcd'
DEFAULT_ETCD_PORT = 80


def main():
    log_format = '%(asctime)-15s %(message)s'
    logging.basicConfig(format=log_format, level=logging.INFO)

    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)

    parser = argparse.ArgumentParser()
    parser.add_argument('--etcd_host', type=str, default=etcd_host)
    parser.add_argument('--etcd_port', type=int, default=etcd_port)
    parser.add_argument('--organization_id', type=str)
    parser.add_argument('--top_res_cnt', type=int)
    parser.add_argument('--top_res_with_raw', type=int)
    args = parser.parse_args()
    generator = PresetGenerator(
        args.etcd_host, args.etcd_port,
        GeneratorSettings(
            organization_id=args.organization_id,
            top_res_cnt=args.top_res_cnt,
            top_res_with_raw=args.top_res_with_raw,
            output_file='%s_dump.json' % int(datetime.utcnow().timestamp()),
            anonymize=False
        )
    )
    try:
        generator.generate()
    finally:
        generator.cleanup()


if __name__ == "__main__":
    main()
