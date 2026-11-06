import copy
import hashlib
import ipaddress
import json
import logging
import re
import socket
import uuid
from collections import defaultdict
from datetime import date, datetime, time, timezone
from decimal import Decimal
from functools import wraps
from urllib.parse import urlparse

import boto3
import re2
from botocore import UNSIGNED
from botocore.config import Config as BotoConfig
from botocore.exceptions import BotoCoreError, ClientError

from tools.cloud_adapter.clouds.base import S3CloudMixin, new_core_session
from tools.cloud_adapter.exceptions import (
    CloudConnectionError, InvalidParameterException)
from tools.cloud_adapter.utils import CloudParameter

LOG = logging.getLogger(__name__)

DEFAULT_FILE_PATTERN = r'\.(csv|csv\.gz|gz|zip|parquet)$'
AUTH_ERROR_CODES = {'AccessDenied', 'InvalidAccessKeyId',
                    'SignatureDoesNotMatch', 'AllAccessDisabled',
                    'InvalidToken', 'ExpiredToken'}
NO_BUCKET_ERROR_CODES = {'NoSuchBucket'}
# connection errors of a custom endpoint are not shown to the user
ENDPOINT_CONNECTION_ERROR = 'Cannot connect to s3_endpoint'


def compile_user_regex(pattern, ignore_case=False):
    """Compile a user-supplied regex with RE2: it matches in linear time, so
    a crafted pattern cannot hang a worker on crafted data. Raises
    ValueError."""
    options = re2.Options()
    options.log_errors = False
    options.case_sensitive = not ignore_case
    try:
        return re2.compile(pattern, options)
    except re2.error as exc:
        message = exc.args[0] if exc.args else ''
        if isinstance(message, bytes):
            message = message.decode('utf-8', errors='replace')
        raise ValueError(message) from exc


def _is_public(ip):
    return not (ip.is_private or ip.is_loopback or ip.is_link_local or
                ip.is_multicast or ip.is_reserved or ip.is_unspecified)


def validate_endpoint(url):
    # SSRF protection for a user-supplied s3_endpoint
    parsed = urlparse(url)
    if parsed.scheme != 'https' or not parsed.hostname:
        raise InvalidParameterException('s3_endpoint must be an https URL')
    try:
        infos = socket.getaddrinfo(parsed.hostname, parsed.port or 443,
                                   proto=socket.IPPROTO_TCP)
    except socket.gaierror as exc:
        raise InvalidParameterException(
            's3_endpoint host %s cannot be resolved' % parsed.hostname
        ) from exc
    for info in infos:
        ip = ipaddress.ip_address(info[4][0].split('%', 1)[0])
        if not _is_public(ip):
            raise InvalidParameterException(
                's3_endpoint resolves to a non-public address')


