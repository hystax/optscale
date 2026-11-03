import time
import unittest
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import patch

from tools.cloud_adapter.exceptions import InvalidParameterException
from tools.cloud_adapter.clouds import focus
from tools.cloud_adapter.clouds.focus import (
    RowNormalizer, RowParseError, compile_user_regex, detect_format,
    effective_mapping, parse_datetime, parse_number, parse_tags,
    validate_endpoint, validate_mapping)

AZURE_COLUMNS = [
    'BilledCost', 'EffectiveCost', 'BillingCurrency', 'ChargeCategory',
    'ChargePeriodStart', 'ChargePeriodEnd', 'CommitmentDiscountId',
    'CommitmentDiscountType', 'InvoiceId', 'RegionId', 'ResourceId',
    'ResourceName', 'ServiceName', 'SkuId', 'Tags', 'x_ResourceGroupName',
    'x_ResourceType']
OCI_COLUMNS = [
    'BilledCost', 'BillingCurrency', 'ChargeCategory', 'ChargePeriodStart',
    'ChargePeriodEnd', 'ChargeSubcategory', 'Region', 'ResourceId',
    'ResourceType', 'ServiceName', 'SkuId', 'Tags', 'UsageQuantity']


class TestFormats(unittest.TestCase):
    def test_detect(self):
        self.assertEqual(detect_format(AZURE_COLUMNS), focus.AZURE_1_2)
        self.assertEqual(detect_format(
            ['x_ResourceGroupName', 'x_InvoiceId']), focus.AZURE_1_0)
        self.assertEqual(detect_format(['x_ServiceCode', 'InvoiceId']),
                         focus.AWS_1_2)
        self.assertEqual(detect_format(OCI_COLUMNS), focus.OCI)
        # FOCUS 1.0+ reports of OCI have RegionId and oci_ columns
        self.assertEqual(detect_format(
            ['BilledCost', 'RegionId', 'RegionName', 'oci_CompartmentId']),
            focus.OCI)
        self.assertEqual(detect_format(['InvoiceId', 'RegionId']),
                         focus.GENERIC_1_2)
        self.assertEqual(detect_format(['RegionId', 'ChargeClass']),
                         focus.GENERIC_1_0)
        self.assertEqual(detect_format(['Foo']), focus.UNKNOWN)

    def test_defaults_are_valid(self):
        for fmt in (focus.AWS_1_2, focus.AZURE_1_2, focus.AZURE_1_0,
                    focus.OCI, focus.GENERIC_1_2, focus.GENERIC_1_0,
                    focus.UNKNOWN):
            validate_mapping(focus.default_mapping(fmt))

    def test_user_field_replaces_default(self):
        mapping = effective_mapping(focus.AZURE_1_2, {
            'resource_id': {'columns': ['ResourceId']}})
        self.assertEqual(mapping['resource_id'], {'columns': ['ResourceId']})
        self.assertEqual(mapping['cost'], {'columns': ['BilledCost'],
                                           'decimal_separator': '.'})

    def test_default_fallback(self):
        mapping = effective_mapping(focus.AZURE_1_2, {
            'resource_id': {'template': '{x_Project}/{ResourceName}',
                            'fallback': {'default': True}},
            'resource_type': {
                'rules': [{'column': 'x_Kind', 'match': '^db$',
                           'type': 'Database'}],
                'columns': ['x_Kind'], 'fallback': {'default': True}},
            'cost': {'columns': ['x_Cost'], 'decimal_separator': ',',
                     'fallback': {'default': True}},
        })
        resource_id = mapping['resource_id']
        # the user source, then the source chain of the Azure default
        self.assertEqual(resource_id['template'], '{x_Project}/{ResourceName}')
        self.assertEqual(resource_id['fallback']['columns'],
                         ['ResourceId', 'CommitmentDiscountId'])
        self.assertTrue(resource_id['fallback'][focus.FROM_DEFAULT])
        self.assertEqual(resource_id['fallback']['fallback']['template'],
                         '{ServiceName}/{SkuId}')
        # parameters not set by the user come from the default
        self.assertEqual(resource_id['normalize'], ['strip', 'lower'])
        self.assertEqual(mapping['cost']['decimal_separator'], ',')
        # default resource type rules go after the user ones
        types = [r['type'] for r in mapping['resource_type']['rules']]
        self.assertEqual(types[0], 'Database')
        self.assertIn('Instance', types[1:])
        validate_mapping({'cost': {'columns': ['x_Cost'],
                                   'fallback': {'default': True}}})


