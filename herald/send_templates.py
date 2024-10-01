#!/usr/bin/env python
import argparse
import logging
import os
import sys
import re
from operator import itemgetter

import requests
import urllib3
from uuid import UUID
from os.path import isfile, join

PARAMETER_DUMPS = {
    'alert': {
        "email": ["kowalski@mail.mg"],
        "subject": "OptScale Pool limit alert",
        "template_type": "alert",
        "template_params": {
            "texts": {
                "organization": {
                    "name": "New York Central Park Zoo",
                    "id": "c432cbd6-ab2b-4c6f-a601-c71c11b5502b",
                    "currency_code": "$"
                },
                "pool_name": "Zoo-org",
                "alert_type": "cost",
                "threshold": "$5",
            }
        }
    },
    'employee_greetings': {
        'email': ['andersonmatthew_hwp@hystax.com'],
        'subject': 'Thank you for registering at OptScale. Please proceed with the setup',
        'template_type': 'employee_greetings',
        'template_params': {
            'texts': {
                'name': 'andersonmatthew',
                'token': 'MDAwZWxvY2F0aW9uIAowMDJlaWRlbnRpZmllciBhbmRlcnNvbm1hdHRoZXdfaHdwQGh5c3RheC5jb20KMDAyZGNpZCBlb'
                         'WFpbDphbmRlcnNvbm1hdHRoZXdfaHdwQGh5c3RheC5jb20KMDAyMWNpZCBjcmVhdGVkOjE2MTcxOTg1MTMuNjk3MTIKMD'
                         'AyZnNpZ25hdHVyZSB-fYhK5DixwPGK5RlnWa1TXEdUSuWLZ_XP9JUTn8jQogo',
                'organization': {
                    'id': 'd7092814-2b12-4e60-89c5-67919c9b17d6',
                    'name': 'Funny company',
                    'currency_code': '$'
                }}}},
    'invite': {
        "email": ["me@1.com"],
        "subject": "OptScale invitation notification",
        "template_type": "invite",
        "template_params": {
            "texts": {
                "organization": {
                    'id': "95a42273-2e87-4749-aa11-e60a61dcc0b8",
                    'name': "ishorg",
                    'currency_code': '$'
                }
            },
            "links": {
                "login_button": "https://172.22.20.8/login?email=me%401.ru&next=accept-invitation?inviteId=ffd31ed0"
                                "-1886-4ed2-b7e6-2dfcbc7bb4d0 "
            }
        }
    },
    'new_cloud_account': {
        "email": ["optscale-staging-notifications@hystax.com"],
        "subject": "[172.22.20.8] Data source has been connected",
        "template_type": "new_cloud_account",
        "template_params": {
            "texts": {
                "cloud_account_id": "cb40fab5-3247-4064-b416-c3632786707a",
                "cloud_account_name": "aws",
                "cloud_account_type": "aws_cnr",
                "organization": {
                    'id': "a550ba8f-2766-4a4c-ba07-84a502ecca10",
                    "name": "Twister Inc.",
                    "currency_code": "$"
                },
                "user_email": "me2@1.com",
                "user_name": "Mr Twister"
            }
        }
    },
    'cloud_account_deleted': {
        "email": ["optscale-staging-notifications@hystax.com"],
        "subject": "[172.22.20.8] Data source has been deleted",
        "template_type": "cloud_account_deleted",
        "template_params": {
            "texts": {
                "cloud_account_id": "cb40fab5-3247-4064-b416-c3632786707a",
                "cloud_account_name": "aws",
                "cloud_account_type": "aws_cnr",
                "organization": {
                    'id': "a550ba8f-2766-4a4c-ba07-84a502ecca10",
                    "name": "Twister Inc.",
                    "currency_code": "$"
                },
                "user_email": "me2@1.ru",
                "user_name": "Mr Twister"
            }
        }
    },
    'organization_audit_submit': {
        "email": ["optscale-staging-notifications@hystax.com"],
        "subject": "[172.22.20.8] Organization submitted for technical audit",
        "template_type": "organization_audit_submit",
        "template_params": {
            "texts": {

                "organization": {
                    "id": "a550ba8f-2766-4a4c-ba07-84a502ecca10",
                    "name": "Twister Inc.",
                    "currency_code": "$"
                },
                "employee": {
                    "id": "cb40fab5-3247-4064-b416-c3632786707a",
                    "name": "Twister Inc."
                }
            }
        }
    },
    'new_employee': {
        "email": ["optscale-staging-notifications@hystax.com"],
        "subject": "[172.22.20.8] New user joined organization",
        "template_type": "new_employee",
        "reply_to_email": "me2@1.com",
        "template_params": {
            "texts": {
                "organization": {
                    "id": "a550ba8f-2766-4a4c-ba07-84a502ecca10",
                    "name": "Twister Inc.",
                    "currency_code": "$"
                },
                "user": {
                    "id": "63b4c37e-ce9b-47fb-be38-413a23168ae3",
                    "email": "me2@1.com",
                    "authentication_type": "password"
                },
                "users_count": 2,
            }
        }
    },
    'new_subscriber': {
        "email": ["optscale-staging-notifications@hystax.com"],
        "subject": "[172.22.20.8] New live demo subscriber",
        "template_type": "new_subscriber",
        "reply_to_email": "me2@1.com",
        "template_params": {
            "texts": {
                "user": {
                    "email": "me2@1.com",
                    "subscribe": True
                },
            }
        }
    },
    'pool_exceed_report': {
        'email': ['james31_pza@hystax.com'],
        'subject': 'Action Required: Hystax OptScale Pool Limit Exceed Alert',
        'template_type': 'pool_exceed_report',
        'template_params': {
            'texts': {
                'total_forecast': 293.5,
                'exceeded': [
                    {
                        'forecast': 293.5,
                        'id': '950251a8-49e4-4f06-a93e-ee4faed97701',
                        'limit': 50,
                        'pool_name': 'AQA_1617018508.3637385. It is very very very very very very very very very '
                                       'very very very very very very very long name',
                        'total_expenses': 293.5
                    },
                    {
                        'forecast': 293.5,
                        'id': '9e07786f-c476-484e-adc5-43d76815bd1d',
                        'limit': 100,
                        'pool_name': 'AQA_CA_1617018508.3637757_find_report',
                        'total_expenses': 293.5
                    }
                ],
                'organization': {
                    'id': '6946211f-47ff-43a3-a9a3-3e5f57d52415',
                    'name': 'AQA_1617018508.3637385',
                    'currency_code': '$'
                }
            }
        }
    },
    'pool_exceed_resources_report': {
        'email': ['ranxygcrfg@novaemail.com'],
        'subject': 'Action Required: Hystax OptScale Pool Limit Exceed Alert',
        'template_type': 'pool_exceed_resources_report',
        'template_params': {
            'texts': {
                'exceeded_pools_count': 2,
                'exceeded_pool_forecasts_count': 2,
                "exceeded_pool_forecasts": [
                    {
                        'forecast': 448.72,
                        'limit': 100,
                        'pool_id': '6e4c3ef9-37a9-47ec-87f7-0a864af86016',
                        'pool_name': 'Dalek Industry pool',
                        'pool_purpose': 'business_unit',
                        'total_expenses': 448.72,
                        "resources": [
                            {
                                'active': True,
                                'cloud_account_id': '5c1ed35a-bf6b-4c7d-897a-8388b220fff3',
                                'cloud_account_name': 'AWS linked',
                                'cloud_console_link': 'https://console.aws.amazon.com/ec2/v2/home?region=us-west-2'
                                                      '#InstanceDetails:instanceId=i-082b1a163698b8ede',
                                'cloud_created_at': 1607326764,
                                'cloud_resource_id': 'i-082b1a163698b8ede',
                                'flavor': 't2.large',
                                'image_id': 'ami-09d7e4ccf2c68700d',
                                'last_seen': 1617152478,
                                'last_seen_not_stopped': 1617152478,
                                'organization_id': '955f3783-ad70-4ad8-9682-b64890ef95c6',
                                'owner_id': '0b2287ea-c543-4b47-a8aa-a2953fad9eb4',
                                'owner_name': 'Tester',
                                'name': 'HystaxWebSite. It is very very very very very very very very very very very '
                                        'very very very very very long name',
                                'pool_id': '6e4c3ef9-37a9-47ec-87f7-0a864af86016',
                                'pool_name': 'Dalek Industry',
                                'pool_purpose': 'business_unit',
                                'region': 'us-west-2',
                                'resource_id': 'd3809841-eb70-4568-bb02-e962e401fdca',
                                'spotted': False,
                                'stopped_allocated': False,
                                'type': 'instance',
                                'security_groups': [
                                    {
                                        'GroupId': 'sg-0d99e8ecd70254ebe',
                                        'GroupName': 'websites'}],
                                'tags': {
                                    'aws:createdBy': 'IAMUser:AIDA4YBYU3OICYSASYZ2E:pkozlov'
                                }
                            }
                        ]
                    },
                    {
                        'forecast': 448.72,
                        'limit': 100,
                        'pool_id': '6e4c3ef9-37a9-47ec-87f7-0a864af86016',
                        'pool_name': 'My Pool',
                        'pool_purpose': 'business_unit',
                        'total_expenses': 448.72,
                        "resources": [
                            {
                                'active': True,
                                'cloud_account_id': '5c1ed35a-bf6b-4c7d-897a-8388b220fff3',
                                'cloud_account_name': 'AWS linked',
                                'cloud_console_link': 'https://console.aws.amazon.com/ec2/v2/home?region=us-west-2'
                                                      '#InstanceDetails:instanceId=i-082b1a163698b8ede',
                                'cloud_created_at': 1607326764,
                                'cloud_resource_id': 'i-082b1a163698b8ede',
                                'flavor': 't2.large',
                                'image_id': 'ami-09d7e4ccf2c68700d',
                                'last_seen': 1617152478,
                                'last_seen_not_stopped': 1617152478,
                                'organization_id': '955f3783-ad70-4ad8-9682-b64890ef95c6',
                                'owner_id': '0b2287ea-c543-4b47-a8aa-a2953fad9eb4',
                                'owner_name': 'Tester',
                                'name': 'HystaxWebSite. It is very very very very very very very very very very very '
                                        'very very very very very long name',
                                'pool_id': '6e4c3ef9-37a9-47ec-87f7-0a864af86016',
                                'pool_name': 'Dalek Industry',
                                'pool_purpose': 'business_unit',
                                'region': 'us-west-2',
                                'resource_id': 'd3809841-eb70-4568-bb02-e962e401fdca',
                                'spotted': False,
                                'stopped_allocated': False,
                                'type': 'instance',
                                'security_groups': [
                                    {
                                        'GroupId': 'sg-0d99e8ecd70254ebe',
                                        'GroupName': 'websites'}],
                                'tags': {
                                    'aws:createdBy': 'IAMUser:AIDA4YBYU3OICYSASYZ2E:pkozlov'
                                }
                            }
                        ]
                    }
                ],
                'exceeded_pools': [
                    {
                        'forecast': 448.72,
                        'limit': 100,
                        'pool_id': '6e4c3ef9-37a9-47ec-87f7-0a864af86016',
                        'pool_name': 'My pool',
                        'pool_purpose': 'business_unit',
                        'total_expenses': 448.72,
                        "resources": [
                            {
                                'active': True,
                                'cloud_account_id': '5c1ed35a-bf6b-4c7d-897a-8388b220fff3',
                                'cloud_account_name': 'AWS linked',
                                'cloud_console_link': 'https://console.aws.amazon.com/ec2/v2/home?region=us-west-2'
                                                      '#InstanceDetails:instanceId=i-082b1a163698b8ede',
                                'cloud_created_at': 1607326764,
                                'cloud_resource_id': 'i-082b1a163698b8ede',
                                'flavor': 't2.large',
                                'image_id': 'ami-09d7e4ccf2c68700d',
                                'last_seen': 1617152478,
                                'last_seen_not_stopped': 1617152478,
                                'organization_id': '955f3783-ad70-4ad8-9682-b64890ef95c6',
                                'owner_id': '0b2287ea-c543-4b47-a8aa-a2953fad9eb4',
                                'owner_name': 'Tester',
                                'name': 'HystaxWebSite. It is very very very very very very very very very very very '
                                        'very very very very very long name',
                                'pool_id': '6e4c3ef9-37a9-47ec-87f7-0a864af86016',
                                'pool_name': 'Dalek Industry',
                                'pool_purpose': 'business_unit',
                                'region': 'us-west-2',
                                'resource_id': 'd3809841-eb70-4568-bb02-e962e401fdca',
                                'spotted': False,
                                'stopped_allocated': False,
                                'type': 'instance',
                                'security_groups': [
                                    {
                                        'GroupId': 'sg-0d99e8ecd70254ebe',
                                        'GroupName': 'websites'}],
                                'tags': {
                                    'aws:createdBy': 'IAMUser:AIDA4YBYU3OICYSASYZ2E:pkozlov'
                                }
                            }
                        ]
                    },
                    {
                        'forecast': 448.72,
                        'limit': 100,
                        'pool_id': '6e4c3ef9-37a9-47ec-87f7-0a864af86016',
                        'pool_name': 'Dalek Industry pool',
                        'pool_purpose': 'business_unit',
                        'total_expenses': 448.72,
                        'resources': [
                            {
                                'active': True,
                                'cloud_account_id': '5c1ed35a-bf6b-4c7d-897a-8388b220fff3',
                                'cloud_account_name': 'AWS linked',
                                'cloud_console_link': 'https://console.aws.amazon.com/ec2/v2/home?region=us-west-2'
                                                      '#InstanceDetails:instanceId=i-082b1a163698b8ede',
                                'cloud_created_at': 1607326764,
                                'cloud_resource_id': 'i-082b1a163698b8ede',
                                'flavor': 't2.large',
                                'image_id': 'ami-09d7e4ccf2c68700d',
                                'last_seen': 1617152478,
                                'last_seen_not_stopped': 1617152478,
                                'organization_id': '955f3783-ad70-4ad8-9682-b64890ef95c6',
                                'owner_id': '0b2287ea-c543-4b47-a8aa-a2953fad9eb4',
                                'owner_name': 'Tester',
                                'name': 'HystaxWebSite. It is very very very very very very very very very very very '
                                        'very very very very very long name',
                                'pool_id': '6e4c3ef9-37a9-47ec-87f7-0a864af86016',
                                'pool_name': 'Dalek Industry',
                                'pool_purpose': 'business_unit',
                                'region': 'us-west-2',
                                'resource_id': 'd3809841-eb70-4568-bb02-e962e401fdca',
                                'spotted': False,
                                'stopped_allocated': False,
                                'type': 'instance',
                                'security_groups': [
                                    {
                                        'GroupId': 'sg-0d99e8ecd70254ebe',
                                        'GroupName': 'websites'}],
                                'tags': {
                                    'aws:createdBy': 'IAMUser:AIDA4YBYU3OICYSASYZ2E:pkozlov'}},
                            {
                                'active': True,
                                'cloud_account_id': '5c1ed35a-bf6b-4c7d-897a-8388b220fff3',
                                'cloud_account_name': 'AWS linked',
                                'cloud_console_link': 'https://console.aws.amazon.com/ec2/v2/home?region=us-west-2'
                                                      '#InstanceDetails:instanceId=i-00360dfdf85958d24',
                                'cloud_created_at': 1607326819,
                                'cloud_resource_id': 'i-00360dfdf85958d24',
                                'flavor': 't2.large',
                                'image_id': 'ami-057935eae1159db28',
                                'last_seen': 1617152478,
                                'last_seen_not_stopped': 1617152478,
                                'name': 'OptScaleWebSite',
                                'organization_id': '955f3783-ad70-4ad8-9682-b64890ef95c6',
                                'owner_id': '0b2287ea-c543-4b47-a8aa-a2953fad9eb4',
                                'owner_name': 'Tester',
                                'pool_id': '6e4c3ef9-37a9-47ec-87f7-0a864af86016',
                                'pool_name': 'Dalek Industry',
                                'pool_purpose': 'business_unit',
                                'region': 'us-west-2',
                                'resource_id': '56c9b581-20cd-41b6-af1d-be37c4c8cf64',
                                'spotted': False,
                                'stopped_allocated': False,
                                'type': 'instance',
                                'security_groups': [
                                    {
                                        'GroupId': 'sg-0d99e8ecd70254ebe',
                                        'GroupName': 'websites'}],
                                'tags': {
                                    'aws:createdBy': 'IAMUser:AIDA4YBYU3OICYSASYZ2E:pkozlov'}},
                            {
                                'active': True,
                                'cloud_account_id': '5c1ed35a-bf6b-4c7d-897a-8388b220fff3',
                                'cloud_account_name': 'AWS linked',
                                'cloud_console_link': 'https://console.aws.amazon.com/ec2/v2/home?region=us-west-2'
                                                      '#InstanceDetails:instanceId=i-0e464cfbf9650bd21',
                                'cloud_created_at': 1607339156,
                                'cloud_resource_id': 'i-0e464cfbf9650bd21',
                                'flavor': 't2.large',
                                'image_id': 'ami-0896ae01b544f65a8',
                                'last_seen': 1617152478,
                                'last_seen_not_stopped': 1617152478,
                                'name': 'finops-practice',
                                'organization_id': '955f3783-ad70-4ad8-9682-b64890ef95c6',
                                'owner_id': '0b2287ea-c543-4b47-a8aa-a2953fad9eb4',
                                'owner_name': 'Tester',
                                'pool_id': '6e4c3ef9-37a9-47ec-87f7-0a864af86016',
                                'pool_name': 'Dalek Industry',
                                'pool_purpose': 'business_unit',
                                'region': 'us-west-2',
                                'resource_id': '422e7381-56cd-4d67-a8e8-2429691536f1',
                                'spotted': False,
                                'stopped_allocated': False,
                                'type': 'instance',
                                'security_groups': [
                                    {
                                        'GroupId': 'sg-0d99e8ecd70254ebe',
                                        'GroupName': 'websites'}],
                                'tags': {
                                    'aws:createdBy': 'IAMUser:AIDA4YBYU3OICYSASYZ2E:pkozlov'}},
                            {
                                'active': True,
                                'attached': False,
                                'cloud_account_id': 'ba5a7439-df3a-4d41-9244-4927b80770f2',
                                'cloud_account_name': 'AWS',
                                'cloud_console_link': 'https://console.aws.amazon.com/ec2/v2/home?region=eu-central-1'
                                                      '#Volumes:volumeId=vol-01b510489d2a9cd00',
                                'cloud_resource_id': 'vol-01b510489d2a9cd00',
                                'last_attached': 0,
                                'last_seen': 1617152217,
                                'name': 'ish-ami-deletion-test-volume',
                                'organization_id': '955f3783-ad70-4ad8-9682-b64890ef95c6',
                                'owner_id': '0b2287ea-c543-4b47-a8aa-a2953fad9eb4',
                                'owner_name': 'Tester',
                                'pool_id': '6e4c3ef9-37a9-47ec-87f7-0a864af86016',
                                'pool_name': 'Dalek Industry',
                                'pool_purpose': 'business_unit',
                                'region': 'eu-central-1',
                                'resource_id': '2a003a1f-0e66-4bc6-8d38-7036b15720a6',
                                'size': 1,
                                'snapshot_id': None,
                                'type': 'volume',
                                'volume_type': 'gp2',
                                'tags': {
                                    'aws:createdBy': 'Root:044478323321'}},
                            {
                                'active': True,
                                'attached': False,
                                'cloud_account_id': 'ba5a7439-df3a-4d41-9244-4927b80770f2',
                                'cloud_account_name': 'AWS',
                                'cloud_console_link': 'https://console.aws.amazon.com/ec2/v2/home?region=eu-central-1'
                                                      '#Volumes:volumeId=vol-0753b8ad653355bda',
                                'cloud_resource_id': 'vol-0753b8ad653355bda',
                                'last_attached': 1609330672,
                                'last_seen': 1617152217,
                                'name': 'ubuntu-ducky_15ad46bc-1b5c-b22d-9cd1-928241c509c5',
                                'organization_id': '955f3783-ad70-4ad8-9682-b64890ef95c6',
                                'owner_id': '0b2287ea-c543-4b47-a8aa-a2953fad9eb4',
                                'owner_name': 'Tester',
                                'pool_id': '6e4c3ef9-37a9-47ec-87f7-0a864af86016',
                                'pool_name': 'Dalek Industry',
                                'pool_purpose': 'business_unit',
                                'region': 'eu-central-1',
                                'resource_id': 'afdfc60f-0b2b-4bc6-aa5b-c9f74470bbe5',
                                'size': 5,
                                'snapshot_id': None,
                                'type': 'volume',
                                'volume_type': 'gp2',
                                'tags': {
                                    'aws:createdBy': 'IAMUser:AIDAJGWH6JNRGDXONCBLI:va-iam-full',
                                    'hystax_backup_id': '53310f74-00be-4696-b752-8b30155e90fe',
                                    'hystax_device_id': '8bee6539-8260-8f59-cd9b-f2c3b9a87a44',
                                    'hystax_device_name': 'ubuntu-ducky',
                                    'hystax_type': 'acura'}},
                            {
                                'active': True,
                                'attached': True,
                                'cloud_account_id': '5c1ed35a-bf6b-4c7d-897a-8388b220fff3',
                                'cloud_account_name': 'AWS linked',
                                'cloud_console_link': 'https://console.aws.amazon.com/ec2/v2/home?region=us-west-2'
                                                      '#Volumes:volumeId=vol-01ddb07d1f7d3eaa1',
                                'cloud_resource_id': 'vol-01ddb07d1f7d3eaa1',
                                'last_attached': 1617152218,
                                'last_seen': 1617152217,
                                'name': '',
                                'organization_id': '955f3783-ad70-4ad8-9682-b64890ef95c6',
                                'owner_id': '0b2287ea-c543-4b47-a8aa-a2953fad9eb4',
                                'owner_name': 'Tester',
                                'pool_id': '6e4c3ef9-37a9-47ec-87f7-0a864af86016',
                                'pool_name': 'Dalek Industry',
                                'pool_purpose': 'business_unit',
                                'region': 'us-west-2',
                                'resource_id': 'ce72bdc8-eb36-43e9-8288-d3ea50077fc7',
                                'size': 30,
                                'snapshot_id': 'snap-0bb2b0d4627a9ea92',
                                'type': 'volume',
                                'volume_type': 'gp3',
                                'tags': {}},
                            {
                                'active': True,
                                'attached': True,
                                'cloud_account_id': '5c1ed35a-bf6b-4c7d-897a-8388b220fff3',
                                'cloud_account_name': 'AWS linked',
                                'cloud_console_link': 'https://console.aws.amazon.com/ec2/v2/home?region=us-west-2'
                                                      '#Volumes:volumeId=vol-0d2a2bc4145146934',
                                'cloud_resource_id': 'vol-0d2a2bc4145146934',
                                'last_attached': 1617152218,
                                'last_seen': 1617152217,
                                'name': '',
                                'organization_id': '955f3783-ad70-4ad8-9682-b64890ef95c6',
                                'owner_id': '0b2287ea-c543-4b47-a8aa-a2953fad9eb4',
                                'owner_name': 'Tester',
                                'pool_id': '6e4c3ef9-37a9-47ec-87f7-0a864af86016',
                                'pool_name': 'Dalek Industry',
                                'pool_purpose': 'business_unit',
                                'region': 'us-west-2',
                                'resource_id': 'df705cae-5e13-47da-b1a8-fddde6a2b037',
                                'size': 40,
                                'snapshot_id': 'snap-0e2213980002234ef',
                                'volume_type': 'gp3',
                                'type': 'volume',
                                'tags': {}},
                            {
                                'active': True,
                                'attached': True,
                                'cloud_account_id': '5c1ed35a-bf6b-4c7d-897a-8388b220fff3',
                                'cloud_account_name': 'AWS linked',
                                'cloud_console_link': 'https://console.aws.amazon.com/ec2/v2/home?region=us-west-2'
                                                      '#Volumes:volumeId=vol-0b1884d70bf748195',
                                'cloud_resource_id': 'vol-0b1884d70bf748195',
                                'last_attached': 1617152218,
                                'last_seen': 1617152217,
                                'name': '',
                                'organization_id': '955f3783-ad70-4ad8-9682-b64890ef95c6',
                                'owner_id': '0b2287ea-c543-4b47-a8aa-a2953fad9eb4',
                                'owner_name': 'Tester',
                                'pool_id': '6e4c3ef9-37a9-47ec-87f7-0a864af86016',
                                'pool_name': 'Dalek Industry',
                                'pool_purpose': 'business_unit',
                                'region': 'us-west-2',
                                'resource_id': 'f905da3a-ef30-4c57-bb62-f34b0f140fd9',
                                'size': 30,
                                'snapshot_id': 'snap-0282131236002be43',
                                'volume_type': 'gp3',
                                'type': 'volume',
                                'tags': {}},
                            {
                                'active': True,
                                'cloud_account_id': '5c1ed35a-bf6b-4c7d-897a-8388b220fff3',
                                'cloud_account_name': 'AWS linked',
                                'cloud_console_link': 'https://console.aws.amazon.com/ec2/v2/home?region=us-west-1'
                                                      '#Snapshots:snapshotId=snap-03dc9f67588b2f3d0',
                                'cloud_resource_id': 'snap-03dc9f67588b2f3d0',
                                'description': 'Created by CreateImage(i-0c041db9f5b6ccbef) for ami-000060dc272d8ed47 '
                                               'from vol-0a12e44b17a7d0d93',
                                'last_seen': 1617152176,
                                'name': '',
                                'organization_id': '955f3783-ad70-4ad8-9682-b64890ef95c6',
                                'owner_id': '0b2287ea-c543-4b47-a8aa-a2953fad9eb4',
                                'owner_name': 'Tester',
                                'pool_id': '6e4c3ef9-37a9-47ec-87f7-0a864af86016',
                                'pool_name': 'Dalek Industry',
                                'pool_purpose': 'business_unit',
                                'region': 'us-west-1',
                                'resource_id': '009c7c48-94bf-44e7-9000-9801db3a37c3',
                                'size': 30,
                                'state': 'completed',
                                'type': 'snapshot',
                                'volume_id': 'vol-0a12e44b17a7d0d93',
                                'tags': {}},
                            {
                                'active': True,
                                'cloud_account_id': '5c1ed35a-bf6b-4c7d-897a-8388b220fff3',
                                'cloud_account_name': 'AWS linked',
                                'cloud_console_link': 'https://console.aws.amazon.com/ec2/v2/home?region=us-west-1'
                                                      '#Snapshots:snapshotId=snap-012a9084f4db84efe',
                                'cloud_resource_id': 'snap-012a9084f4db84efe',
                                'description': 'Created by CreateImage(i-0c041db9f5b6ccbef) for ami-05a0b94d614da51d8 '
                                               'from vol-0a12e44b17a7d0d93',
                                'name': '',
                                'organization_id': '955f3783-ad70-4ad8-9682-b64890ef95c6',
                                'owner_id': '0b2287ea-c543-4b47-a8aa-a2953fad9eb4',
                                'owner_name': 'Tester',
                                'pool_id': '6e4c3ef9-37a9-47ec-87f7-0a864af86016',
                                'pool_name': 'Dalek Industry',
                                'pool_purpose': 'business_unit',
                                'region': 'us-west-1',
                                'resource_id': 'e68ddee4-7e2a-42ee-a21a-5999e0cc3fee', 'last_seen': 1617152176,
                                'size': 30,
                                'state': 'completed',
                                'type': 'snapshot',
                                'volume_id': 'vol-0a12e44b17a7d0d93',
                                'tags': {}},
                            {
                                'active': True,
                                'cloud_account_id': '5c1ed35a-bf6b-4c7d-897a-8388b220fff3',
                                'cloud_account_name': 'AWS linked',
                                'cloud_console_link': 'https://console.aws.amazon.com/ec2/v2/home?region=us-west-1'
                                                      '#Snapshots:snapshotId=snap-0b060b59614baee12',
                                'cloud_resource_id': 'snap-0b060b59614baee12',
                                'description': 'Created by CreateImage(i-0ffa47c24ddbfaedf) for ami-01c997d55fdff26b8 '
                                               'from vol-0dcec72ac83abcb10',
                                'last_seen': 1617152176,
                                'name': '',
                                'organization_id': '955f3783-ad70-4ad8-9682-b64890ef95c6',
                                'owner_id': '0b2287ea-c543-4b47-a8aa-a2953fad9eb4',
                                'owner_name': 'Tester',
                                'pool_id': '6e4c3ef9-37a9-47ec-87f7-0a864af86016',
                                'pool_name': 'Dalek Industry',
                                'pool_purpose': 'business_unit',
                                'region': 'us-west-1',
                                'resource_id': '9d311563-54c0-4f24-89b6-2bf08b9fcf98',
                                'size': 40,
                                'state': 'completed',
                                'type': 'snapshot',
                                'volume_id': 'vol-0dcec72ac83abcb10',
                                'tags': {}},
                            {
                                'active': True,
                                'cloud_account_id': '5c1ed35a-bf6b-4c7d-897a-8388b220fff3',
                                'cloud_account_name': 'AWS linked',
                                'cloud_console_link': 'https://console.aws.amazon.com/ec2/v2/home?region=us-west-2'
                                                      '#Snapshots:snapshotId=snap-0bb2b0d4627a9ea92',
                                'cloud_resource_id': 'snap-0bb2b0d4627a9ea92',
                                'description': 'Copied for DestinationAmi ami-0896ae01b544f65a8 from SourceAmi '
                                               'ami-000060dc272d8ed47 for SourceSnapshot snap-03dc9f67588b2f3d0. Task '
                                               'created on 1,607,338,338,349.',
                                'last_seen': 1617152176,
                                'name': '',
                                'organization_id': '955f3783-ad70-4ad8-9682-b64890ef95c6',
                                'owner_id': '0b2287ea-c543-4b47-a8aa-a2953fad9eb4',
                                'owner_name': 'Tester',
                                'pool_id': '6e4c3ef9-37a9-47ec-87f7-0a864af86016',
                                'pool_name': 'Dalek Industry',
                                'pool_purpose': 'business_unit',
                                'region': 'us-west-2',
                                'resource_id': '707948fc-571b-4e05-8ac1-3c54d7fe328f',
                                'size': 30,
                                'state': 'completed',
                                'type': 'snapshot',
                                'volume_id': None,
                                'tags': {}},
                            {
                                'active': True,
                                'cloud_account_id': '5c1ed35a-bf6b-4c7d-897a-8388b220fff3',
                                'cloud_account_name': 'AWS linked',
                                'cloud_console_link': 'https://console.aws.amazon.com/ec2/v2/home?region=us-west-2'
                                                      '#Snapshots:snapshotId=snap-0e2213980002234ef',
                                'cloud_resource_id': 'snap-0e2213980002234ef',
                                'description': 'Copied for DestinationAmi ami-09d7e4ccf2c68700d from SourceAmi '
                                               'ami-01c997d55fdff26b8 for SourceSnapshot snap-0b060b59614baee12. Task '
                                               'created on 1,607,325,344,215.',
                                'last_seen': 1617152176,
                                'name': '',
                                'organization_id': '955f3783-ad70-4ad8-9682-b64890ef95c6',
                                'owner_id': '0b2287ea-c543-4b47-a8aa-a2953fad9eb4',
                                'owner_name': 'Tester',
                                'pool_id': '6e4c3ef9-37a9-47ec-87f7-0a864af86016',
                                'pool_name': 'Dalek Industry',
                                'pool_purpose': 'business_unit',
                                'region': 'us-west-2',
                                'resource_id': '87160f24-ef1f-4495-8489-16b668ad39cc',
                                'size': 40,
                                'state': 'completed',
                                'volume_id': None,
                                'type': 'snapshot',
                                'tags': {}},
                            {
                                'active': True,
                                'cloud_account_id': '5c1ed35a-bf6b-4c7d-897a-8388b220fff3',
                                'cloud_account_name': 'AWS linked',
                                'cloud_console_link': 'https://console.aws.amazon.com/ec2/v2/home?region=us-west-2'
                                                      '#Snapshots:snapshotId=snap-0282131236002be43',
                                'cloud_resource_id': 'snap-0282131236002be43',
                                'description': 'Copied for DestinationAmi ami-057935eae1159db28 from SourceAmi '
                                               'ami-05a0b94d614da51d8 for SourceSnapshot snap-012a9084f4db84efe. Task '
                                               'created on 1,607,325,351,739.',
                                'last_seen': 1617152176,
                                'name': '',
                                'organization_id': '955f3783-ad70-4ad8-9682-b64890ef95c6',
                                'owner_id': '0b2287ea-c543-4b47-a8aa-a2953fad9eb4',
                                'owner_name': 'Tester',
                                'pool_id': '6e4c3ef9-37a9-47ec-87f7-0a864af86016',
                                'pool_name': 'Dalek Industry',
                                'pool_purpose': 'business_unit',
                                'region': 'us-west-2',
                                'resource_id': 'bead6bad-b296-4fe4-92de-fc37a89e93b1',
                                'size': 30,
                                'state': 'completed',
                                'type': 'snapshot',
                                'volume_id': None,
                                'tags': {}},
                            {
                                'active': True,
                                'cloud_account_id': 'ba5a7439-df3a-4d41-9244-4927b80770f2',
                                'cloud_account_name': 'AWS',
                                'cloud_console_link': 'https://console.aws.amazon.com/s3/buckets/cf-templates'
                                                      '-nvn8cifbt6g5-eu-north-1?region=eu-north-1&tab=objects',
                                'cloud_resource_id': 'cf-templates-nvn8cifbt6g5-eu-north-1',
                                'last_seen': 1617152439,
                                'name': 'cf-templates-nvn8cifbt6g5-eu-north-1',
                                'organization_id': '955f3783-ad70-4ad8-9682-b64890ef95c6',
                                'owner_id': '0b2287ea-c543-4b47-a8aa-a2953fad9eb4',
                                'owner_name': 'Tester',
                                'pool_id': '6e4c3ef9-37a9-47ec-87f7-0a864af86016',
                                'pool_name': 'Dalek Industry',
                                'pool_purpose': 'business_unit',
                                'region': 'eu-north-1',
                                'resource_id': 'a1b4ef44-1ef2-4123-bb66-f78d48a39ad7',
                                'type': 'bucket',
                                'tags': {}},
                            {
                                'active': True,
                                'cloud_account_id': 'ba5a7439-df3a-4d41-9244-4927b80770f2',
                                'cloud_account_name': 'AWS',
                                'cloud_console_link': 'https://console.aws.amazon.com/s3/buckets/202101060-liberty'
                                                      '-backup?region=eu-central-1&tab=objects',
                                'cloud_resource_id': '202101060-liberty-backup',
                                'last_seen': 1617152439,
                                'name': '202101060-liberty-backup',
                                'organization_id': '955f3783-ad70-4ad8-9682-b64890ef95c6',
                                'owner_id': '0b2287ea-c543-4b47-a8aa-a2953fad9eb4',
                                'owner_name': 'Tester',
                                'pool_id': '6e4c3ef9-37a9-47ec-87f7-0a864af86016',
                                'pool_name': 'Dalek Industry',
                                'pool_purpose': 'business_unit',
                                'region': 'eu-central-1',
                                'resource_id': '949bada8-92ae-4871-8faa-342b95d2f28c',
                                'type': 'bucket',
                                'tags': {
                                    'aws:createdBy': 'IAMUser:AIDAJGWH6JNRGDXONCBLI:va-iam-full'}},
                            {
                                'active': True,
                                'cloud_account_id': 'ba5a7439-df3a-4d41-9244-4927b80770f2',
                                'cloud_account_name': 'AWS',
                                'cloud_console_link': 'https://console.aws.amazon.com/s3/buckets/hystax-eu-west-1'
                                                      '?region=eu-west-1&tab=objects',
                                'cloud_resource_id': 'hystax-eu-west-1',
                                'last_seen': 1617152439,
                                'name': 'hystax-eu-west-1',
                                'organization_id': '955f3783-ad70-4ad8-9682-b64890ef95c6',
                                'owner_id': '0b2287ea-c543-4b47-a8aa-a2953fad9eb4',
                                'owner_name': 'Tester',
                                'pool_id': '6e4c3ef9-37a9-47ec-87f7-0a864af86016',
                                'pool_name': 'Dalek Industry',
                                'pool_purpose': 'business_unit',
                                'region': 'eu-west-1',
                                'resource_id': '0fee4514-7b48-4616-9cd1-1b88cdbf5eef',
                                'type': 'bucket',
                                'tags': {
                                    'aws:createdBy': 'IAMUser:AIDAIPPYCHRYQONGDLRJS:pk-full'}
                            }
                        ]
                    }
                ],
                'organization': {
                    'id': 'c2272558-912f-4571-8dc5-99bd5d30f7d1',
                    'name': 'Dalek Industry',
                    'currency_code': '$'
                },
            }
        }
    },
    'pool_owner_violation_report': {
        'email': ['lori54_lskqtdln@hystax.com'],
        'subject': 'Action required: Hystax OptScale Resource Constraints Report',
        'template_type': 'pool_owner_violation_report',
        'template_params': {
            'texts': {
                'total_differ': 0,
                'total_violated': 2,
                'differ_resources': [],
                'organization': {
                    'id': '28eef4b1-4acf-4050-b833-86c3b2aaf1e7',
                    'name': 'Lori Inc'
                },
                'violated_resources': [
                    {
                        'cloud_resource_id': 'i-05377b0fa5b9674fd',
                        'constraint_limit': 1,
                        'created_at': 1617198128,
                        'deleted_at': 0,
                        'hit_value': 9,
                        'id': '026df797-2d92-45d6-9f8e-6be329e346e0',
                        'organization_id': '28eef4b1-4acf-4050-b833-86c3b2aaf1e7',
                        'owner_id': '25252003-7c90-47df-a942-e8a6caaa58fb',
                        'owner_name': 'tparker',
                        'pool_id': 'eceb67e8-da0e-40ff-b9c6-9f0b23090135',
                        'pool_name': 'AQA_1617196474.73338',
                        'pool_purpose': 'business_unit',
                        'resource_id': '08589dbe-3291-4a8d-8e52-7302933a46ee',
                        'resource_type': 'Instance',
                        'resource_name': 'aqa_eu_instance_for_migration. It is very very very very very very very '
                                         'very very very very very very very very very long name',
                        'time': 1617198128,
                        'type': 'expense_limit'},
                    {
                        'constraint_limit': 1,
                        'created_at': 1617198124,
                        'deleted_at': 0,
                        'hit_value': 733,
                        'id': '650cbb4d-7b87-4153-bd21-ca636168a59f',
                        'organization_id': '28eef4b1-4acf-4050-b833-86c3b2aaf1e7',
                        'owner_id': '25252003-7c90-47df-a942-e8a6caaa58fb',
                        'owner_name': 'tparker',
                        'pool_id': 'eceb67e8-da0e-40ff-b9c6-9f0b23090135',
                        'pool_name': 'AQA_1617196474.73338',
                        'pool_purpose': 'business_unit',
                        'cloud_resource_id': 'i-05377b0fa5b9674fd',
                        'resource_id': '08589dbe-3291-4a8d-8e52-7302933a46ee',
                        'resource_name': 'aqa_eu_instance_for_migration',
                        'resource_type': 'Instance',
                        'time': 1617198124,
                        'type': 'ttl'}]}}},
    'resource_owner_violation_alert': {
        "email": ["kepler71@de.io"],
        "template_type": "resource_owner_violation_alert",
        "subject": "Action required: Hystax OptScale Resource Constraint Violation Alert",
        "template_params": {
            "texts": {
                "total_violated": 2,
                "organization": {
                    "id": "2254d0c7-d341-45cd-a2b4-200f8df8112a",
                    "name": "Renaissance science",
                    "currency_code": "$"
                },
                "violated_resources": [
                    {
                        "cloud_resource_id": "hystax-eu-fra",
                        "employee_id": "99ba5718-c73d-4cf2-84f7-62cc7df6c020",
                        "employee_name": "Iogann Kepler",
                        "hit_value": 1617706815,
                        "pool_id": "3f575a6a-237d-4f4d-a4b4-1f8005451432",
                        "pool_name": "IK_ORG",
                        "resource_name": "hystax-eu-fra. It is very very very very very very very very very very very "
                                         "very very very very very long name",
                        "type": "ttl",
                        "resource_id": "e2b0412d-d3d3-425e-bd1e-e27ac881d58e",
                    },
                    {
                        "cloud_resource_id": "hystax-eu-fra",
                        "employee_id": "99ba5718-c73d-4cf2-84f7-62cc7df6c020",
                        "employee_name": "Iogann Kepler",
                        "hit_value": 20,
                        "pool_id": "3f575a6a-237d-4f4d-a4b4-1f8005451432",
                        "pool_name": "IK_ORG",
                        "resource_name": "hystax-eu-fra",
                        "type": "expense_limit",
                        "resource_id": "2b2dd58e-366d-4138-ad72-756aec545eca",
                    }
                ]
            }
        }
    },
    'resource_owner_violation_report': {
        "email": ["root@hystax.com"],
        "template_type": "resource_owner_violation_report",
        "subject": "Action required: Hystax OptScale Resource Constraints Report",
        "template_params": {
            "texts": {
                "total_differ": 1,
                "total_violated": 1,
                "differ_resources": [{
                    "cloud_resource_id": "hystax-eu-fra",
                    "created_at": 1608790595,
                    "deleted_at": 0,
                    "id": "d48a8c38-19ea-4ae5-9229-c46887508480",
                    "limit": 1,
                    "organization_id": "b8835bce-da4c-4c29-98a0-4b4967baba53",
                    "owner_id": "ecded3e5-d84f-4354-bce2-db2c89755e6c",
                    "owner_name": "Ivan Shashero",
                    "pool_id": "5e3390d7-76ea-4c3b-a00a-b3bbc733a115",
                    "pool_name": "test",
                    "pool_purpose": "pool",
                    "resource_id": "4532cba1-e5cf-4785-a4ee-67c08c5440cf",
                    "resource_name": "hystax-eu-fra. It is very very very very very very very very very very very "
                                     "very very very very very long name",
                    "resource_type": "Bucket",
                    "type": "ttl",
                    "policy": {
                        "active": True,
                        "created_at": 1608790627,
                        "deleted_at": 0,
                        "id": "bba410ce-d23b-4dfd-8331-422270984cdb",
                        "limit": 2,
                        "organization_id": "b8835bce-da4c-4c29-98a0-4b4967baba53",
                        "pool_id": "5e3390d7-76ea-4c3b-a00a-b3bbc733a115",
                        "pool_name": "test",
                        "type": "ttl"
                    },
                }],
                "organization": {
                    "id": "b8835bce-da4c-4c29-98a0-4b4967baba53",
                    "name": "Czar Pictures"
                },
                "violated_resources": [{
                    "cloud_resource_id": "hystax-eu-fra",
                    "constraint_limit": 1,
                    "created_at": 1617025349,
                    "deleted_at": 0,
                    "hit_value": 10903,
                    "id": "cb292ab1-6be8-46f5-8694-f94c0b0a2edf",
                    "organization_id": "b8835bce-da4c-4c29-98a0-4b4967baba53",
                    "owner_id": "ecded3e5-d84f-4354-bce2-db2c89755e6c",
                    "owner_name": "Ivan Shashero",
                    "pool_id": "5e3390d7-76ea-4c3b-a00a-b3bbc733a115",
                    "pool_name": "test",
                    "pool_purpose": "pool",
                    "resource_id": "4532cba1-e5cf-4785-a4ee-67c08c5440cf",
                    "resource_name": "hystax-eu-fra. It is very very very very very very very very very very very "
                                     "very very very very very long name",
                    "resource_type": "Bucket",
                    "time": 1617025349,
                    "type": "ttl"
                }]
            }
        }
    },
    'weekly_expense_report': {
        "email": ["root@hystax.com"],
        "template_type": "weekly_expense_report",
        "subject": "OptScale weekly expense report",
        "template_params": {
            "texts": {
                "organization": {
                    "forecast": 482.32,
                    "id": "ed74eb3b-1c4d-477e-b431-28f697d62233",
                    "limit": 500,
                    "name": "ishorg",
                    "total_cost": 451.21,
                    "currency_code": "$"
                },
                "pools": [
                    {
                        "cost": 0,
                        "forecast": 0.0,
                        "id": "b1d60c69-4e14-4bda-be16-dc8fc6d8b941",
                        "limit": 0,
                        "name": "123. It is very very very very very very very very very very very very very very "
                                "very very long name",
                        "tracked": 0,
                    },
                    {
                        "cost": 6.41,
                        "forecast": 6.85,
                        "id": "f5a563ee-b38e-4fff-8277-41bf32b8725c",
                        "limit": 5,
                        "name": "trash",
                        "tracked": 15
                    },
                    {
                        "limit": 500,
                        "cost": 49.27,
                        "forecast": 52.67,
                        "id": "a575532e-3abb-4d5b-b4d1-c3c65c5166ed",
                        "name": "ishorg",
                        "tracked": 106
                    },
                    {
                        "cost": 91.67,
                        "forecast": 97.99,
                        "id": "5e3390d7-76ea-4c3b-a00a-b3bbc733a115",
                        "limit": 100,
                        "name": "test",
                        "tracked": 1
                    },
                    {
                        "cost": 93.56,
                        "forecast": 122222312300.01,
                        "id": "278c5876-43bb-4f33-9dff-55ae518d65db",
                        "limit": 50,
                        "name": "testo",
                        "tracked": 2
                    }
                ],
                "unassigned": {
                    "forecast": 224.81,
                    "total_cost": 210.3,
                    "resources_tracked": 540
                }
            }
        }
    },
    'bumi_task_execution_failed': {
        'email': 'test_user@service.com',
        'subject': '[127.0.0.1] Bumi task execution failed',
        'template_type': 'bumi_task_execution_failed',
        'template_params': {
            'texts': {
                'organization': {
                    'id': '6946211f-47ff-43a3-a9a3-3e5f57d52415',
                    'name': 'Czar Pictures'
                },
                "reason": "Timeout error while process task 1639638582 (organization_id b74f3ca6-c392-4bcb-96b3-2ffaa0281810)",
                'failed_modules': [{
                    'module': 'instance_migration',
                    'error': 'Timeout error while process task 1639638582 '
                             '(organization_id b74f3ca6-c392-4bcb-96b3-2ffaa0281810, '
                             'module instance_migration, try 0) step Process'
                }]
            }}},
    'bumi_module_execution_failed': {
        'email': 'test_user@service.com',
        'subject': '[127.0.0.1] Recommendation module failed',
        'template_type': 'bumi_module_execution_failed',
        'template_params': {
            'texts': {
                'organization': {
                    'id': 'b8835bce-da4c-4c29-98a0-4b4967baba53',
                    'name': 'Czar Pictures'
                },
                'failed_modules': [{
                    'module': 'short_living_instances',
                    'error': "name 'LOG' is not defined"}]
            }}},
    'first_shareable_resources': {
        "email": ["azaza@ma.il"],
        "subject": "OptScale shareable environments notification",
        "template_type": "first_shareable_resources",
        "template_params": {
            "texts": {
                "organization": {
                    "id": "5d3d4501-0de8-40dc-a9ed-df2fb1396141",
                    "name": "am2"
                }
            },
        }
    },
    'report_import_failed': {
        'email': ['azaza@ma.il'],
        'subject': '[1.2.3.4] Report import failed',
        'template_type': 'report_import_failed',
        'template_params': {
            "texts": {
                'organization': {
                    'id': '5d3d4501-0de8-40dc-a9ed-df2fb1396141',
                    'name': 'am2'
                },
                'cloud_account': {
                    'id': '8aa14efd-d111-4934-9c19-92b6f0da18fe',
                    'name': 'Ali',
                    'type': 'alibaba_cnr',
                    'last_import_at': '09/03/2021 10:37:57 UTC'
                },
                'reason': 'Because'
            },
        }
    },
    'environment_changes': {
        "email": ["azaza@ma.il"],
        "subject": "Environment changed",
        "template_type": "environment_changes",
        "template_params": {
            "texts": {
                "organization": {
                    "name": "AS_Test_ORG",
                    "id": "7e23e036-87b9-460f-aa3e-10f2a5b63f54",
                    "currency_code": "$"
                },
                "user": {
                    "user_display_name": "ASBalmah_Engineer"
                },
                "environment_status_changed": {
                    "changed_environment": {
                        "name": "Test_Environment",
                        "id": "5dba5d14-d385-4b29-a426-b37160d1adbf",
                        "status": "released"
                    }
                },
                "environment_prop_changed": {
                    "changed_environment": {
                        "property_info": [
                            {
                                "name": "Purpose",
                                "previous_value": "Staging",
                                "new_value": "Production"
                            },
                            {
                                "name": "Purpose2",
                                "previous_value": "Staging2",
                                "new_value": "Production2"
                            }
                        ],
                        "name": "Test_Environment",
                        "id": "5dba5d14-d385-4b29-a426-b37160d1adbf",
                    }
                },
                "environments_infos": {
                    "cloud_resource_id": "environment_f09696910bdd874a99cd74c8f05b5c44",
                    "resource_name": "Test_Environment",
                    "cloud_account_id": "07b66570-ad21-4cae-93f7-b079b548daae",
                    "cloud_account_name": "Environment",
                    "type": "Test_Type",
                    "resource_id": "5dba5d14-d385-4b29-a426-b37160d1adbf",
                    "pool": "Environment",
                    "resource_type": "environment",
                    "jira_tickets": [
                        {
                            "url": "https://jira.com.example/NGUI-1242",
                            "name": "NGUI-1242"
                        }, 
                        {
                            "url": "https://jira.com.example/NGUI-3214",
                            "name": "NGUI-3214"
                        }
                    ],
                    "software": "software_example",
                    "status": {
                        "Status": "IN USE",
                        "details": {
                            "User": "John Doe",
                            "Since": "2024-08-01 06:44:49 UTC",
                            "Until": "2024-08-01 10:00:00 UTC",
                            "Remained": "3 hours"
                        }
                    },
                    "upcoming_bookings": [
                        {
                            "details": {
                                "User": "John Doe",
                                "Since": "2024-08-02 07:00:00 UTC",
                                "Until": "2024-08-04 07:00:00 UTC",
                                "Duration": "48 hours"
                            },
                            "status_info": {
                                "Status": "<upcoming booking status>"
                            }
                        }
                    ],
                    "contains_envs": True,
                    "env_properties": [
                        {
                            "env_key": "Purpose",
                            "env_value": "Production"
                        },
                        {
                            "env_key": "Software version",
                            "env_value": "v1.2.32141"
                        }

                    ]
                },
                "environment_state_changed": {
                    "changed_environment": {
                        "name": "Test_Environment",
                        "id": "5dba5d14-d385-4b29-a426-b37160d1adbf",
                        "previous_value": "Active",
                        "new_value": "Not Active",
                    }
                },
                "name": "John Doe",
            },
        }
    },
    'anomaly_detection_alert': {
        'email': ['james31_pza@hystax.com'],
        'subject': 'Anomaly detected',
        'template_type': 'anomaly_detection_alert',
        'template_params': {
            'texts': {
                'title': 'Anomaly detection Alert',
                'organization': {
                    'id': '6946211f-47ff-43a3-a9a3-3e5f57d52415',
                    'name': 'AQA_1617018508.3637385',
                    'currency_code': '$'
                },
                'organization_constraint': {
                    'name': 'Anomaly#1',
                    'resource_count_anomaly': False,
                    'expense_anomaly': True,
                    'resource_quota': False,
                    'recurring_budget': False,
                    'expiring_budget': False,
                    'tagging_policy': False,
                    'id': 'c063973e-0bb2-4134-9ebe-2e68104d7aa8',
                    'definition': {
                        'threshold_days': 7,
                        'threshold': 30,
                    }
                },
                'filters': [{
                    'filter_name': 'pool',
                    'filter_values': 'Pool1(b1d60c69-4e14-4bda-be16-dc8fc6d8b941)'
                }],
                'limit_hit': {
                    'created_at': '02/21/2022',
                    'value': 43,
                    'link': 'https://20.52.178.55/restapi/v2/resources?'
                            'start_date=1643673600&end_date=1645142399&'
                            'breakdownBy=expenses&'
                            'poolId=b1d60c69-4e14-4bda-be16-dc8fc6d8b941',
                    'constraint_limit': 22
                },
                'user': {
                    'assignment_id': 'f3b2a722-9674-4042-a08a-81f41b926647',
                    'assignment_resource_id': '943cb6e0-2cbe-4974-a937-2c480aa9934f',
                    'assignment_type_id': 2,
                    'role_id': 3,
                    'role_name': 'Manager',
                    'role_purpose': 'optscale_manager',
                    'role_scope_id': None,
                    'user_display_name': 'james31',
                    'user_email': 'james31_pza@hystax.com',
                    'user_id': '4a50413a-9703-4586-ab39-96aa289e979e'}}}},
    'new_security_recommendation': {
        'email': 'test_user@service.com',
        'subject': 'New security recommendation detected',
        'template_type': 'new_security_recommendation',
        'template_params': {
            'texts': {
                'title': 'New security recommendation detected',
                'organization': {
                    'id': 'b8835bce-da4c-4c29-98a0-4b4967baba53',
                    'name': 'Czar Pictures',
                    'currency_code': '$'
                },
                'modules': [
                    {'module': 'Public Amazon S3 buckets',
                     'count': 1},
                    {'module': 'Instances with insecure Security Groups settings',
                     'count': 2},
                    {'module': 'Inactive IAM users',
                     'count': 3},
                    {'module': 'IAM users with unused console access',
                     'count': 4}
                ],
                'user': {
                    'user_display_name': 'james31'},
            }}},
    'saving_spike': {
        'email': ['james31_pza@hystax.com'],
        'subject': 'Saving spike',
        'template_type': 'saving_spike',
        'template_params': {
            'texts': {
                'title': 'Saving spike',
                'organization': {
                    'id': '6946211f-47ff-43a3-a9a3-3e5f57d52415',
                    'name': 'AQA_1617018508.3637385',
                    'currency_code': '$'
                },
                'previous_total': 121.21,
                'current_total': 145.45,
                'recommendations': [
                    {
                        'count': 3,
                        'module': 'Abandoned Instances',
                        'saving': 123,
                    },
                    {
                        'count': 5,
                        'module': 'Not attached Volumes',
                        'saving': 22,
                    },
                    {
                        'count': 1,
                        'module': 'Underutilized Instances',
                        'saving': 0.45,
                    }],
                'user': {
                    'user_display_name': 'james31'}}}},
    'organization_policy_quota': {
        'email': ['james31_pza@hystax.com'],
        'subject': 'Organization policy violated',
        'template_type': 'organization_policy_quota',
        'template_params': {
            'texts': {
                'title': 'Organization policy violated',
                'organization': {
                    'id': '6946211f-47ff-43a3-a9a3-3e5f57d52415',
                    'name': 'AQA_1617018508.3637385',
                    'currency_code': '$'
                },
                'organization_constraint': {
                    'name': 'Resources quota in eu-central-1',
                    'expiring_budget': False,
                    'resource_count_anomaly': False,
                    'expense_anomaly': False,
                    'resource_quota': True,
                    'recurring_budget': False,
                    'tagging_policy': False,
                    'id': 'c063973e-0bb2-4134-9ebe-2e68104d7aa8',
                    'definition': {
                        'max_value': 7,
                    }
                },
                'filters': [{
                    'filter_name': 'pool',
                    'filter_values': 'Pool1(b1d60c69-4e14-4bda-be16-dc8fc6d8b941)'
                }],
                'limit_hit': {
                    'created_at': '02/21/2022 11:45 AM UTC',
                    'value': 22,
                    'link': 'https://20.52.178.55/resources?'
                            'breakdownBy=resourceType&region=eu-central-1&'
                            'startDate=1645401600&endDate=1645487999&'
                            'poolId=b1d60c69-4e14-4bda-be16-dc8fc6d8b941',
                    'constraint_limit': 7
                },
                'user': {
                    'user_display_name': 'james31',
                }}}},
    'organization_policy_recurring_budget': {
        'email': ['james31_pza@hystax.com'],
        'subject': 'Organization policy violated',
        'template_type': 'organization_policy_recurring_budget',
        'template_params': {
            'texts': {
                'title': 'Organization policy violated',
                'organization': {
                    'id': '6946211f-47ff-43a3-a9a3-3e5f57d52415',
                    'name': 'AQA_1617018508.3637385',
                    'currency_code': '$'
                },
                'organization_constraint': {
                    'name': 'Monthly limit in eu-central-1',
                    'expiring_budget': False,
                    'resource_count_anomaly': False,
                    'expense_anomaly': False,
                    'resource_quota': False,
                    'recurring_budget': True,
                    'tagging_policy': False,
                    'id': 'c063973e-0bb2-4134-9ebe-2e68104d7aa8',
                    'definition': {
                        'monthly_budget': 1000,
                    }
                },
                'filters': [{
                    'filter_name': 'pool',
                    'filter_values': 'Pool1(b1d60c69-4e14-4bda-be16-dc8fc6d8b941)'
                }],
                'limit_hit': {
                    'created_at': '02/21/2022 11:45 AM UTC',
                    'value': 1557.57,
                    'link': 'https://20.52.178.55/resources?'
                            'breakdownBy=expenses&region=eu-central-1&'
                            'startDate=1645443900&endDate=1646092800&'
                            'poolId=b1d60c69-4e14-4bda-be16-dc8fc6d8b941',
                    'constraint_limit': 1000
                },
                'user': {
                    'user_display_name': 'james31',
                }}}},
    'organization_policy_expiring_budget': {
        'email': ['james31_pza@hystax.com'],
        'subject': 'Organization policy violated',
        'template_type': 'organization_policy_expiring_budget',
        'template_params': {
            'texts': {
                'title': 'Organization policy violated',
                'organization': {
                    'id': '6946211f-47ff-43a3-a9a3-3e5f57d52415',
                    'name': 'AQA_1617018508.3637385',
                    'currency_code': '$'
                },
                'organization_constraint': {
                    'name': 'Expenses limit in eu-central-1',
                    'expiring_budget': True,
                    'resource_count_anomaly': False,
                    'expense_anomaly': False,
                    'resource_quota': False,
                    'recurring_budget': False,
                    'tagging_policy': False,
                    'id': 'c063973e-0bb2-4134-9ebe-2e68104d7aa8',
                    'definition': {
                        'total_budget': 1000,
                        'start_date': 1645443900
                    }
                },
                'filters': [{
                    'filter_name': 'pool',
                    'filter_values': 'Pool1(b1d60c69-4e14-4bda-be16-dc8fc6d8b941)'
                }],
                'limit_hit': {
                    'created_at': '02/21/2022 11:45 AM UTC',
                    'value': 1557.57,
                    'link': 'https://20.52.178.55/resources?breakdownBy=expenses&'
                            'region=eu-central-1&startDate=1645443900'
                            'poolId=b1d60c69-4e14-4bda-be16-dc8fc6d8b941',
                    'constraint_limit': 1000
                },
                'user': {
                    'user_display_name': 'james31',
                }}}},
    'organization_policy_tagging': {
        'email': ['james31_pza@hystax.com'],
        'subject': 'Organization policy violated',
        'template_type': 'organization_policy_tagging',
        'template_params': {
            'texts': {
                'organization': {
                    'id': '6946211f-47ff-43a3-a9a3-3e5f57d52415',
                    'name': 'AQA_1617018508.3637385',
                    'currency_code': '$'
                },
                'organization_constraint': {
                    'name': 'CI/CD resources',
                    'type': 'Tagging policy',
                    'id': 'c063973e-0bb2-4134-9ebe-2e68104d7aa8',
                    'definition': {
                        'start_date': '02/21/2022 11:45 AM UTC',
                        'conditions': {'tag': 'CI/CD', 'without_tag': 'owner'}
                    }
                },
                'conditions': 'with tag "CI/CD", without tag "owner"',
                'limit_hit': {
                    'created_at': '02/21/2022 11:45 AM UTC',
                    'value': 22,
                    'link': 'https://20.52.178.55/resources?'
                            'breakdownBy=resourceType&region=eu-central-1&'
                            'startDate=1645401600&endDate=1645487999&'
                            'poolId=b1d60c69-4e14-4bda-be16-dc8fc6d8b941',
                    'constraint_limit': 0
                }}}},
    'report_imports_passed_for_org': {
        'email': ['james31_pza@hystax.com'],
        'subject': 'Expenses initial processing completed',
        'template_type': 'report_imports_passed_for_org',
        'template_params': {
            'texts': {
                'organization': {
                    'id': '6946211f-47ff-43a3-a9a3-3e5f57d52415',
                    'name': 'AQA_1617018508.3637385',
                    'currency_code': '$'
                }
            }
        }
    },
    'insider_prices_sslerror': {
        "email": ["optscale-staging-notifications@hystax.com"],
        "subject": "[172.22.20.6] Insider faced Azure SSLError",
        'template_type': 'insider_prices_sslerror',
        'template_params': {
            'texts': {
                'title': 'Insider faced Azure SSLError',
                }}},
    'incorrect_alibaba_expenses': {
        "email": ["optscale-staging-notifications@hystax.com"],
        "subject": "[172.22.20.6] Incorrect expenses for Alibaba data source",
        'template_type': 'incorrect_alibaba_expenses',
        'template_params': {
            'texts': {
                'clean_expenses': 18256.11,
                'cloud_expenses': 17822.97,
                'period': '2022-11-11 - 2022-11-17',
                'organization': {
                    'id': '6946211f-47ff-43a3-a9a3-3e5f57d52415',
                    'name': 'AQA_1617018508.3637385',
                },
                'cloud_account': {
                    'id': 'c063973e-0bb2-4134-9ebe-2e68104d7aa8',
                    'name': 'Test_data_source',
                }}}},
    'disconnect_survey': {
        'email': ['andersonmatthew_hwp@hystax.com'],
        'subject': 'Disconnect Survey [d7092814-2b12-4e60-89c5-67919c9b17d6, Funny company]',
        'template_type': 'disconnect_survey',
        'template_params': {
            'texts': {
                'user': 'Eliot Alderson',
                'email': 'ealderson@fsociety.com',
                'data': [{
                    'k': 'key1',
                    'v': 'value1',
                }, {
                    'k': 'key2',
                    'v': 'value2',
                }],
                'organization': {
                    'id': 'd7092814-2b12-4e60-89c5-67919c9b17d6',
                    'name': 'Funny company',
                }}}},
    'restore_password': {
        'email': ['serviceuser@hystax.com'],
        'subject': 'Optscale password recovery',
        'template_type': 'restore_password',
        'template_params': {
            'texts': {
                'code': 263308
            },
            'links': {
                'restore_button': 'https://172.22.20.8/password-recovery'
                                  '?email=serviceuser%40hystax.com&code=263308'
            }
        }
    }
}

