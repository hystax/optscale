import enum
import io
import json
import logging
import os
import re
import base64
import uuid
import hashlib
import cryptocode
from urllib.parse import urlencode
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from decimal import Decimal
from string import ascii_letters, digits

import json_excel_converter.xlsx.formats as ExcelFormats
import netaddr
from bson import ObjectId
from config_client.client import Client as ConfigClient
from json_excel_converter import Converter as ExcelConverter
from json_excel_converter.xlsx import (Writer as ExcelWriter,
                                       DEFAULT_COLUMN_WIDTH)
from sqlalchemy.exc import InternalError, DatabaseError

from optscale_exceptions.common_exc import (WrongArgumentsException,
                                            NotFoundException,
                                            ConflictException,
                                            FailedDependency,
                                            ForbiddenException,
                                            TimeoutException)
from optscale_exceptions.http_exc import OptHTTPError
from pymongo.errors import BulkWriteError
from cloud_adapter.exceptions import CloudAdapterBaseException
from rest_api_server.exceptions import Err
from retrying import retry
import unicodedata

MAX_32_INT = 2 ** 31 - 1
MAX_64_INT = 2 ** 63 - 1
BASE_POOL_EXPENSES_EXPORT_LINK_FORMAT = 'https://{0}/restapi/v2/pool_expenses_exports/{1}'
tp_executor = ThreadPoolExecutor(30)
tp_executor_context = ThreadPoolExecutor(30)
tp_executor_license = ThreadPoolExecutor(10)
tp_executor_bulk_cloud_calls = ThreadPoolExecutor(16)
LOG = logging.getLogger(__name__)
GB = 1024 * 1024 * 1024
SECONDS_IN_HOUR = 60 * 60
CURRENCY_MAP = {
    "AED": "د.إ",
    "AFN": "؋",
    "ALL": "L",
    "AMD": "֏",
    "ANG": "ƒ",
    "AOA": "Kz",
    "ARS": "$",
    "AUD": "$",
    "AWG": "ƒ",
    "AZN": "₼",
    "BAM": "KM",
    "BBD": "$",
    "BDT": "৳",
    "BGN": "лв",
    "BHD": ".د.ب",
    "BIF": "FBu",
    "BMD": "$",
    "BND": "$",
    "BOB": "$b",
    "BOV": "BOV",
    "BRL": "R$",
    "BSD": "$",
    "BTN": "Nu.",
    "BWP": "P",
    "BYN": "Br",
    "BZD": "BZ$",
    "CAD": "CA$",
    "CDF": "FC",
    "CHE": "CHE",
    "CHF": "CHF",
    "CHW": "CHW",
    "CLF": "UF",
    "CLP": "$",
    "CNY": "¥",
    "COP": "$",
    "COU": "COU",
    "CRC": "₡",
    "CUC": "$",
    "CUP": "₱",
    "CVE": "$",
    "CZK": "Kč",
    "DJF": "Fdj",
    "DKK": "kr",
    "DOP": "RD$",
    "DZD": "دج",
    "EGP": "£",
    "ERN": "Nfk",
    "ETB": "Br",
    "EUR": "€",
    "FJD": "$",
    "FKP": "£",
    "GBP": "£",
    "GEL": "₾",
    "GHS": "GH₵",
    "GIP": "£",
    "GMD": "D",
    "GNF": "FG",
    "GTQ": "Q",
    "GYD": "$",
    "HKD": "$",
    "HNL": "L",
    "HRK": "kn",
    "HTG": "G",
    "HUF": "Ft",
    "IDR": "Rp",
    "ILS": "₪",
    "INR": "₹",
    "IQD": "ع.د",
    "IRR": "﷼",
    "ISK": "kr",
    "JMD": "J$",
    "JOD": "JD",
    "JPY": "¥",
    "KES": "KSh",
    "KGS": "лв",
    "KHR": "៛",
    "KMF": "CF",
    "KPW": "₩",
    "KRW": "₩",
    "KWD": "KD",
    "KYD": "$",
    "KZT": "лв",
    "LAK": "₭",
    "LBP": "£",
    "LKR": "₨",
    "LRD": "$",
    "LSL": "M",
    "LYD": "LD",
    "MAD": "MAD",
    "MDL": "lei",
    "MGA": "Ar",
    "MKD": "ден",
    "MMK": "K",
    "MNT": "₮",
    "MOP": "MOP$",
    "MRU": "UM",
    "MUR": "₨",
    "MVR": "Rf",
    "MWK": "MK",
    "MXN": "$",
    "MXV": "MXV",
    "MYR": "RM",
    "MZN": "MT",
    "NAD": "$",
    "NGN": "₦",
    "NIO": "C$",
    "NOK": "kr",
    "NPR": "₨",
    "NZD": "$",
    "OMR": "﷼",
    "PAB": "B/.",
    "PEN": "S/.",
    "PGK": "K",
    "PHP": "₱",
    "PKR": "₨",
    "PLN": "zł",
    "PYG": "Gs",
    "QAR": "﷼",
    "RON": "lei",
    "RSD": "Дин.",
    "RUB": "₽",
    "RWF": "R₣",
    "SAR": "﷼",
    "SBD": "$",
    "SCR": "₨",
    "SDG": "ج.س.",
    "SEK": "kr",
    "SGD": "$",
    "SHP": "£",
    "SLE": "Le",
    "SLL": "Le",
    "SOS": "S",
    "SRD": "$",
    "SSP": "£",
    "STN": "Db",
    "SVC": "$",
    "SYP": "£",
    "SZL": "E",
    "THB": "฿",
    "TJS": "SM",
    "TMT": "T",
    "TND": "د.ت",
    "TOP": "T$",
    "TRY": "₺",
    "TTD": "TT$",
    "TWD": "NT$",
    "TZS": "TSh",
    "UAH": "₴",
    "UGX": "USh",
    "USD": "$",
    "USN": "USN",
    "UYI": "UYI",
    "UYU": "$U",
    "UYW": "UYW",
    "UZS": "лв",
    "VED": "VED",
    "VES": "BsS",
    "VND": "₫",
    "VUV": "VT",
    "WST": "WS$",
    "XAF": "FCFA",
    "XCD": "$",
    "XDR": "XDR",
    "XOF": "CFA",
    "XPF": "₣",
    "XSU": "XSU",
    "XUA": "XUA",
    "YER": "﷼",
    "ZAR": "R",
    "ZMW": "K",
    "ZWL": "ZWL",
}