class TestValidateMapping(unittest.TestCase):
    def assertInvalid(self, mapping, text):
        with self.assertRaises(InvalidParameterException) as ctx:
            validate_mapping(mapping)
        self.assertIn(text, str(ctx.exception))

    def test_valid(self):
        validate_mapping({
            'cost': {'columns': ['EffectiveCost'], 'decimal_separator': ','},
            'region': {'columns': ['x_SkuRegion'],
                       'fallback': {'value': 'global'}},
            'resource_id': {'template': '{SubAccountId}/{ResourceId}',
                            'normalize': ['strip', 'lower']},
            'resource_type': {'rules': [
                {'column': 'x_ResourceType', 'match': '(?i)disk',
                 'type': 'Volume'}], 'columns': ['ServiceName']},
            'tags': {'mode': 'prefixed_columns', 'prefix': 'tag.'},
        })

    def test_invalid(self):
        self.assertInvalid({'cost': {'column': 'A'}}, 'unexpected keys')
        self.assertInvalid({'foo': {'columns': ['A']}}, 'unknown field')
        self.assertInvalid({'cost': {'columns': ['A'], 'value': 1}},
                           'exactly one')
        self.assertInvalid({'cost': {'columns': []}}, 'non-empty list')
        self.assertInvalid({'name': {'template': 'no placeholder'}},
                           'placeholder')
        self.assertInvalid({'cost': {'columns': ['A'],
                                     'decimal_separator': ';'}},
                           'decimal_separator')
        self.assertInvalid({'resource_id': {'columns': ['A'],
                                            'normalize': ['upper']}},
                           'normalize')
        self.assertInvalid({'resource_type': {'rules': [
            {'column': 'A', 'match': '(', 'type': 'X'}],
            'columns': ['B']}}, 'invalid regex')
        self.assertInvalid({'tags': {'mode': 'prefixed_columns'}}, 'prefix')
        self.assertInvalid({'tags': {'columns': ['Tags'], 'prefix': 'x'}},
                           'prefix')
        self.assertInvalid({'region': {'value': True}}, 'string or a number')
        self.assertInvalid({'region': {'columns': ['A'], 'fallback': {
            'value': 'x', 'normalize': ['lower']}}}, 'unexpected keys')

    def test_invalid_default(self):
        self.assertInvalid({'cost': {'default': True}}, 'unexpected keys')
        self.assertInvalid({'cost': {'columns': ['A'], 'fallback': {
            'default': False}}}, '"default" must be true')
        self.assertInvalid({'cost': {'columns': ['A'], 'fallback': {
            'default': True, 'fallback': {'columns': ['B']}}}},
            '"default" must be true and the last')
        self.assertInvalid({'tags': {'columns': ['T'], 'mode': 'list',
                                     'fallback': {'default': True}}},
                           'json mode')


class TestParsing(unittest.TestCase):
    def test_dates(self):
        expected = datetime(2024, 5, 14)
        for value in ['2024-05-14T00:00:00Z', '2024-05-14T00:00Z',
                      '2024-05-14 00:00:00', '2024-05-14',
                      '2024-05-14T03:00:00+03:00', '1715644800',
                      '1715644800000', 1715644800000,
                      datetime(2024, 5, 14, tzinfo=timezone.utc),
                      '2024-05-14 00:00:00 UTC', '2024-05-14 00:00:00 gmt',
                      '2024-05-14T00:00:00.0000000Z',
                      '2024-05-14 00:00:00+00', '20240514']:
            self.assertEqual(parse_datetime(value), expected, value)
        for value in ['03/04/2025', '1234567', 20240514,
                      '2024-05-14T00:00:00+03:00 UTC']:
            with self.assertRaises(ValueError, msg=value):
                parse_datetime(value)

    def test_numbers(self):
        self.assertEqual(parse_number('1.5'), 1.5)
        self.assertEqual(parse_number('1.2E-05'), 1.2e-05)
        self.assertEqual(parse_number('-3'), -3.0)
        self.assertEqual(parse_number(Decimal('2.25')), 2.25)
        self.assertEqual(parse_number('1234,56', ','), 1234.56)
        self.assertEqual(parse_number(''), 0.0)
        for bad in ['1,234.56', 'abc', '1.2.3']:
            with self.assertRaises(ValueError):
                parse_number(bad)
        with self.assertRaises(ValueError):
            parse_number('1.234,56', ',')

    def test_tags(self):
        self.assertEqual(parse_tags('{"env": "prod", "n": {"a": 1}}', 'json'),
                         {'env': 'prod', 'n.a': '1'})
        self.assertEqual(parse_tags([('env', 'prod')], 'json'),
                         {'env': 'prod'})
        self.assertEqual(parse_tags('["env:prod", "team=core"]', 'list'),
                         {'env': 'prod', 'team': 'core'})
        self.assertEqual(parse_tags([{'key': 'env', 'value': 'prod'}],
                                    'list'), {'env': 'prod'})
        self.assertEqual(parse_tags('', 'json'), {})