REGEX_EMAIL = '^[a-z0-9!#$%&\'*+/=?`{|}~\^\-\+_()]+(\.[a-z0-9!#$%&\'*+/=' \
              '?`{|}~\^\-\+_()]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,18})$'

LOG = logging.getLogger(__name__)


def set_args(arguments):
    def check_email(checked):
        return re.search(REGEX_EMAIL, checked)

    def check_uuid(checked):
        try:
            return str(UUID(checked, version=4)) == checked
        except ValueError:
            return False

    temp_emails = [] if not os.environ.get('TARGET_EMAILS') else os.environ.get('TARGET_EMAILS').split(' ')
    temp_secret = os.environ.get('CLUSTER_SECRET')
    temp_host = os.environ.get('CLUSTER_HOST')
    temp_templates = list(PARAMETER_DUMPS) if not os.environ.get('TEMPLATES') else os.environ.get('TEMPLATES').split(' ')
    params = {
        'emails': temp_emails,
        'secret': temp_secret,
        'host': temp_host,
        'templates': temp_templates
    }
    find_error = False
    if arguments.emails:
        params['emails'] = arguments.emails
    if arguments.secret:
        params['secret'] = arguments.secret
    if arguments.host:
        params['host'] = arguments.host
    if arguments.templates:
        params['templates'] = arguments.templates
    for k, v in params.items():
        if not v:
            LOG.error("%s not specified" % k)
            find_error = True
    bad_emails = []
    for email in params['emails']:
        if not check_email(email):
            bad_emails.append(email)
    if bad_emails:
        LOG.error('Invalid email specified: %s' % ', '.join(bad_emails))
        find_error = True
    if not check_uuid(params['secret']):
        LOG.error('Invalid secret specified')
        find_error = True
    bad_templates = []
    for template in params['templates']:
        if template not in list(PARAMETER_DUMPS):
            bad_templates.append(template)
    if bad_templates:
        LOG.error('Invalid template specified: %s' % ', '.join(bad_templates))
        find_error = True
    return params, find_error