def handle_connection_errors(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except BotoCoreError as exc:
            raise CloudConnectionError(
                self._connection_error_text(exc)) from exc
    return wrapper


AWS_1_2 = 'aws_1.2'
AZURE_1_2 = 'azure_1.2'
AZURE_1_0 = 'azure_1.0'
OCI = 'oci'
GENERIC_1_2 = 'generic_1.2'
GENERIC_1_0 = 'generic_1.0'
UNKNOWN = 'unknown'

# ChargeCategory is filled in every FOCUS row, while purchases, credits and
# marketplace charges may have no ResourceId, ServiceName or SkuId
_CHARGE_CATEGORY = {'columns': ['ChargeCategory']}
_IDENTITY_FALLBACK = {
    'template': '{ServiceName}/{SkuId}',
    'fallback': {'template': '{ChargeCategory}/{ServiceName}',
                 'fallback': _CHARGE_CATEGORY}
}
_GENERIC_TYPE_RULES = [
    {'column': 'ResourceType', 'match': '(?i)snapshot',
     'type': 'Snapshot'},
    {'column': 'ResourceType', 'match': '(?i)virtual machine|instance',
     'type': 'Instance'},
    {'column': 'ResourceType', 'match': '(?i)disk|volume',
     'type': 'Volume'},
    {'column': 'ResourceType', 'match': '(?i)bucket|storage account',
     'type': 'Bucket'},
    {'column': 'ResourceType', 'match': '(?i)ip address',
     'type': 'IP Address'},
]

GENERIC_MAPPING = {
    'cost': {'columns': ['BilledCost'], 'decimal_separator': '.'},
    'start_date': {'columns': ['ChargePeriodStart']},
    'end_date': {'columns': ['ChargePeriodEnd']},
    'resource_id': {
        'columns': ['ResourceId', 'CommitmentDiscountId'],
        'normalize': ['strip'],
        'fallback': _IDENTITY_FALLBACK
    },
    'resource_type': {
        'rules': _GENERIC_TYPE_RULES,
        'columns': ['ServiceName'],
        'fallback': _CHARGE_CATEGORY
    },
    'name': {'columns': ['ResourceName']},
    'region': {'columns': ['RegionId', 'RegionName']},
    'service_name': {'columns': ['ServiceName']},
    'tags': {'columns': ['Tags'], 'mode': 'json'},
}

_FORMAT_OVERRIDES = {
    AWS_1_2: {
        'resource_type': {
            'rules': [
                {'column': 'x_Operation', 'match': '^RunInstances',
                 'type': 'Instance'},
                {'column': 'x_Operation', 'match': '^CreateSnapshot',
                 'type': 'Snapshot'},
                {'column': 'x_Operation', 'match': '^CreateVolume',
                 'type': 'Volume'},
                {'column': 'x_ServiceCode', 'match': '^AmazonS3$',
                 'type': 'Bucket'},
                {'column': 'x_Operation', 'match': '^AssociateAddress',
                 'type': 'IP Address'},
            ],
            'columns': ['ServiceName'],
            'fallback': _CHARGE_CATEGORY
        },
    },
    AZURE_1_2: {
        'resource_id': {
            'columns': ['ResourceId', 'CommitmentDiscountId'],
            'normalize': ['strip', 'lower'],
            'fallback': _IDENTITY_FALLBACK
        },
        'resource_type': {
            'rules': [
                {'column': 'x_ResourceType',
                 'match': r'(?i)^microsoft\.compute/virtualmachines$',
                 'type': 'Instance'},
                {'column': 'x_ResourceType',
                 'match': r'(?i)^microsoft\.compute/disks$',
                 'type': 'Volume'},
                {'column': 'x_ResourceType',
                 'match': r'(?i)^microsoft\.compute/snapshots$',
                 'type': 'Snapshot'},
                {'column': 'x_ResourceType',
                 'match': r'(?i)^microsoft\.storage/storageaccounts$',
                 'type': 'Bucket'},
                {'column': 'x_ResourceType',
                 'match': r'(?i)^microsoft\.network/publicipaddresses$',
                 'type': 'IP Address'},
                # exports without x_ResourceType
            ] + _GENERIC_TYPE_RULES,
            'columns': ['ServiceName'],
            'fallback': _CHARGE_CATEGORY
        },
    },
    OCI: {
        'resource_id': {
            'columns': ['ResourceId'],
            'normalize': ['strip'],
            'fallback': _IDENTITY_FALLBACK
        },
        # Region is the column of FOCUS 0.5
        'region': {'columns': ['RegionId', 'RegionName', 'Region']},
    },
    UNKNOWN: {
        'region': {'columns': ['RegionId', 'RegionName', 'Region']},
    },
}
_FORMAT_OVERRIDES[AZURE_1_0] = _FORMAT_OVERRIDES[AZURE_1_2]

_AZURE_SIGNALS = {'x_ResourceGroupName', 'x_SkuMeterId'}
_AWS_SIGNALS = {'x_ServiceCode', 'x_Operation'}
_GENERIC_1_2_SIGNALS = {'InvoiceId', 'PricingCurrency', 'BillingAccountType'}


def detect_format(columns):
    # Detect a FOCUS variant from a file's column names.
    columns = set(columns)
    if columns & _AWS_SIGNALS:
        return AWS_1_2
    if columns & _AZURE_SIGNALS:
        if 'InvoiceId' in columns:
            return AZURE_1_2
        return AZURE_1_0
    if any(c.startswith('oci_') for c in columns) or (
            # FOCUS 0.5 report of OCI
            'Region' in columns and 'RegionId' not in columns and
            columns & {'UsageQuantity', 'ChargeSubcategory'}):
        return OCI
    if columns & _GENERIC_1_2_SIGNALS:
        return GENERIC_1_2
    if {'RegionId', 'ChargeClass'} <= columns:
        return GENERIC_1_0
    return UNKNOWN


def default_mapping(fmt):
    mapping = copy.deepcopy(GENERIC_MAPPING)
    mapping.update(copy.deepcopy(_FORMAT_OVERRIDES.get(fmt, {})))
    return mapping


def _source_chain(rule):
    """Sources and fallbacks of a rule without the field parameters, marked
    as taken from the default mapping."""
    chain = {k: v for k, v in rule.items() if k in SOURCE_KEYS}
    chain[FROM_DEFAULT] = True
    if rule.get('fallback'):
        chain['fallback'] = _source_chain(rule['fallback'])
    return chain


def _with_default(field, rule, default_rule):
    """Replace {"default": true} at the end of the fallback chain with the
    default rule. Field parameters not set by the user are taken from the
    default rule, default resource type rules go after the user ones."""
    rule = copy.deepcopy(rule)
    node = rule
    while node.get('fallback') and not node['fallback'].get(DEFAULT_SOURCE):
        node = node['fallback']
    if not node.get('fallback'):
        return rule
    node['fallback'] = _source_chain(default_rule)
    for param in FIELD_PARAMS.get(field, ()):
        if param == 'rules':
            rule['rules'] = rule.get('rules', []) + copy.deepcopy(
                default_rule.get('rules', []))
        elif param not in rule and param in default_rule:
            rule[param] = copy.deepcopy(default_rule[param])
    return rule


def effective_mapping(fmt, user_mapping=None):
    """Defaults for the format, with user fields replacing whole fields."""
    mapping = default_mapping(fmt)
    for field, rule in (user_mapping or {}).items():
        mapping[field] = _with_default(field, rule, mapping[field])
    return mapping


# ---- mapping validation and row normalization ----

REQUIRED_FIELDS = ('cost', 'start_date', 'end_date', 'resource_id',
                   'resource_type')
OPTIONAL_FIELDS = ('name', 'region', 'service_name', 'tags')
FIELDS = REQUIRED_FIELDS + OPTIONAL_FIELDS

SOURCE_KEYS = ('columns', 'value', 'template')
# the last fallback {"default": true} is the rule of the default mapping
DEFAULT_SOURCE = 'default'
# marks the part of an effective rule taken from the default mapping
FROM_DEFAULT = '_from_default'
DECIMAL_SEPARATORS = ('.', ',')
NORMALIZE_OPTIONS = ('strip', 'lower')
TAG_MODES = ('json', 'list', 'prefixed_columns')

FIELD_PARAMS = {
    'cost': {'decimal_separator'},
    'resource_id': {'normalize'},
    'resource_type': {'rules'},
    'tags': {'mode', 'prefix'},
}

# rest_api limits for cloud resource string fields
MAX_RESOURCE_ID_LEN = 512
MAX_NAME_LEN = 512
MAX_ATTR_LEN = 255

COMMITMENT_ID_COLUMN = 'CommitmentDiscountId'
COMMITMENT_TYPE_COLUMN = 'CommitmentDiscountType'
CURRENCY_COLUMN = 'BillingCurrency'
# FOCUS cost columns denominated in BillingCurrency
BILLING_CURRENCY_COST_COLUMNS = {'BilledCost', 'EffectiveCost', 'ListCost',
                                 'ContractedCost'}

PLACEHOLDER_RE = re.compile(r'\{([^{}]+)\}')
NUMBER_RE = re.compile(r'^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$')
COMPACT_DATE_RE = re.compile(r'^\d{8}$')
UTC_SUFFIX_RE = re.compile(r'\s*(Z|UTC|GMT)$', re.IGNORECASE)
EPOCH_MS_THRESHOLD = 10 ** 11
MIN_EPOCH = 10 ** 9


def _err(path, message):
    raise InvalidParameterException('mapping.%s: %s' % (path, message))


def _validate_source(path, rule, is_fallback=False):
    if is_fallback and DEFAULT_SOURCE in rule:
        if rule != {DEFAULT_SOURCE: True}:
            _err(path, '"default" must be true and the last fallback')
        return
    sources = [k for k in SOURCE_KEYS if k in rule]
    if len(sources) != 1:
        _err(path, 'exactly one of %s is required' % ', '.join(SOURCE_KEYS))
    source = sources[0]
    value = rule[source]
    if source == 'columns':
        if (not isinstance(value, list) or not value or
                not all(isinstance(c, str) and c.strip() for c in value)):
            _err(path + '.columns', 'must be a non-empty list of column names')
    elif source == 'value':
        if isinstance(value, bool) or not isinstance(value, (str, int, float)):
            _err(path + '.value', 'must be a string or a number')
    else:
        if not isinstance(value, str) or not PLACEHOLDER_RE.search(value):
            _err(path + '.template',
                 'must be a string with at least one {Column} placeholder')
    if 'fallback' in rule:
        fallback = rule['fallback']
        if not isinstance(fallback, dict):
            _err(path + '.fallback', 'must be an object')
        unexpected = set(fallback) - set(SOURCE_KEYS) - {
            'fallback', DEFAULT_SOURCE}
        if unexpected:
            _err(path + '.fallback',
                 'unexpected keys: %s' % ', '.join(sorted(unexpected)))
        _validate_source(path + '.fallback', fallback, is_fallback=True)


def _validate_rules(path, rules):
    if not isinstance(rules, list):
        _err(path, 'must be a list')
    for i, item in enumerate(rules):
        item_path = '%s[%s]' % (path, i)
        if not isinstance(item, dict) or set(item) != {'column', 'match',
                                                       'type'}:
            _err(item_path, 'must have exactly column, match and type')
        for key in ('column', 'match', 'type'):
            if not isinstance(item[key], str) or not item[key].strip():
                _err('%s.%s' % (item_path, key), 'must be a non-empty string')
        try:
            compile_user_regex(item['match'])
        except ValueError as exc:
            _err(item_path + '.match', 'invalid regex: %s' % exc)
        if len(item['type']) > MAX_ATTR_LEN:
            _err(item_path + '.type', 'is too long')


def validate_mapping(mapping):
    """Validate a user mapping. Raises InvalidParameterException."""
    if mapping is None:
        return
    if not isinstance(mapping, dict):
        raise InvalidParameterException('mapping must be an object')
    unexpected = set(mapping) - set(FIELDS)
    if unexpected:
        _err(', '.join(sorted(unexpected)), 'unknown field')
    for field, rule in mapping.items():
        if not isinstance(rule, dict):
            _err(field, 'must be an object')
        allowed = set(SOURCE_KEYS) | {'fallback'} | FIELD_PARAMS.get(
            field, set())
        unexpected = set(rule) - allowed
        if unexpected:
            _err(field, 'unexpected keys: %s' % ', '.join(sorted(unexpected)))
        if field == 'tags' and rule.get('mode') == 'prefixed_columns':
            prefix = rule.get('prefix')
            if not isinstance(prefix, str) or not prefix:
                _err('tags.prefix', 'is required for prefixed_columns mode')
            if any(k in rule for k in SOURCE_KEYS) or 'fallback' in rule:
                _err('tags', 'prefixed_columns mode takes no source')
        else:
            _validate_source(field, rule)
        if field == 'cost' and 'decimal_separator' in rule:
            if rule['decimal_separator'] not in DECIMAL_SEPARATORS:
                _err('cost.decimal_separator',
                     'must be one of %s' % ', '.join(DECIMAL_SEPARATORS))
        if field == 'resource_id' and 'normalize' in rule:
            normalize = rule['normalize']
            if (
                    not isinstance(normalize, list) or
                    not all(isinstance(o, str) and o in NORMALIZE_OPTIONS
                            for o in normalize)
            ):
                _err('resource_id.normalize', 'must be a list of %s' %
                     ', '.join(NORMALIZE_OPTIONS))
        if field == 'resource_type' and 'rules' in rule:
            _validate_rules('resource_type.rules', rule['rules'])
        if field == 'tags':
            mode = rule.get('mode', 'json')
            if mode not in TAG_MODES:
                _err('tags.mode', 'must be one of %s' % ', '.join(TAG_MODES))
            if 'prefix' in rule and mode != 'prefixed_columns':
                _err('tags.prefix', 'is only used in prefixed_columns mode')
            if mode != 'json' and _uses_default(rule):
                # tags of all default mappings are json
                _err('tags', '"default" fallback needs json mode')


def _has_default_part(rule):
    while rule:
        if rule.get(FROM_DEFAULT):
            return True
        rule = rule.get('fallback')
    return False


def _uses_default(rule):
    while rule:
        if rule.get(DEFAULT_SOURCE):
            return True
        rule = rule.get('fallback')
    return False


class RowParseError(ValueError):
    def __init__(self, field, column, value, reason):
        self.field = field
        self.column = column
        self.value = value
        super().__init__('%s: %s value %r in column %s' % (
            field, reason, _short(value), column))


def _short(value, limit=64):
    text = str(value)
    return text if len(text) <= limit else text[:limit] + '...'


def is_empty(value):
    if value is None:
        return True
    if isinstance(value, str):
        # CSV exported from SQL engines writes NULL for empty values
        return not value.strip() or value.strip().upper() == 'NULL'
    if isinstance(value, (list, dict, tuple)):
        return not value
    return False


def _as_text(value):
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def parse_datetime(value):
    # Parse a FOCUS date to a naive UTC datetime.
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, date):
        dt = datetime.combine(value, time())
    elif isinstance(value, (int, float, Decimal)) and not isinstance(
            value, bool):
        dt = _from_epoch(float(value))
    elif isinstance(value, str):
        text = value.strip()
        if COMPACT_DATE_RE.match(text):
            dt = datetime.strptime(text, '%Y%m%d')
        elif NUMBER_RE.match(text):
            dt = _from_epoch(float(text))
        else:
            dt = datetime.fromisoformat(UTC_SUFFIX_RE.sub('+00:00', text))
    else:
        raise ValueError('unsupported date type %s' % type(value).__name__)
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def _from_epoch(number):
    if abs(number) >= EPOCH_MS_THRESHOLD:
        number = number / 1000
    if number < MIN_EPOCH:
        raise ValueError('%s is not an epoch timestamp' % number)
    return datetime.fromtimestamp(number, tz=timezone.utc)