class TestRowNormalizer(unittest.TestCase):
    def _azure_row(self, **kwargs):
        row = {
            'BilledCost': '1.5', 'EffectiveCost': '1.2',
            'BillingCurrency': 'USD', 'ChargeCategory': 'Usage',
            'ChargePeriodStart': '2024-05-14T00:00:00Z',
            'ChargePeriodEnd': '2024-05-15T00:00:00Z',
            'CommitmentDiscountId': '', 'CommitmentDiscountType': '',
            'RegionId': 'westeurope',
            'ResourceId': '/subscriptions/ABC/resourceGroups/RG/vm1',
            'ResourceName': 'vm1', 'ServiceName': 'Virtual Machines',
            'SkuId': 'D2', 'Tags': '{"env": "prod"}',
            'x_ResourceType': 'microsoft.compute/virtualMachines',
        }
        row.update(kwargs)
        return row

    def _normalizer(self, columns=None, user_mapping=None):
        columns = columns or AZURE_COLUMNS
        mapping = effective_mapping(detect_format(columns), user_mapping)
        return RowNormalizer(mapping, columns)

    def test_cost_in_billing_currency(self):
        normalizer = self._normalizer(
            AZURE_COLUMNS + ['x_BilledCostInUsd'],
            {'cost': {'columns': ['x_BilledCostInUsd'],
                      'fallback': {'columns': ['BilledCost']}}})
        # decided by the column the cost of each row is taken from
        normalizer.normalize(self._azure_row(x_BilledCostInUsd='2'))
        self.assertFalse(normalizer.cost_in_billing_currency)
        normalizer.normalize(self._azure_row(x_BilledCostInUsd=''))
        self.assertTrue(normalizer.cost_in_billing_currency)
        normalizer = self._normalizer(user_mapping={'cost': {'value': 0}})
        normalizer.normalize(self._azure_row())
        self.assertFalse(normalizer.cost_in_billing_currency)

    def test_default_fallback_rows_are_counted(self):
        user_mapping = {'resource_id': {
            'template': '{x_Project}/{ResourceName}',
            'fallback': {'default': True}}}
        normalizer = self._normalizer(AZURE_COLUMNS + ['x_Project'],
                                      user_mapping)
        ids = [normalizer.normalize(self._azure_row(x_Project=p))[
            'resource_id'] for p in ('alpha', '')]
        self.assertEqual(ids, ['alpha/vm1',
                               '/subscriptions/abc/resourcegroups/rg/vm1'])
        self.assertIn('resource_id: 1 rows took the default mapping',
                      normalizer.collect_warnings())
        # mapped columns missing in the file are reported
        normalizer = self._normalizer(user_mapping=user_mapping)
        self.assertIn('resource_id: none of the mapped columns found in '
                      'file; default mapping is used for all rows',
                      normalizer.warnings)

    def test_azure_defaults(self):
        result = self._normalizer().normalize(self._azure_row())
        self.assertEqual(result, {
            'cost': 1.5,
            'start_date': datetime(2024, 5, 14),
            'end_date': datetime(2024, 5, 15),
            'resource_id': '/subscriptions/abc/resourcegroups/rg/vm1',
            'resource_type': 'Instance',
            'name': 'vm1',
            'region': 'westeurope',
            'service_name': 'Virtual Machines',
            'tags': {'env': 'prod'},
        })

    def test_cost_column(self):
        normalizer = self._normalizer(user_mapping={
            'cost': {'columns': ['EffectiveCost']}})
        self.assertEqual(normalizer.normalize(self._azure_row())['cost'], 1.2)

    def test_identity_chain(self):
        normalizer = self._normalizer()
        commitment = normalizer.normalize(self._azure_row(
            ResourceId='', CommitmentDiscountId='/RI/1',
            CommitmentDiscountType='Reservation'))
        self.assertEqual(commitment['resource_id'], '/ri/1')
        self.assertEqual(commitment['resource_type'], 'Reservation')
        tax = normalizer.normalize(self._azure_row(
            ResourceId='', ServiceName='Tax', SkuId='',
            ChargeCategory='Tax', x_ResourceType=''))
        self.assertEqual(tax['resource_id'], 'tax/tax')
        self.assertEqual(tax['resource_type'], 'Tax')
        support = normalizer.normalize(self._azure_row(
            ResourceId='', ServiceName='Support', SkuId='S1',
            x_ResourceType=''))
        self.assertEqual(support['resource_id'], 'support/s1')

    def test_rows_without_service(self):
        # marketplace purchases and credits may have no service or SKU
        normalizer = self._normalizer()
        purchase = normalizer.normalize(self._azure_row(
            ChargeCategory='Purchase', ServiceName='', SkuId='',
            x_ResourceType=''))
        self.assertEqual(purchase['resource_id'],
                         '/subscriptions/abc/resourcegroups/rg/vm1')
        self.assertEqual(purchase['resource_type'], 'Purchase')
        credit = normalizer.normalize(self._azure_row(
            ChargeCategory='Credit', ResourceId='', ServiceName='',
            SkuId='', x_ResourceType=''))
        self.assertEqual(credit['resource_id'], 'credit')
        self.assertEqual(credit['resource_type'], 'Credit')

    def test_null_strings_are_empty(self):
        # CSV exported from SQL engines
        normalizer = self._normalizer()
        result = normalizer.normalize(self._azure_row(
            ResourceId='NULL', CommitmentDiscountId='null', RegionId='NULL',
            Tags='NULL', x_ResourceType='NULL'))
        self.assertEqual(result['resource_id'], 'virtual machines/d2')
        self.assertIsNone(result['region'])
        self.assertEqual(result['tags'], {})
        self.assertFalse(any(w.startswith('tags') for w in
                             normalizer.collect_warnings()))

    def test_azure_without_x_resource_type(self):
        columns = [c for c in AZURE_COLUMNS if c != 'x_ResourceType'] + [
            'ResourceType']
        normalizer = self._normalizer(columns=columns)
        result = normalizer.normalize(self._azure_row(
            ResourceType='Virtual machine'))
        self.assertEqual(result['resource_type'], 'Instance')

    def test_composite_identity_and_constant(self):
        normalizer = self._normalizer(
            columns=AZURE_COLUMNS + ['SubAccountId'], user_mapping={
                'resource_id': {'template': '{SubAccountId}/{ResourceName}'},
                'region': {'value': 'global'}})
        result = normalizer.normalize(self._azure_row(SubAccountId='sub1'))
        self.assertEqual(result['resource_id'], 'sub1/vm1')
        self.assertEqual(result['region'], 'global')

    def test_missing_required_column(self):
        with self.assertRaises(InvalidParameterException):
            self._normalizer(user_mapping={'cost': {'columns': ['Missing']}})

    def test_missing_optional_column_warns(self):
        normalizer = self._normalizer(user_mapping={
            'region': {'columns': ['x_SkuRegion']}})
        self.assertIsNone(normalizer.normalize(self._azure_row())['region'])
        self.assertTrue(any('region' in w for w in normalizer.warnings))

    def test_bad_values(self):
        normalizer = self._normalizer()
        with self.assertRaises(RowParseError):
            normalizer.normalize(self._azure_row(BilledCost='1,5'))
        with self.assertRaises(RowParseError):
            normalizer.normalize(self._azure_row(
                ChargePeriodStart='03/04/2025'))
        result = normalizer.normalize(self._azure_row(Tags='{broken'))
        self.assertEqual(result['tags'], {})
        self.assertIn('tags: 1 rows with unparsable tags skipped',
                      normalizer.collect_warnings())

    def test_oci(self):
        normalizer = self._normalizer(columns=OCI_COLUMNS)
        result = normalizer.normalize({
            'BilledCost': '2', 'BillingCurrency': 'USD',
            'ChargeCategory': 'Usage', 'ChargePeriodStart': '1715644800000',
            'ChargePeriodEnd': '1715648400000', 'Region': 'us-ashburn-1',
            'ResourceId': 'ocid1.instance.oc1..aaa', 'ResourceType':
                'Virtual Machine', 'ServiceName': 'Compute', 'SkuId': 'B1',
            'Tags': '{"orcl-cloud.free-tier-retained": "true"}'})
        self.assertEqual(result['region'], 'us-ashburn-1')
        self.assertEqual(result['resource_type'], 'Instance')
        self.assertEqual(result['tags'],
                         {'orcl-cloud.free-tier-retained': 'true'})
        self.assertEqual(result['end_date'], datetime(2024, 5, 14, 1))

    def test_oci_focus_1_0(self):
        columns = ['BilledCost', 'BillingCurrency', 'ChargeCategory',
                   'ChargePeriodStart', 'ChargePeriodEnd', 'RegionId',
                   'RegionName', 'ResourceId', 'ResourceType', 'ServiceName',
                   'SkuId', 'Tags', 'oci_CompartmentId']
        normalizer = self._normalizer(columns=columns)
        result = normalizer.normalize({
            'BilledCost': '2', 'BillingCurrency': 'USD',
            'ChargeCategory': 'Usage',
            'ChargePeriodStart': '2024-09-09 18:00:00',
            'ChargePeriodEnd': '2024-09-09 19:00:00', 'RegionId': '',
            'RegionName': 'us-sanjose-1', 'ResourceId': 'ocid1.instance.x',
            'ResourceType': 'instance', 'ServiceName': 'COMPUTE',
            'SkuId': 'B1', 'Tags': '', 'oci_CompartmentId': 'ocid1.c.x'})
        self.assertEqual(result['region'], 'us-sanjose-1')
        self.assertEqual(result['resource_type'], 'Instance')

    def test_prefixed_tags(self):
        columns = AZURE_COLUMNS + ['tag.env', 'tag.team']
        normalizer = self._normalizer(columns=columns, user_mapping={
            'tags': {'mode': 'prefixed_columns', 'prefix': 'tag.'}})
        result = normalizer.normalize(self._azure_row(**{
            'tag.env': 'prod', 'tag.team': ''}))
        self.assertEqual(result['tags'], {'env': 'prod'})

    def test_long_resource_id(self):
        result = self._normalizer().normalize(self._azure_row(
            ResourceId='x' * 600))
        self.assertLessEqual(len(result['resource_id']), 512)