def singleton(class_):
    instances = {}

    def get_instance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return get_instance


@singleton
class Config(object):

    def __init__(self):
        etcd_host = os.environ.get('HX_ETCD_HOST')
        etcd_port = int(os.environ.get('HX_ETCD_PORT'))
        self.client = ConfigClient(host=etcd_host, port=etcd_port)

    @property
    def auth_url(self):
        return self.client.auth_url()

    @property
    def keeper_url(self):
        return self.client.keeper_url()

    @property
    def cluster_secret(self):
        return self.client.cluster_secret()

    @property
    def mongo_params(self):
        return self.client.mongo_params()

    @property
    def katara_url(self):
        return self.client.katara_url()

    @property
    def clickhouse_params(self):
        return self.client.clickhouse_params()

    @property
    def arcee_url(self):
        return self.client.arcee_url()


def humanize_storage_size(size, precision=2):
    suffixes = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'ZB', 'YB')
    suff_index = 0
    while size > 1024 and suff_index < len(suffixes):
        suff_index += 1
        size /= 1024.0
    return "%.*f %s" % (precision, size, suffixes[suff_index])


def timestamp_to_date(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


def is_uuid(check_str):
    pattern = '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z'
    return bool(re.match(pattern, str(check_str).lower()))


def datetime_to_timestamp(dt):
    return dt.timestamp() if dt else 0


def check_ipv4_addr(address):
    if not address or not netaddr.valid_ipv4(str(address),
                                             netaddr.core.INET_PTON):
        raise ValueError("%s is not an IPv4 address" % address)


def is_valid_port(value):
    try:
        port = int(value)
    except (ValueError, TypeError):
        return False
    if 1 <= port <= 65535:
        return True
    return False


def _check_is_string(name, value):
    if not isinstance(value, str):
        raise WrongArgumentsException(Err.OE0214, [name])


def check_string(name, value):
    if value is None:
        raise_not_provided_exception(name)
    _check_is_string(name, value)
    if value.isspace():
        raise WrongArgumentsException(Err.OE0416, [name])


def check_string_attribute(name, value, min_length=1, max_length=255):
    check_string(name, value)
    if not min_length <= len(value) <= max_length:
        count = ('max %s' % max_length if min_length == 0
                 else '%s-%s' % (min_length, max_length))
        raise WrongArgumentsException(Err.OE0215, [name, count])


def check_dict_attribute(name, value):
    if not value:
        raise_not_provided_exception(name)
    if not isinstance(value, dict):
        raise WrongArgumentsException(Err.OE0344, [name])


def check_list_attribute(name, value):
    if not value:
        raise_not_provided_exception(name)
    if not isinstance(value, list):
        raise WrongArgumentsException(Err.OE0385, [name])


def check_int_attribute(name, value, min_length=0, max_length=MAX_32_INT):
    if value is None:
        raise_not_provided_exception(name)
    if not isinstance(value, int) or isinstance(value, bool):
        raise WrongArgumentsException(Err.OE0223, [name])
    if not min_length <= value <= max_length:
        raise WrongArgumentsException(
            Err.OE0224, [name, min_length, max_length])


def check_float_attribute(name, value, min_length=0, max_length=MAX_32_INT):
    if value is None:
        raise_not_provided_exception(name)
    if not isinstance(value, float) and not isinstance(value, int):
        raise WrongArgumentsException(Err.OE0466, [name])
    if not min_length <= value <= max_length:
        raise WrongArgumentsException(
            Err.OE0224, [name, min_length, max_length])


def check_bool_attribute(name, value):
    if not isinstance(value, bool):
        raise WrongArgumentsException(Err.OE0226, [name])


def check_ipv4_attribute(name, value):
    if value is None:
        raise_not_provided_exception(name)
    _check_is_string(name, value)
    try:
        check_ipv4_addr(value)
    except ValueError:
        raise WrongArgumentsException(Err.OE0356, [name])


def check_regex_attribute(name, value):
    if value is None:
        raise_not_provided_exception(name)
    _check_is_string(name, value)
    if not any(map(lambda x: x not in {'?', '*'}, value)):
        raise WrongArgumentsException(Err.OE0496, [name])


def is_valid_meta(metadata):
    try:
        meta = json.loads(metadata)
        if not isinstance(meta, dict):
            return False
    except:
        return False
    return True


def is_email_format(check_str):
    regex = '^[a-z0-9!#$%&\'*+/=?`{|}~\^\-\+_()]+(\.[a-z0-9!#$%&\'*+/=?`{|}~\^\-\+_()]+)*' \
            '@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,18})$'
    match = re.match(regex, str(check_str).lower())
    return bool(match)


def get_encryption_key():
    return Config().client.read('/encryption_key').value.encode()


def is_valid_hostname(hostname):
    """http://stackoverflow.com/a/20204811"""
    regex = '(?=^.{1,253}$)(^(((?!-)[a-zA-Z0-9-]{1,63}(?<!-))|((?!-)' \
            '[a-zA-Z0-9-]{1,63}(?<!-)\.)+[a-zA-Z]{2,63})$)'
    match = re.match(regex, str(hostname).lower())
    return bool(match)


def _is_not_allowed_char(char):
    return char not in (ascii_letters + digits) + '_' + '-' + '.'


def is_allowed_name(name):
    not_allowed = list(filter(_is_not_allowed_char, map(lambda c: c, str(name))))
    if not not_allowed and str(name)[0].isalpha():
        return True
    return False


def strtobool(val):
    val = val.lower()
    if val not in ['true', 'false']:
        raise ValueError('Should be false or true')
    return val == 'true'


def check_duplicates(ordered_pairs):
    d = {}
    for k, v in ordered_pairs:
        if k in d:
            raise KeyError(k)
        else:
            d[k] = v
    return d


def raise_invalid_argument_exception(argument):
    raise WrongArgumentsException(Err.OE0217, [argument])


def raise_not_provided_exception(argument):
    raise WrongArgumentsException(Err.OE0216, [argument])


def raise_does_not_exist_exception(type_, argument):
    raise WrongArgumentsException(Err.OE0005, [type_, argument])


def raise_unexpected_exception(unexpected_params):
    message = ', '.join(unexpected_params)
    raise WrongArgumentsException(Err.OE0212, [message])


def validate_key_in_collection(key, collection):
    if key in collection:
        value = collection.get(key)
        if value is None:
            raise_not_provided_exception(key)


class ModelEncoder(json.JSONEncoder):
    # pylint: disable=E0202
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, enum.Enum):
            return obj.value
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, ObjectId):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