def check_templates():
    excluded_templates = ['default']
    templates_path = './modules/email_generator/templates'
    if os.path.exists(templates_path):
        ready_templates = PARAMETER_DUMPS.keys()
        existing_templates = []
        files = [f for f in os.listdir(templates_path) if isfile(join(templates_path, f))]
        for file in files:
            filename, file_extension = os.path.splitext(file)
            if file_extension != '.html':
                continue
            if filename in excluded_templates:
                continue
            existing_templates.append(filename)
        non_ready_templates = list(set(existing_templates) - set(ready_templates))
        if non_ready_templates:
            LOG.warning('WARNING! Found templates that are not included in the'
                        ' script! Please add the following templates to the '
                        'script: %s!' % ', '.join(non_ready_templates))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-e', '--email', nargs='*', dest='emails',
                        help='Target email (it is possible to specify several times)')
    parser.add_argument('-s', '--secret', help='Cluster secret')
    parser.add_argument('--host', help='Cluster IP')
    parser.add_argument('-t', '--template', nargs='*', dest='templates',
                        help='Target template (it is possible to specify several times)')
    args = parser.parse_args()
    params, bad_args = set_args(args)
    if bad_args:
        sys.exit(1)
    logging.basicConfig(level=logging.INFO)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    for template_type in sorted(params['templates']):
        LOG.info('Sending {} email'.format(template_type))
        data = PARAMETER_DUMPS.get(template_type).copy()
        if template_type == 'weekly_expense_report':
            data['template_params']['texts']['pools'] = sorted(
                data['template_params']['texts']['pools'],
                key=itemgetter('cost'), reverse=True)
        data['email'] = params['emails']
        requests.post(
            url='https://{}/herald/v2/email'.format(params['host']),
            headers={'Secret': params['secret']},
            verify=False,
            json=data,
        )

    if sorted(params['templates']) == sorted(PARAMETER_DUMPS.keys()):
        check_templates()
    LOG.info('Done')