class TestEndpoint(unittest.TestCase):
    @staticmethod
    def _resolve(ip):
        return patch('socket.getaddrinfo',
                     return_value=[(2, 1, 6, '', (ip, 443))])

    def test_public_https(self):
        with self._resolve('52.1.2.3'):
            validate_endpoint('https://s3.example.com')

    def test_rejected(self):
        for url, ip in [('https://meta', '169.254.169.254'),
                        ('https://minio', '10.0.0.5'),
                        ('https://local', '127.0.0.1'),
                        ('http://s3.example.com', '52.1.2.3'),
                        ('ftp://s3.example.com', '52.1.2.3')]:
            with self._resolve(ip):
                with self.assertRaises(InvalidParameterException, msg=url):
                    validate_endpoint(url)


class TestUserRegex(unittest.TestCase):
    def test_no_catastrophic_backtracking(self):
        regex = compile_user_regex('(a+)+$')
        start = time.monotonic()
        self.assertIsNone(regex.search('a' * 100000 + 'b'))
        self.assertLess(time.monotonic() - start, 1)

    def test_ignore_case(self):
        self.assertTrue(compile_user_regex(
            focus.DEFAULT_FILE_PATTERN, ignore_case=True).search('A.CSV'))
        self.assertFalse(compile_user_regex('csv').search('CSV'))

    def test_unsupported_syntax_rejected(self):
        for pattern in ['(', r'(a)\1', '(?=a)']:
            with self.assertRaises(InvalidParameterException, msg=pattern):
                validate_mapping({'resource_type': {
                    'columns': ['ServiceName'],
                    'rules': [{'column': 'A', 'match': pattern,
                               'type': 'Instance'}]}})


if __name__ == '__main__':
    unittest.main()
