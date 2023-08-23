from collections import defaultdict
from datetime import datetime, timezone, timedelta
from concurrent.futures.thread import ThreadPoolExecutor

from bumiworker.bumiworker.consts import ArchiveReason
from bumiworker.bumiworker.modules.base import ModuleBase, ArchiveBase

from tools.cloud_adapter.cloud import Cloud as CloudAdapter


class InactiveUsersBase(ModuleBase):
    SUPPORTED_CLOUD_TYPES = [
        'aws_cnr'
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unused_datetime = datetime.fromtimestamp(0, tz=timezone.utc)

    def list_users(self, cloud_adapter):
        raise NotImplementedError

    def handle_user(self, user, now, cloud_adapter, days_threshold):
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
            self.SUPPORTED_CLOUD_TYPES, skip_cloud_accounts)

        result = []
        for config in list(cloud_account_map.values()):
            config.update(config.get('config', {}))
            users = self.collect_cloud_info(config, days_threshold)
            result.extend(users)
        return result

    def collect_cloud_info(self, config, days_threshold):
        adapter = CloudAdapter.get_adapter(config)
        now = datetime.now(tz=timezone.utc)

        result = []
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = []
            for user in self.list_users(adapter):
                futures.append(
                    executor.submit(self.handle_user, user=user,
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
    SERVICE_ACCOUNT_USED_DESCRIPTION = 'service account was used'

    @property
    def supported_cloud_types(self):
        return self.SUPPORTED_CLOUD_TYPES

    def collect_info(self, config, days_threshold):
        users = super().collect_cloud_info(config, days_threshold)
        return {self.get_record_key(u): u for u in users}

    def _handle_optimization(self, user_info, optimization):
        raise NotImplementedError

    def _get(self, previous_options, optimizations, cloud_accounts_map,
             **kwargs):
        days_threshold = previous_options['days_threshold']

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
            users_info_map = self.collect_info(
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

    def handle_nebius_user(self, user, now, cloud_adapter, days_threshold):
        service_account_id = user['id']
        folder_id = user['folderId']
        created_at = datetime.strptime(
            user['createdAt'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
        inactive_threshold = self._get_inactive_threshold(days_threshold)
        is_old_user = self._is_outdated(now, created_at, inactive_threshold)
        if not is_old_user:
            return

        result = {'user_id': service_account_id}

        end_date = now
        start_date = now - timedelta(days=100)
        service_account_usage = cloud_adapter.get_service_account_metrics(
            [service_account_id], start_date, end_date, folder_id
        )

        metrics = service_account_usage.get('metrics', [])
        data = []
        for metric in metrics:
            data.extend(metric.get('timeseries', {}).get('int64Values', []))
        if any(x != 0 for x in data):
            result['is_service_account_used'] = True
        return result