def parse_number(value, decimal_separator='.'):
    if isinstance(value, bool):
        raise ValueError('boolean is not a number')
    if isinstance(value, (int, float, Decimal)):
        return float(value)
    if not isinstance(value, str):
        raise ValueError('unsupported number type %s' % type(value).__name__)
    text = value.strip()
    if not text:
        return 0.0
    if decimal_separator == ',':
        if '.' in text:
            raise ValueError('unexpected "." with decimal separator ","')
        text = text.replace(',', '.')
    if not NUMBER_RE.match(text):
        raise ValueError('not a number')
    return float(text)


def flatten_tags(raw_tags):
    """Flatten nested tag values into dot-separated string keys."""
    tags = {}

    def _flatten(key, value):
        if isinstance(value, dict):
            for k, v in value.items():
                _flatten('%s.%s' % (key, k), v)
        elif isinstance(value, list):
            for i, v in enumerate(value):
                _flatten('%s.%s' % (key, i), v)
        elif isinstance(value, bool):
            tags[key] = 'true' if value else 'false'
        elif value is not None:
            tags[key] = value if isinstance(value, str) else str(value)

    for k, v in raw_tags.items():
        _flatten(str(k), v)
    return tags


def _pairs_to_dict(items):
    """Turn a list of pairs, "k:v" / "k=v" strings or {key, value} dicts
    into a dict."""
    result = {}
    for item in items:
        if isinstance(item, (list, tuple)) and len(item) == 2:
            result[str(item[0])] = item[1]
        elif isinstance(item, dict):
            key = item.get('key', item.get('Key'))
            if key is None:
                raise ValueError('tag item without key')
            result[str(key)] = item.get('value', item.get('Value'))
        elif isinstance(item, str):
            sep = ':' if ':' in item else '=' if '=' in item else None
            if sep is None:
                result[item] = ''
            else:
                k, v = item.split(sep, 1)
                result[k.strip()] = v.strip()
        else:
            raise ValueError('unsupported tag item')
    return result