def gen_id():
    return str(uuid.uuid4())


def now_timestamp():
    return int(datetime.utcnow().timestamp())


def safe_string(str_, length=20):
    regex = re.compile('[^a-zA-Z0-9 _-]')
    safe_name = regex.sub('', str_)
    return safe_name[:length]


class RetriableException(Exception):
    pass


def should_retry(exception):
    if isinstance(exception, RetriableException):
        return True
    return False


async def run_task(func, *args, **kwargs):
    try:
        res = await func(*args, **kwargs)
    except WrongArgumentsException as ex:
        raise OptHTTPError.from_opt_exception(400, ex)
    except ForbiddenException as ex:
        raise OptHTTPError.from_opt_exception(403, ex)
    except NotFoundException as ex:
        raise OptHTTPError.from_opt_exception(404, ex)
    except ConflictException as ex:
        raise OptHTTPError.from_opt_exception(409, ex)
    except FailedDependency as ex:
        raise OptHTTPError.from_opt_exception(424, ex)
    except CloudAdapterBaseException as ex:
        # TODO: Better handling for cloud exceptions
        raise OptHTTPError(424, Err.OE0433, [str(ex)])
    except TimeoutException as ex:
        raise OptHTTPError.from_opt_exception(503, ex)
    except InternalError as exc:
        if "Deadlock found when trying to get lock" in str(exc):
            LOG.warning('Deadlock found, raising 503: %s', str(exc))
            raise OptHTTPError(503, Err.OE0003, [str(exc)])
        raise
    except DatabaseError as exc:
        if 'Lock wait timeout exceeded' in str(exc):
            LOG.warning('Lock timeout, raising 503 to retry: %s', str(exc))
            raise OptHTTPError(503, Err.OE0003, [str(exc)])
        raise
    except RetriableException as exc:
        LOG.warning('Retry count reached: %s', str(exc))
        raise OptHTTPError(503, Err.OE0003, [str(exc)])
    return res


