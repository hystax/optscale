from collections import defaultdict
from datetime import datetime, timezone, timedelta
from concurrent.futures.thread import ThreadPoolExecutor

from bumi_worker.consts import ArchiveReason
from bumi_worker.modules.base import ModuleBase, ArchiveBase

from cloud_adapter.cloud import Cloud as CloudAdapter


SUPPORTED_CLOUD_TYPES = [
    'aws_cnr'
]


class InactiveUsersBase(ModuleBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unused_datetime = datetime.fromtimestamp(0, tz=timezone.utc)

    def handle_aws_user(self, user, now, cloud_adapter, days_threshold):
        raise NotImplementedError

    @property
    def is_resource_based(self):
        return False

    @property
    def unique_record_keys(self):
        return 'cloud_account_id', 'user_id',

    def _get_inactive_threshold(self, days_threshold):
        return timedelta(days=days_threshold)

    def _get_inactive_keys_threshold(self, days_threshold):
        return timedelta(days=days_threshold)

    @staticmethod
    def _is_outdated(now, last_used, inactive_threshold):
        return now - last_used > inactive_threshold

    def _get_password_last_used(self, user):
        last_password_used = user.get(
            'PasswordLastUsed', self.unused_datetime)
        return last_password_used

    def _get_access_keys_last_used(self, user, cloud_adapter):
        keys_last_used = self.unused_datetime
        for key in cloud_adapter.list_access_keys(user['UserName']):
            if key['Status'] == 'Active':
                usage_info = cloud_adapter.get_access_key_usage_info(
                    key['AccessKeyId'])
                access_key_used = usage_info.get('LastUsedDate',
                                                 self.unused_datetime)
                if access_key_used > keys_last_used:
                    keys_last_used = access_key_used
        return keys_last_used

    def _get(self):
        days_threshold, skip_cloud_accounts = self.get_options_values()
        cloud_account_map = self.get_cloud_accounts(
            SUPPORTED_CLOUD_TYPES, skip_cloud_accounts)

        result = []
        for config in list(cloud_account_map.values()):
            config.update(config.get('config', {}))
            users = self.collect_aws_info(config, days_threshold)
            result.extend(users)
        return result

    def collect_aws_info(self, config, days_threshold):
        adapter = CloudAdapter.get_adapter(config)
        now = datetime.now(tz=timezone.utc)

        result = []
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = []
            for user in adapter.list_users():
                futures.append(
                    executor.submit(self.handle_aws_user, user=user,
                                    now=now, cloud_adapter=adapter,
                                    days_threshold=days_threshold))

            for f in futures:
                res = f.result()
                if res:
                    result.append({
                        'cloud_account_id': config['id'],
                        'cloud_type': config['type'],
                        **res
                    })
        return result


class ArchiveInactiveUsersBase(ArchiveBase, InactiveUsersBase):
    PASSWORD_USED_DESCRIPTION = 'password was used'
    ACCESS_KEY_USED_DESCRIPTION = 'access key was used'

    def collect_aws_info(self, config, days_threshold):
        users = super().collect_aws_info(config, days_threshold)
        return {self.get_record_key(u): u for u in users}

    def _handle_optimization(self, user_info, optimization):
        raise NotImplementedError

    def _get(self, previous_options, optimizations, **kwargs):
        days_threshold = previous_options['days_threshold']
        skip_cloud_accounts = previous_options['skip_cloud_accounts']

        cloud_accounts_map = self.get_cloud_accounts(
            SUPPORTED_CLOUD_TYPES, skip_cloud_accounts)

        account_optimizations_map = defaultdict(list)
        for optimization in optimizations:
            account_optimizations_map[optimization['cloud_account_id']].append(
                optimization)

        result = []
        for cloud_account_id, optimizations_ in account_optimizations_map.items():
            if cloud_account_id not in cloud_accounts_map:
                for optimization in optimizations_:
                    self._set_reason_properties(
                        optimization, ArchiveReason.CLOUD_ACCOUNT_DELETED)
                    result.append(optimization)
                continue

            cloud_account = cloud_accounts_map[cloud_account_id]
            cloud_account.update(cloud_account.get('config', {}))
            users_info_map = self.collect_aws_info(
                cloud_account, days_threshold)

            for optimization in optimizations_:
                user_key = self.get_record_key(optimization)
                user_info = users_info_map.get(user_key)
                optimization = self._handle_optimization(
                    user_info, optimization)
                result.append(optimization)
        return result

    def handle_aws_user(self, user, now, cloud_adapter, days_threshold):
        inactive_threshold = self._get_inactive_threshold(days_threshold)
        inactive_access_keys_threshold = self._get_inactive_keys_threshold(
            days_threshold)

        def is_outdated(last_used_, inactive_threshold_):
            return self._is_outdated(now, last_used_, inactive_threshold_)

        is_old_user = is_outdated(
            user.get('CreateDate', now), inactive_threshold)
        if not is_old_user:
            return

        result = {'user_id': user['UserId']}

        password_last_used = self._get_password_last_used(user)
        is_password_used = not is_outdated(
            password_last_used, inactive_threshold)
        result['is_password_used'] = is_password_used
        if is_password_used:
            return result

        access_keys_last_used = self._get_access_keys_last_used(
            user, cloud_adapter)
        is_access_keys_used = not is_outdated(
            access_keys_last_used, inactive_access_keys_threshold)
        result['is_access_keys_used'] = is_access_keys_used
        return result