def parse_tags(value, mode):
    if is_empty(value):
        return {}
    if isinstance(value, str):
        value = json.loads(value)
    if isinstance(value, dict):
        return flatten_tags(value)
    if isinstance(value, (list, tuple)):
        # pyarrow returns map columns as a list of (key, value) tuples
        return flatten_tags(_pairs_to_dict(value))
    raise ValueError('unsupported tags type %s' % type(value).__name__)


def _truncate_id(value):
    if len(value) <= MAX_RESOURCE_ID_LEN:
        return value
    digest = hashlib.sha1(value.encode('utf-8')).hexdigest()[:16]
    return '%s#%s' % (value[:MAX_RESOURCE_ID_LEN - 17], digest)


class RowNormalizer:
    def __init__(self, mapping, columns):
        self.mapping = mapping
        self.columns = list(columns)
        self._column_set = set(self.columns)
        self.warnings = []
        self.bad_tags_rows = 0
        # field -> number of rows that took the default mapping
        self.default_rows = defaultdict(int)
        # the column the cost of the last normalized row was taken from
        self.cost_column = None
        self._check_columns()
        self._rules = [
            (r['column'], compile_user_regex(r['match']), r['type'])
            for r in mapping['resource_type'].get('rules', [])
            if r['column'] in self._column_set
        ]
        tags_rule = mapping.get('tags') or {}
        self._tags_mode = tags_rule.get('mode', 'json')
        self._tag_columns = []
        if self._tags_mode == 'prefixed_columns':
            prefix = tags_rule['prefix']
            self._tag_columns = [(c, c[len(prefix):]) for c in self.columns
                                 if c.startswith(prefix) and len(c) > len(
                                     prefix)]
            if not self._tag_columns:
                self.warnings.append('tags: no columns with prefix %s found '
                                     'in file; tags are empty' % prefix)
        self._decimal_separator = mapping['cost'].get(
            'decimal_separator', '.')
        self._normalize = mapping['resource_id'].get('normalize', [])

    @property
    def cost_in_billing_currency(self):
        """Whether the cost of the last normalized row was taken from a
        column in BillingCurrency."""
        return self.cost_column in BILLING_CURRENCY_COST_COLUMNS

    def _source_columns(self, rule):
        columns = list(rule.get('columns', []))
        if 'template' in rule:
            columns.extend(PLACEHOLDER_RE.findall(rule['template']))
        return columns

    def _can_resolve(self, rule, user_only=False):
        """Whether any source in the fallback chain can yield a value."""
        while rule:
            if user_only and rule.get(FROM_DEFAULT):
                return False
            if 'value' in rule:
                return True
            if 'columns' in rule and set(rule['columns']) & self._column_set:
                return True
            if 'template' in rule and set(PLACEHOLDER_RE.findall(
                    rule['template'])) <= self._column_set:
                return True
            rule = rule.get('fallback')
        return False

    def _check_columns(self):
        for field in FIELDS:
            rule = self.mapping.get(field)
            if not rule:
                continue
            if field == 'tags' and rule.get('mode') == 'prefixed_columns':
                continue
            if self._can_resolve(rule):
                if (_has_default_part(rule) and
                        not self._can_resolve(rule, user_only=True)):
                    self.warnings.append(
                        '%s: none of the mapped columns found in file; '
                        'default mapping is used for all rows' % field)
                for column in self._missing_template_columns(rule):
                    self.warnings.append(
                        '%s: template uses missing column %s; fallback is '
                        'used for all rows' % (field, column))
                continue
            columns = sorted(set(self._chain_columns(rule)))
            if field in REQUIRED_FIELDS:
                raise InvalidParameterException(
                    '%s: none of columns %s found in file' % (
                        field, ', '.join(columns)))
            self.warnings.append('%s: none of columns %s found in file; %s '
                                 'is empty' % (field, ', '.join(columns),
                                               field))
        missing = sorted({r['column'] for r in self.mapping[
            'resource_type'].get('rules', [])} - self._column_set)
        for column in missing:
            self.warnings.append('resource_type: rule column %s not found; '
                                 'its rules are skipped' % column)

    def _chain_columns(self, rule):
        while rule:
            yield from self._source_columns(rule)
            rule = rule.get('fallback')

    def _missing_template_columns(self, rule):
        missing = []
        while rule:
            if 'template' in rule:
                missing.extend(c for c in PLACEHOLDER_RE.findall(
                    rule['template']) if c not in self._column_set)
            rule = rule.get('fallback')
        return missing

    def _resolve(self, field, row):
        """Returns (value, column) of the first non-empty source."""
        rule = self.mapping[field]
        while rule:
            value, column = self._resolve_source(rule, row)
            if not is_empty(value):
                if rule.get(FROM_DEFAULT):
                    self.default_rows[field] += 1
                return value, column
            rule = rule.get('fallback')
        return None, None

    @staticmethod
    def _resolve_source(rule, row):
        if 'value' in rule:
            return rule['value'], None
        if 'columns' in rule:
            for column in rule['columns']:
                value = row.get(column)
                if not is_empty(value):
                    return value, column
        if 'template' in rule:
            values = {}
            for column in PLACEHOLDER_RE.findall(rule['template']):
                value = row.get(column)
                if is_empty(value):
                    return None, None
                values[column] = _as_text(value)
            return PLACEHOLDER_RE.sub(
                lambda m: values[m.group(1)], rule['template']), None
        return None, None

    def _text_field(self, field, row, max_len):
        if not self.mapping.get(field):
            return None
        value, _ = self._resolve(field, row)
        if is_empty(value):
            return None
        return _as_text(value)[:max_len]

    def _resource_type(self, row, id_column):
        if id_column == COMMITMENT_ID_COLUMN:
            value = row.get(COMMITMENT_TYPE_COLUMN)
            if not is_empty(value):
                return _as_text(value)[:MAX_ATTR_LEN]
        for column, regex, res_type in self._rules:
            value = row.get(column)
            if not is_empty(value) and regex.search(_as_text(value)):
                return res_type
        value, _ = self._resolve('resource_type', row)
        if is_empty(value):
            return None
        return _as_text(value)[:MAX_ATTR_LEN]

    def _date(self, field, row):
        value, column = self._resolve(field, row)
        if is_empty(value):
            raise RowParseError(field, column, value, 'empty')
        try:
            return parse_datetime(value)
        except (ValueError, OverflowError, OSError) as exc:
            raise RowParseError(field, column, value,
                                'cannot parse date (%s)' % exc)

    def _tags(self, row):
        if self._tags_mode == 'prefixed_columns':
            raw = {key: row.get(column) for column, key in self._tag_columns
                   if not is_empty(row.get(column))}
            return flatten_tags(raw)
        if not self.mapping.get('tags'):
            return {}
        value, _ = self._resolve('tags', row)
        try:
            return parse_tags(value, self._tags_mode)
        except (ValueError, TypeError):
            self.bad_tags_rows += 1
            return {}

    def normalize(self, row):
        """Return normalized fields for a row. Raises RowParseError."""
        cost_value, cost_column = self._resolve('cost', row)
        self.cost_column = cost_column
        try:
            cost = 0.0 if is_empty(cost_value) else parse_number(
                cost_value, self._decimal_separator)
        except (ValueError, ArithmeticError) as exc:
            raise RowParseError('cost', cost_column, cost_value,
                                'cannot parse number (%s)' % exc)
        start_date = self._date('start_date', row)
        end_date = self._date('end_date', row)
        if end_date < start_date:
            raise RowParseError('end_date', None, end_date,
                                'end before start')
        resource_id, id_column = self._resolve('resource_id', row)
        if is_empty(resource_id):
            raise RowParseError('resource_id', id_column, resource_id,
                                'empty')
        resource_id = _as_text(resource_id)
        if 'lower' in self._normalize:
            resource_id = resource_id.lower()
        resource_id = _truncate_id(resource_id)
        resource_type = self._resource_type(row, id_column)
        if not resource_type:
            raise RowParseError('resource_type', None, None, 'empty')
        return {
            'cost': cost,
            'start_date': start_date,
            'end_date': end_date,
            'resource_id': resource_id,
            'resource_type': resource_type,
            'name': self._text_field('name', row, MAX_NAME_LEN),
            'region': self._text_field('region', row, MAX_ATTR_LEN),
            'service_name': self._text_field('service_name', row,
                                             MAX_ATTR_LEN),
            'tags': self._tags(row),
        }

    def collect_warnings(self):
        warnings = list(self.warnings)
        if self.bad_tags_rows:
            warnings.append('tags: %s rows with unparsable tags skipped' %
                            self.bad_tags_rows)
        for field, count in sorted(self.default_rows.items()):
            warnings.append('%s: %s rows took the default mapping' % (
                field, count))
        return warnings