def bytes_to_gb(num_bytes):
    return num_bytes / GB


def seconds_to_hour(num_seconds):
    return num_seconds / SECONDS_IN_HOUR


def get_http_error_info(exception):
    # TODO: research a better approach for auth (and others) error handling
    try:
        return json.loads(exception.response.text)['error']
    except Exception:
        return {
            'status_code': exception.response.status_code,
            'error_code': Err.OE0435.name,
            'reason': 'Service call error: %s' % str(exception),
            'params': [str(exception)],
        }


def query_url(**query):
    query = {
        key: value for key, value in query.items() if value is not None
    }
    encoded_query = urlencode(query, doseq=True)
    return "?" + encoded_query


def get_nil_uuid():
    return str(uuid.UUID(int=0))


def encode_string(val, decode=False):
    if len(val) == 0:
        return val
    method = base64.b64decode if decode else base64.b64encode
    return method(val.encode('utf-8')).decode('utf-8')


def encoded_tags(tags, decode=False):
    return encoded_map(tags, decode)


def encoded_map(map, decode=False):
    if not map:
        return {}
    new_map = {}
    for k, v in map.items():
        new_key = encode_string(k, decode)
        new_map[new_key] = v
    return new_map


def update_tags(db_value, value, is_report_import=False, decode=True):
    resource_tags = encoded_tags(
        value, decode=True) if decode else value
    db_resource_tags = encoded_tags(
        db_value, decode=True) if decode else db_value
    if db_resource_tags:
        db_update = {db_key: db_value
                     for db_key, db_value in db_resource_tags.items()
                     if db_key not in set(resource_tags.keys()) and (
                             db_key.startswith('aws:') or is_report_import)}
        if db_update:
            resource_tags.update(db_update)
    if decode:
        value = encoded_tags(resource_tags)
    return value


