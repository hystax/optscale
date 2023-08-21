#!/usr/bin/env python

import argparse
import json
import os

from optscale_client.rest_api_client.client_v2 import Client as RestClient
from optscale_client.config_client.client import Client as ConfigClient

from bi_exporter.bumblebi.common.enums import BITypes

DEFAULT_ETCD_HOST = 'etcd'
DEFAULT_ETCD_PORT = 80


def init(rest_cli: RestClient, args: argparse.Namespace) -> None:
    ret, res = rest_cli.bi_create(
        org_id=args.org_id, type_=args.type, days=args.days, name=args.name)
    print(f"ret: {ret}")
    print(f"Created BI: {res['id']}")
    print(f"Response Body: \n{json.dumps(res, indent=4, sort_keys=True)}")


def delete(rest_cli: RestClient, args: argparse.Namespace) -> None:
    ret, res = rest_cli.bi_delete(args.bi_id)
    print(f"ret: {ret}")
    print(f"res: {res}")


def force_export(rest_cli: RestClient, args: argparse.Namespace) -> None:
    body = {
        'next_run': 1,
        'status': "ACTIVE",
        'last_status_error': None
    }
    ret, res = rest_cli.bi_update(args.bi_id, body)
    print(f"ret: {ret}")
    print(f"Response Body: \n{json.dumps(res, indent=4, sort_keys=True)}")


def list_bi(rest_cli: RestClient, args: argparse.Namespace) -> None:
    ret, res = rest_cli.bi_list(org_id=args.org_id)
    print(f"ret: {ret}")
    print(f"Response Body: \n{json.dumps(res, indent=4, sort_keys=True)}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Initialization of OrganizationBI record', add_help=True)

    subparsers = parser.add_subparsers()
    init_parser = subparsers.add_parser('init')
    init_parser.add_argument('--org_id', type=str, required=True)
    init_parser.add_argument('--days', type=int, default=180)
    init_parser.add_argument('--type', type=str, choices=list(BITypes),
                             default=BITypes.AWS_REPORT_EXPORT.value)
    init_parser.add_argument('--name', type=str, required=False)
    init_parser.set_defaults(func=init)

    rm_parser = subparsers.add_parser('rm')
    rm_parser.add_argument('--bi_id', type=str, required=True)
    rm_parser.set_defaults(func=delete)

    force_parser = subparsers.add_parser('force_export')
    force_parser.add_argument('--bi_id', type=str, required=True)
    force_parser.set_defaults(func=force_export)

    list_parser = subparsers.add_parser('list')
    list_parser.add_argument('--org_id', type=str, required=False, default=None)
    list_parser.set_defaults(func=list_bi)

    args = parser.parse_args()

    config_cl = ConfigClient(
        host=os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST),
        port=int(os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)),
    )
    config_cl.wait_configured()
    url = config_cl.restapi_url()

    rest_cl = RestClient(url=url)
    rest_cl.secret = config_cl.cluster_secret()

    vals = vars(args)
    if not any(vals.values()):
        parser.error('No arguments provided.')
    else:
        args.func(rest_cl, args)