class Focus(S3CloudMixin):
    """FOCUS cost and usage files in S3-compatible storage."""

    BILLING_CREDS = [
        CloudParameter(name='bucket_name', type=str, required=False),
        CloudParameter(name='bucket_prefix', type=str, required=False),
        CloudParameter(name='s3_endpoint', type=str, required=False),
        CloudParameter(name='region_name', type=str, required=False),
        # no credentials mean anonymous access
        CloudParameter(name='credentials', type=dict, required=False,
                       dependencies=[
                           CloudParameter(name='access_key_id', type=str,
                                          required=True),
                           CloudParameter(name='secret_access_key', type=str,
                                          required=True, protected=True),
                       ]),
        CloudParameter(name='file_pattern', type=str, required=False),
        CloudParameter(name='mapping', type=dict, required=False),
    ]
    SUPPORTS_REPORT_UPLOAD = True

    def __init__(self, cloud_config, *args, **kwargs):
        super().__init__(cloud_config, *args, **kwargs)
        self._s3_client = None
        self._currency = None

    @property
    def bucket_name(self):
        return self.config.get('bucket_name')

    @property
    def bucket_prefix(self):
        return (self.config.get('bucket_prefix') or '').lstrip('/')

    @property
    def s3_endpoint(self):
        return self.config.get('s3_endpoint')

    @property
    def credentials(self):
        return self.config.get('credentials') or {}

    @property
    def is_anonymous(self):
        return not self.credentials

    @property
    def file_pattern(self):
        return compile_user_regex(self.config.get('file_pattern') or
                                  DEFAULT_FILE_PATTERN, ignore_case=True)

    def _validate_settings(self):
        validate_mapping(self.config.get('mapping'))
        try:
            self.file_pattern
        except ValueError as exc:
            raise InvalidParameterException(
                'file_pattern: invalid regex: %s' % exc) from exc
        if self.s3_endpoint:
            validate_endpoint(self.s3_endpoint)

    def _account_id(self):
        if not self.bucket_name:
            return str(uuid.uuid4())
        endpoint = (self.s3_endpoint or 'aws').strip().rstrip('/').lower()
        source = '|'.join([endpoint, self.bucket_name,
                           self.bucket_prefix.rstrip('/')])
        return hashlib.sha256(source.encode('utf-8')).hexdigest()[:32]

    def validate_credentials(self, org_id=None):
        self._validate_settings()
        warnings = self._check_access() if self.bucket_name else []
        return {'account_id': self._account_id(), 'warnings': warnings}

    def _make_client(self, addressing_style):
        config_kwargs = {
            's3': {'addressing_style': addressing_style},
            'connect_timeout': 20,
            'read_timeout': 60,
            'retries': {'max_attempts': 3},
        }
        if self.is_anonymous:
            # never fall back to the credentials of the OptScale host
            config_kwargs['signature_version'] = UNSIGNED
        session = boto3.Session(
            aws_access_key_id=self.credentials.get('access_key_id'),
            aws_secret_access_key=self.credentials.get('secret_access_key'),
            botocore_session=new_core_session())
        client_kwargs = {'config': BotoConfig(**config_kwargs)}
        if self.s3_endpoint:
            client_kwargs['endpoint_url'] = self.s3_endpoint
        if self.config.get('region_name'):
            client_kwargs['region_name'] = self.config['region_name']
        return session.client('s3', **client_kwargs)

    def _addressing_styles(self):
        if not self.s3_endpoint:
            return ['virtual']
        if '.' in self.bucket_name:
            return ['path']
        return ['path', 'virtual']

    def _virtual_endpoint(self):
        parsed = urlparse(self.s3_endpoint)
        port = ':%s' % parsed.port if parsed.port else ''
        return 'https://%s.%s%s' % (self.bucket_name, parsed.hostname, port)

    def _connection_error_text(self, exc):
        if not self.s3_endpoint:
            return str(exc)
        LOG.warning('Connection to s3_endpoint %s failed: %s',
                    self.s3_endpoint, exc)
        return ENDPOINT_CONNECTION_ERROR

    def _detect_client(self):
        """Create an S3 client, trying addressing styles until listing the
        bucket works. The working style is not stored."""
        if not self.bucket_name:
            raise InvalidParameterException('bucket_name is not set')
        if self.s3_endpoint:
            validate_endpoint(self.s3_endpoint)
        errors = []
        for style in self._addressing_styles():
            if self.s3_endpoint and style == 'virtual':
                # virtual style connects to <bucket>.<endpoint host>:
                # validate it too
                try:
                    validate_endpoint(self._virtual_endpoint())
                except InvalidParameterException as exc:
                    errors.append((style, '', str(exc)))
                    continue
            client = self._make_client(style)
            try:
                client.list_objects_v2(Bucket=self.bucket_name,
                                       Prefix=self.bucket_prefix, MaxKeys=1)
                LOG.info('Using %s addressing style for bucket %s', style,
                         self.bucket_name)
                return client
            except ClientError as exc:
                errors.append((style, exc.response.get('Error', {}).get(
                    'Code', ''), str(exc)))
            except BotoCoreError as exc:
                errors.append((style, '', self._connection_error_text(exc)))
        codes = {code for _, code, _ in errors}
        message = '; '.join('%s style: %s' % (style, text)
                            for style, _, text in errors)
        if codes & NO_BUCKET_ERROR_CODES:
            raise InvalidParameterException(
                'Bucket %s not found' % self.bucket_name)
        if codes & AUTH_ERROR_CODES:
            raise InvalidParameterException(
                'Access to bucket %s is denied (ListBucket): %s' % (
                    self.bucket_name, message))
        raise CloudConnectionError(message)

    @property
    def s3(self):
        if self._s3_client is None:
            self._s3_client = self._detect_client()
        return self._s3_client

    def _matches(self, key):
        if key.endswith('/'):
            return False
        return bool(self.file_pattern.search(key.rsplit('/', 1)[-1]))

    @staticmethod
    def group_key(file_key):
        """Files are grouped by their parent directory, '/' for the bucket
        root: diworker skips state saving for an empty key."""
        return file_key.rsplit('/', 1)[0] if '/' in file_key else '/'

    @handle_connection_errors
    def get_report_files(self):
        """Return {group: [{Key, ETag, LastModified, Size}]} for files under
        the prefix that match file_pattern."""
        groups = defaultdict(list)
        paginator = self.s3.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=self.bucket_name,
                                       Prefix=self.bucket_prefix):
            for obj in page.get('Contents', []):
                if not self._matches(obj['Key']):
                    continue
                groups[self.group_key(obj['Key'])].append({
                    'Key': obj['Key'],
                    'ETag': obj.get('ETag', ''),
                    'LastModified': obj.get('LastModified'),
                    'Size': obj.get('Size', 0),
                })
        return dict(groups)

    @handle_connection_errors
    def download_report_file(self, report_name, file_obj):
        self.s3.download_fileobj(self.bucket_name, report_name, file_obj)

    @handle_connection_errors
    def _check_access(self):
        """Check storage access without reading report data. Returns
        warnings."""
        paginator = self.s3.get_paginator('list_objects_v2')
        matched = next(
            (o['Key'] for page in paginator.paginate(
                Bucket=self.bucket_name, Prefix=self.bucket_prefix)
             for o in page.get('Contents', []) if self._matches(o['Key'])),
            None)
        if not matched:
            return ['No files matching %s found under %s/%s' % (
                self.file_pattern.pattern, self.bucket_name,
                self.bucket_prefix)]
        try:
            self.s3.head_object(Bucket=self.bucket_name, Key=matched)
        except ClientError as exc:
            code = exc.response.get('Error', {}).get('Code', '')
            if code in AUTH_ERROR_CODES or code in ('403', 'Forbidden'):
                raise InvalidParameterException(
                    'Reading objects in bucket %s is denied (GetObject)' %
                    self.bucket_name) from exc
            raise CloudConnectionError(str(exc)) from exc
        return []

    def configure_report(self):
        # storage access is checked in validate_credentials
        return {'config_updates': {}, 'warnings': []}

    def set_currency(self, currency):
        self._currency = currency

    def get_regions_coordinates(self, load=True):
        return {}

    def discovery_calls_map(self):
        return {}