def generate_discovered_cluster_resources_stat(
        newly_discovered_resources, cluster_map, cluster_key='cluster_id'):
    newly_discovered_stat = {}
    for r in newly_discovered_resources:
        cloud_account_id = r['cloud_account_id']
        if not newly_discovered_stat.get(cloud_account_id):
            newly_discovered_stat[cloud_account_id] = {
                'total': 0, 'clusters': set(), 'clustered': 0}
        stat = newly_discovered_stat[cloud_account_id]
        stat['total'] += 1

        cluster = cluster_map.get(r.get(cluster_key))
        if cluster:
            stat['clustered'] += 1
            stat['clusters'].add(r.get('cluster_id'))
    for statistic in list(newly_discovered_stat.values()):
        if 'clusters' in statistic:
            statistic['clusters'] = list(statistic['clusters'])
    return newly_discovered_stat


def _retry_on_mongo_error(exc):
    if isinstance(exc, BulkWriteError):
        # retry if we got error in mongo upsert
        return True
    return False


@retry(retry_on_exception=_retry_on_mongo_error, wait_fixed=2000,
       stop_max_attempt_number=10)
def retry_mongo_upsert(method, *args, **kwargs):
    return method(*args, **kwargs)


def object_to_xlsx(obj):
    with io.BytesIO() as f:
        conv = ExcelConverter()
        conv.convert(obj, ExcelWriter(
            file=f,
            header_formats=(
                ExcelFormats.Bold,
            ),
            column_widths={
                DEFAULT_COLUMN_WIDTH: 30
            },
        ))
        f.seek(0)
        result = f.read()
    return result


def convert_to_safe_filename(name, replace=' ', char_limit=200):
    if not name or not isinstance(name, str):
        return
    # replace spaces
    for r in replace:
        name = name.replace(r, '_')

    # keep only valid ascii chars
    cleaned_filename = unicodedata.normalize('NFKD', name).encode(
        'ASCII', 'ignore').decode()

    # keep only whitelisted chars
    cleaned_filename = ''.join(c for c in cleaned_filename if
                               _is_not_allowed_char(c) is False)
    return cleaned_filename[:char_limit]


def gen_fingerprint(ssh_public_key):
    key = base64.b64decode(ssh_public_key.strip().split()[1].encode('ascii'))
    fp_plain = hashlib.md5(key).hexdigest()
    return ':'.join(a + b for a, b in zip(fp_plain[::2], fp_plain[1::2]))


def get_root_directory_path():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _get_encryption_salt():
    return Config().client.encryption_salt()


def encode_config(config_dict):
    s = _get_encryption_salt()
    return cryptocode.encrypt(
        json.dumps(config_dict), s)


def decode_config(encoded_str):
    s = _get_encryption_salt()
    return json.loads(cryptocode.decrypt(encoded_str, s))


class SupportedFiltersMixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.list_filters = [
            'owner_id', 'pool_id', 'cloud_account_id', 'service_name',
            'region', 'resource_type', 'created_by_kind',
            'created_by_name', 'k8s_namespace', 'k8s_node',
            'k8s_service', 'tag', 'without_tag', 'traffic_from', 'traffic_to', '_id'
        ]
        self.bool_filters = [
            'active', 'recommendations', 'constraint_violated'
        ]
        self.str_filters = [
            'name_like', 'cloud_resource_id_like'
        ]
        self.int_filters = []
