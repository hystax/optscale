import logging
import re
from datetime import datetime, timedelta
from calendar import monthrange

from optscale_client.herald_client.client_v2 import Client as HeraldClient

from sqlalchemy import Enum, true, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import and_, exists
from tools.cloud_adapter.exceptions import (
    InvalidParameterException, ReportConfigurationException,
    CloudSettingNotSupported, BucketNameValidationError,
    BucketPrefixValidationError, ReportNameValidationError,
    CloudConnectionError, S3ConnectionError)
from tools.cloud_adapter.cloud import Cloud as CloudAdapter

from tools.optscale_exceptions.common_exc import (
    WrongArgumentsException, NotFoundException, ForbiddenException,
    ConflictException, TimeoutException, FailedDependency)
from rest_api.rest_api_server.controllers.cloud_resource import CloudResourceController
from rest_api.rest_api_server.controllers.cost_model import (
    CloudBasedCostModelController, SkuBasedCostModelController)
from rest_api.rest_api_server.controllers.base import ClickHouseMixin
from rest_api.rest_api_server.controllers.discovery_info import DiscoveryInfoController
from rest_api.rest_api_server.controllers.employee import EmployeeController
from rest_api.rest_api_server.controllers.expense import (
    ExpenseController,
    ServiceFilteredCloudFormattedExpenseController,
    RegionFilteredCloudFormattedExpenseController,
    ResourceTypeFilteredCloudFormattedExpenseController,
    EmployeeFilteredCloudFormattedExpenseController,
    PoolFilteredCloudFormattedExpenseController,
    NodeFilteredCloudFormattedExpenseController,
    NamespaceFilteredCloudFormattedExpenseController,
    K8sServiceFilteredCloudFormattedExpenseController
)
from rest_api.rest_api_server.controllers.organization import OrganizationController
from rest_api.rest_api_server.controllers.organization_constraint import OrganizationConstraintController
from rest_api.rest_api_server.controllers.pool import PoolController
from rest_api.rest_api_server.controllers.report_import import (
    ExpensesRecalculationScheduleController,
    ReportImportBaseController
)
from rest_api.rest_api_server.controllers.rule import RuleController
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.models import (
    CloudAccount, DiscoveryInfo, Organization, Pool)
from rest_api.rest_api_server.models.enums import CloudTypes, ConditionTypes
from rest_api.rest_api_server.controllers.base import BaseController
from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.utils import (
    check_bool_attribute, check_dict_attribute, check_float_attribute,
    check_int_attribute, check_string, check_string_attribute,
    raise_invalid_argument_exception, raise_not_provided_exception,
    CURRENCY_MAP, encode_config, decode_config)
LOG = logging.getLogger(__name__)


NOTIFY_FIELDS = ["name", "config"]


class CloudAccountController(BaseController, ClickHouseMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._employee_ctrl = None
        self._resource_ctrl = None

    @property
    def employee_ctrl(self):
        if self._employee_ctrl is None:
            self._employee_ctrl = EmployeeController(
                self.session, self._config, self.token)
        return self._employee_ctrl

    def _get_model_type(self):
        return CloudAccount

    @property
    def resource_ctrl(self):
        if not self._resource_ctrl:
            self._resource_ctrl = CloudResourceController(
                self.session, self._config, self.token
            )
        return self._resource_ctrl

    def _check_organization(self, organization_id):
        organization = OrganizationController(
            self.session, self._config, self.token).get(organization_id)
        if organization is None:
            raise NotFoundException(Err.OE0005, [Organization.__name__, organization_id])

    def _validate(self, cloud_acc, is_new=True, **kwargs):
        org_id = kwargs.get('organization_id')
        if org_id:
            self._check_organization(org_id)
        query = self.session.query(exists().where(
            and_(*(cloud_acc.get_uniqueness_filter(is_new)))))
        cloud_acc_exist = query.scalar()
        if cloud_acc_exist:
            raise ConflictException(
                Err.OE0404, [cloud_acc.name, cloud_acc.organization_id])
        if cloud_acc.type == CloudTypes.ENVIRONMENT:
            process_recommendations = kwargs.get('process_recommendations')
            if process_recommendations:
                raise FailedDependency(Err.OE0476, [])

    def handle_config(self, adapter_cls, config, organization=None):
        self.validate_config(adapter_cls, config,
                             {'bucket_prefix': check_string})
        config = adapter_cls.configure_credentials(config)
        adapter = adapter_cls(config)
        org_id = None
        if organization:
            adapter.set_currency(organization.currency)
            org_id = organization.id
        try:
            response = adapter.validate_credentials(org_id=org_id)
        except InvalidParameterException as ex:
            raise ForbiddenException(Err.OE0433, [str(ex)])
        except CloudSettingNotSupported as ex:
            raise WrongArgumentsException(Err.OE0437, [adapter_cls.__name__, str(ex)])
        except CloudConnectionError as ex:
            raise WrongArgumentsException(Err.OE0455, [str(ex)])
        return config, response['account_id'], response['warnings']

    def validate_config(self, adapter_cls, config,
                        except_cloud_acc_name_func=None):

        def validate_part(expected_params, config_part):
            required_field_names = [p.name for p in expected_params
                                    if p.required]
            missing_required = [p for p in required_field_names if p not in config_part]
            if missing_required:
                message = ', '.join(missing_required)
                raise_not_provided_exception(message)

            all_param_names = [p.name for p in expected_params if not p.readonly]
            unexpected_params = [p for p in config_part if p not in all_param_names]
            if unexpected_params:
                raise WrongArgumentsException(Err.OE0212, [unexpected_params])

            for type, func in [(str, check_string_attribute),
                               (int, check_int_attribute),
                               (bool, check_bool_attribute),
                               (dict, check_dict_attribute),
                               (float, check_float_attribute)]:
                params = [
                    p for p in expected_params
                    if p.type == type and (
                        p.name in config_part or p.default is not None)]
                for param in params:
                    param_name = param.name
                    if except_cloud_acc_name_func:
                        if param_name in except_cloud_acc_name_func.keys():
                            cloud_acc_func = except_cloud_acc_name_func[param_name]
                            cloud_acc_func(param_name, config_part[param_name])
                            continue
                    param_value = config_part.get(param_name)
                    if param_value is not None and not param_value and param.default:
                        config_part[param_name] = param.default
                    if param.type == str:
                        func(param_name, config_part.get(param_name),
                             check_length=param.check_len)
                    else:
                        func(param_name, config_part.get(param_name))
                    if param.dependencies is not None:
                        validate_part(param.dependencies, config_part[param_name])

        validate_part(adapter_cls.BILLING_CREDS, config)

    def check_cloud_account_exists(
            self, organization_id, cloud_acc_type, account_id,
            cloud_acc_id=None):
        try:
            cloud_type = Enum(CloudTypes).enum_class(cloud_acc_type)
        except ValueError as ex:
            raise WrongArgumentsException(Err.OE0287, [str(ex)])
        cloud_account_exist = self.session.query(
            exists().where(
                and_(
                    self.model_type.deleted.is_(False),
                    self.model_type.type == cloud_type,
                    self.model_type.account_id == account_id,
                    self.model_type.organization_id == organization_id,
                    self.model_type.id != cloud_acc_id
                )
            )
        ).scalar()
        if cloud_account_exist:
            raise ConflictException(Err.OE0402, [])

    def verify(self, params):
        cloud_acc_type = params.get('type')
        if cloud_acc_type is None:
            raise_not_provided_exception('type')
        adapter_cls = self.get_adapter(cloud_acc_type)
        config = params.get('config', {})
        # TODO: handle validation warnings
        self.handle_config(adapter_cls, config)

    def get_adapter(self, cloud_acc_type):
        try:
            return CloudAdapter.get_adapter_type(cloud_acc_type)
        except ValueError:
            raise WrongArgumentsException(Err.OE0436, [cloud_acc_type])

    def _publish_cloud_acc_activity(self, cloud_account, action, level='INFO',
                                    reason=None):
        meta = {
            'object_name': cloud_account.name,
            'level': level
        }
        if reason:
            meta.update({'reason': reason})
        self.publish_activities_task(
            cloud_account.organization_id, cloud_account.id, 'cloud_account',
            action, meta, 'cloud_account.{action}'.format(action=action),
            add_token=True)

    def _publish_validation_warnings_activities(self, ca_obj, warnings):
        for warning in warnings:
            self._publish_cloud_acc_activity(
                ca_obj, 'cloud_account_warning', level='WARNING',
                reason=warning)

    def send_cloud_account_email(self, cloud_account, action='created'):
        recipient = self._config.optscale_email_recipient()
        if not recipient:
            return
        control_panel_name = self._config.public_ip()
        action_params_map = {
            'created': ('Data source has been connected',
                        'new_cloud_account'),
            'deleted': ('Data source has been deleted',
                        'cloud_account_deleted')
        }
        title, template = action_params_map.get(action, (None, None))
        subject = '[%s] %s' % (control_panel_name, title)

        user_info = self.get_user_info()
        if not user_info:
            LOG.info('skipped %s email, '
                     'because CA created/deleted without token' % template)
            return
        template_params = {
            'texts': {
                'organization': {
                    'id': cloud_account.organization_id,
                    'name': cloud_account.organization.name,
                    'currency_code': CURRENCY_MAP.get(
                        cloud_account.organization.currency, '$')
                },
                'cloud_account_name': cloud_account.name,
                'cloud_account_id': cloud_account.id,
                'cloud_account_type': cloud_account.type.value,
                'user_name': user_info.get('display_name'),
                'user_email': user_info.get('email')
            }
        }
        HeraldClient(
            url=self._config.herald_url(),
            secret=self._config.cluster_secret()
        ).email_send(
            [recipient], subject, template_type=template,
            template_params=template_params)

    def _get_non_linked_org_aws_accounts(self, org_id):
        result = list()
        q = self.session.query(CloudAccount).filter(
            CloudAccount.organization_id == org_id,
            CloudAccount.deleted.is_(False),
            CloudAccount.type == CloudTypes.AWS_CNR,
            CloudAccount.auto_import == true()
        ).all()
        for i in q:
            decoded_config = decode_config(i.config)
            if not decoded_config.get('linked', False):
                result.append(i)
        return result

    def create(self, **kwargs):
        LOG.info('Creating cloud account. Input data: %s', kwargs)
        org_id = kwargs.get('organization_id')
        self._check_organization(org_id)
        root_config = kwargs.pop('root_config', None)

        cloud_acc_type = kwargs.get('type')
        if cloud_acc_type is None:
            raise_not_provided_exception('type')
        adapter_cls = self.get_adapter(cloud_acc_type)
        self.check_create_restrictions(**kwargs)
        raw_config = kwargs.pop('config', {})
        config = raw_config
        if root_config:
            config = root_config
            config.update(raw_config)
        cost_model = config.pop('cost_model', {}) if config else {}
        organization = OrganizationController(
            self.session, self._config, self.token).get(org_id)
        config, account_id, warnings = self.handle_config(
            adapter_cls, config, organization)
        self.check_cloud_account_exists(org_id, cloud_acc_type, account_id)
        kwargs['account_id'] = account_id
        last_import_modified_at = self._configure_last_import_modified_at(
            adapter_cls, config)
        if last_import_modified_at:
            kwargs['last_import_modified_at'] = last_import_modified_at
        ca_obj = CloudAccount(**kwargs)
        self._validate(ca_obj, True, **kwargs)
        if ca_obj.type == CloudTypes.AZURE_TENANT:
            ca_obj.auto_import = False
        configuration_res = self._configure_report(
            adapter_cls, config, organization)
        if isinstance(configuration_res, dict):
            for c in [config, raw_config]:
                c.update(configuration_res['config_updates'])
            warnings.extend(configuration_res['warnings'])
        ca_obj.config = encode_config(raw_config if root_config else config)
        self.session.add(ca_obj)
        c_type_ctrl_map = {
            CloudTypes.KUBERNETES_CNR: CloudBasedCostModelController,
            CloudTypes.DATABRICKS: SkuBasedCostModelController
        }
        ctrl = c_type_ctrl_map.get(ca_obj.type)
        if ctrl:
            ctrl(self.session, self._config).create(
                organization_id=org_id, id=ca_obj.id, value=cost_model)
            ca_obj.cost_model_id = ca_obj.id
        rd_infos = []
        if cloud_acc_type != CloudTypes.ENVIRONMENT.value:
            rd_infos = DiscoveryInfoController(
                self.session, self._config, self.token
            ).initialize_discovery_infos(ca_obj.id, adapter_cls, config)
        try:
            self.session.commit()
            if rd_infos:
                self.session.add_all(rd_infos)
                self.session.commit()
        except IntegrityError as ex:
            raise WrongArgumentsException(Err.OE0003, [str(ex)])
        cloud_account_org_id = ca_obj.organization_id
        parent_pool = ca_obj.organization.pool
        if ca_obj.parent_id:
            default_employee = parent_pool.default_owner
            auth_user_id = default_employee.auth_user_id
        else:
            auth_user_id = self.get_user_id()
            default_employee = self.get_employee(auth_user_id,
                                                 cloud_account_org_id)
        pool_name = self._generate_pool_name(ca_obj)
        cloud_pool = PoolController(self.session, self._config, self.token).create(
            organization_id=cloud_account_org_id, parent_id=parent_pool.id,
            name=pool_name, default_owner_id=default_employee.id)
        rule_name = 'Rule for %s_%s' % (ca_obj.name, int(datetime.utcnow().timestamp()))
        RuleController(self.session, self._config, self.token).create_rule(
            auth_user_id, cloud_pool.organization_id, self.token,
            name=rule_name, owner_id=cloud_pool.default_owner_id,
            pool_id=cloud_pool.id, is_deprioritized=True, conditions=[
                {
                    'type': ConditionTypes.CLOUD_IS.value, 'meta_info': ca_obj.id
                }
            ]
        )
        if ca_obj.auto_import:
            self._schedule_report_import(ca_obj)
        self._publish_validation_warnings_activities(ca_obj, warnings)
        self._publish_cloud_acc_activity(ca_obj, 'cloud_account_created')
        self.send_cloud_account_email(ca_obj, action='created')
        return ca_obj

    def _schedule_report_import(self, ca_obj):
        # schedule report import for this CA immediately
        import_ctrl = ReportImportBaseController(self.session, self._config)
        ids = list()
        linked = False
        if ca_obj.type == CloudTypes.AWS_CNR:
            decoded_config = decode_config(ca_obj.config)
            linked = decoded_config.get('linked', False)
        if linked:
            # trigger import tasks for all non-linked AWS accounts for current org id
            # please see OS-5622
            accounts = self._get_non_linked_org_aws_accounts(
                ca_obj.organization_id)
            for a in accounts:
                ids.append(a.id)
        else:
            ids.append(ca_obj.id)
        for i in ids:
            # set priority 8 according to comments in OS-5602
            import_ctrl.create(i, priority=8)

    def _get_evironment_cloud_account(self, organization_id):
        return self.session.query(CloudAccount).filter(
            and_(
                CloudAccount.deleted.is_(False),
                CloudAccount.organization_id == organization_id,
                CloudAccount.type == CloudTypes.ENVIRONMENT
            )
        ).one_or_none()

    def get_or_create_environment_cloud_account(self, organization_id, no_create=False):
        env_cloud_acc = self._get_evironment_cloud_account(organization_id)
        if env_cloud_acc or no_create:
            return env_cloud_acc
        try:
            env_cloud_acc = self.create(
                type=CloudTypes.ENVIRONMENT.value, name='Environment',
                organization_id=organization_id, process_recommendations=False)
        except (IntegrityError, ConflictException):
            env_cloud_acc = self._get_evironment_cloud_account(organization_id)
        return env_cloud_acc

    def _generate_pool_name(self, ca_obj):
        ca_name = ca_obj.name
        pool_for_cloud = self.session.query(Pool).filter(
            and_(
                Pool.deleted.is_(False),
                Pool.name.startswith(ca_name),
                Pool.organization_id == ca_obj.organization_id
            )
        ).order_by(Pool.created_at.desc()).first()
        if not pool_for_cloud:
            return ca_name
        new_pool_name = pool_for_cloud.name
        pool_for_cloud_name_groups = re.findall(r'[a-zA-Z0-9]+', new_pool_name)
        if pool_for_cloud_name_groups[-1].isdigit():
            number = int(pool_for_cloud_name_groups[-1]) + 1
            pool_name_result = new_pool_name[0:len(new_pool_name) - len(pool_for_cloud_name_groups[-1])]
            return '%s%s' % (pool_name_result, number)
        else:
            return '%s %s' % (new_pool_name, '1')

    @staticmethod
    def _configure_report(adapter_cls, config, organization):
        try:
            adapter = adapter_cls(config)
            adapter.set_currency(organization.currency)
            return adapter.configure_report()
        except (ReportConfigurationException, BucketNameValidationError,
                BucketPrefixValidationError, ReportNameValidationError) as exc:
            raise WrongArgumentsException(Err.OE0371, [str(exc)])
        except InvalidParameterException as ex:
            raise ForbiddenException(Err.OE0433, [str(ex)])
        except (CloudSettingNotSupported, S3ConnectionError) as ex:
            raise WrongArgumentsException(Err.OE0437, [
                adapter_cls.__name__, str(ex)])
        except CloudConnectionError as ex:
            raise TimeoutException(Err.OE0455, [str(ex)])

    def _configure_last_import_modified_at(self, adapter_cls, config):
        adapter = adapter_cls(config)
        return adapter.configure_last_import_modified_at()

    @staticmethod
    def _need_notification(kwargs):
        return bool(set(kwargs.keys()).intersection(set(NOTIFY_FIELDS)))

    def edit(self, item_id, **kwargs):
        LOG.info('Editing cloud account %s. Input: %s', item_id, kwargs)
        self.check_update_restrictions(**kwargs)
        cloud_acc_obj = self.get(item_id)
        self._validate(cloud_acc_obj, False, **kwargs)
        cloud_acc_type = cloud_acc_obj.type.value
        adapter_cls = self.get_adapter(cloud_acc_type)
        warnings = []

        config_changed = False
        c_type_ctrl_map = {
            CloudTypes.KUBERNETES_CNR: CloudBasedCostModelController,
            CloudTypes.DATABRICKS: SkuBasedCostModelController
        }
        cost_model_controller = c_type_ctrl_map.get(
            cloud_acc_obj.type, CloudBasedCostModelController)(
            self.session, self._config)
        old_config = cloud_acc_obj.decoded_config
        config = kwargs.pop('config', {})
        if cloud_acc_obj.parent_id and config:
            raise WrongArgumentsException(Err.OE0211, ['config'])
        organization = OrganizationController(
            self.session, self._config, self.token).get(
            cloud_acc_obj.organization_id)
        if config:
            cost_model = config.pop('cost_model', {})
            if config:
                config, account_id, warnings = self.handle_config(
                    adapter_cls, config, organization)
                self.check_cloud_account_exists(cloud_acc_obj.organization_id,
                                                cloud_acc_type, account_id,
                                                cloud_acc_obj.id)
                # k8s config is always different but must not be changed
                # on update
                if cloud_acc_obj.type != CloudTypes.KUBERNETES_CNR:
                    kwargs['account_id'] = account_id
                kwargs['config'] = encode_config(config)
                config_changed = config != old_config
            if cost_model:
                cost_model_controller.edit(cloud_acc_obj.id, value=cost_model)

        if config_changed and cloud_acc_obj.auto_import:
            configuration_res = self._configure_report(
                adapter_cls, config, organization)
            if isinstance(configuration_res, dict):
                config.update(configuration_res['config_updates'])
                warnings.extend(configuration_res['warnings'])
                kwargs['config'] = encode_config(config)

        last_import_update = self._configure_last_import_modified_at(
            adapter_cls, config)
        if last_import_update:
            last_import_modified_at = last_import_update
            kwargs['last_import_modified_at'] = last_import_modified_at

        if kwargs:
            updated_cloud_account = super().update(item_id, **kwargs)
            self._publish_validation_warnings_activities(updated_cloud_account,
                                                         warnings)
            for import_f in ['last_import_at', 'last_import_modified_at',
                             'last_import_attempt_at', 'last_import_attempt_error']:
                kwargs.pop(import_f, None)
        else:
            updated_cloud_account = cloud_acc_obj

        if kwargs and self._need_notification(kwargs):
            self._publish_cloud_acc_activity(
                updated_cloud_account, 'cloud_account_updated')
        return updated_cloud_account

    def clean_clickhouse(self, cloud_account_id, cloud_type):
        self.execute_clickhouse(
            """ALTER TABLE traffic_expenses DELETE
               WHERE cloud_account_id=%(cloud_account_id)s""",
            params={'cloud_account_id': cloud_account_id}
        )
        self.execute_clickhouse(
            """ALTER TABLE average_metrics DELETE
               WHERE cloud_account_id=%(cloud_account_id)s""",
            params={'cloud_account_id': cloud_account_id}
        )
        if cloud_type == CloudTypes.KUBERNETES_CNR:
            self.execute_clickhouse(
                """ALTER TABLE k8s_metrics DELETE
                   WHERE cloud_account_id=%(cloud_account_id)s""",
                params={'cloud_account_id': cloud_account_id}
            )
        elif cloud_type == CloudTypes.AWS_CNR:
            self.execute_clickhouse(
                """ALTER TABLE risp.ri_sp_usage DELETE
                   WHERE cloud_account_id=%(cloud_account_id)s""",
                params={'cloud_account_id': cloud_account_id}
            )
            self.execute_clickhouse(
                """ALTER TABLE risp.uncovered_usage DELETE
                   WHERE cloud_account_id=%(cloud_account_id)s""",
                params={'cloud_account_id': cloud_account_id}
            )

    def delete(self, item_id):
        cloud_account = self.get(item_id)
        self.delete_children_accounts(cloud_account)
        c_type_ctrl_map = {
            CloudTypes.KUBERNETES_CNR: CloudBasedCostModelController,
            CloudTypes.DATABRICKS: SkuBasedCostModelController
        }
        if cloud_account.type in c_type_ctrl_map:
            c_type_ctrl_map[cloud_account.type](
                self.session, self._config).delete(item_id)
        elif cloud_account.type == CloudTypes.ENVIRONMENT:
            raise FailedDependency(Err.OE0477, [])
        super().delete(item_id)
        expense_ctrl = ExpenseController(self._config)
        expense_ctrl.delete_cloud_expenses(item_id)
        resource_ctrl = CloudResourceController(self._config)
        resource_ctrl.delete_cloud_resources(item_id)
        self.clean_clickhouse(cloud_account.id, cloud_account.type)
        OrganizationConstraintController(
            self.session, self._config, self.token).delete_constraints_with_hits(
            cloud_account.organization_id,
            filters={'cloud_account_id': item_id})
        self._publish_cloud_acc_activity(
            cloud_account, 'cloud_account_deleted')
        if not cloud_account.organization.is_demo:
            self.send_cloud_account_email(cloud_account, action='deleted')

    def get_details(self, cloud_acc_id):
        today = datetime.utcnow()
        expense_ctrl = ExpenseController(self._config)
        default = {'cost': 0, 'count': 0, 'types': []}
        month_expenses = self._get_this_month_expenses(
            expense_ctrl, today, [cloud_acc_id]
        ).get(cloud_acc_id, default)
        last_month_total = self._get_last_month_expenses(
            expense_ctrl, today, [cloud_acc_id]
        ).get(cloud_acc_id, default)
        discovery_infos = self._get_discovery_infos([cloud_acc_id])
        first_expenses = expense_ctrl.get_first_expenses_for_forecast(
            'cloud_account_id', [cloud_acc_id])
        details = {
            'last_month_cost': last_month_total['cost'],
            'cost': month_expenses['cost'],
            'forecast': expense_ctrl.get_monthly_forecast(
                last_month_total['cost'] + month_expenses['cost'],
                month_expenses['cost'], first_expenses.get(cloud_acc_id)),
            'resources': month_expenses['count'],
            'discovery_infos': discovery_infos.get(cloud_acc_id, [])
        }
        return details

    def _get_discovery_infos(self, cloud_acc_ids):
        discovery_infos = self.session.query(DiscoveryInfo).filter(
            and_(DiscoveryInfo.cloud_account_id.in_(cloud_acc_ids),
                 DiscoveryInfo.deleted.is_(False))).all()
        discovery_info_map = {}
        for discovery_info in discovery_infos:
            cloud_acc_id = discovery_info.cloud_account_id
            if not discovery_info_map.get(cloud_acc_id):
                discovery_info_map[cloud_acc_id] = []
            discovery_info_map[cloud_acc_id].append(discovery_info.to_dict())
        return discovery_info_map

    def get_expenses(self, cloud_acc, start_date, end_date, filter_by):
        controller_map = {
            'service': ServiceFilteredCloudFormattedExpenseController,
            'region': RegionFilteredCloudFormattedExpenseController,
            'resource_type': ResourceTypeFilteredCloudFormattedExpenseController,
            'pool': PoolFilteredCloudFormattedExpenseController,
            'employee': EmployeeFilteredCloudFormattedExpenseController,
            'k8s_node': NodeFilteredCloudFormattedExpenseController,
            'k8s_namespace': NamespaceFilteredCloudFormattedExpenseController,
            'k8s_service': K8sServiceFilteredCloudFormattedExpenseController
        }
        controller = controller_map.get(filter_by)(self.session, self._config)
        return controller.get_formatted_expenses(
            cloud_acc, start_date, end_date)

    @staticmethod
    def _get_cloud_expenses(expense_ctrl, start, end, cloud_acc_ids):
        expenses = expense_ctrl.get_cloud_expenses_with_resource_info(
            cloud_acc_list=cloud_acc_ids,
            start_date=start,
            end_date=end
        )
        return {
            x[0]: {
                'cost': x[1],
                'count': x[2]
            } for x in expenses
        }

    @staticmethod
    def _get_this_month_expenses(expense_ctrl, today_date, cloud_acc_ids):
        start = today_date.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0)
        _, days_in_month = monthrange(today_date.year, today_date.month)
        end = today_date.replace(hour=23, minute=59, second=59, microsecond=0)
        return CloudAccountController._get_cloud_expenses(
            expense_ctrl, start, end, cloud_acc_ids)

    @staticmethod
    def _get_last_month_expenses(expense_ctrl, today_date, cloud_acc_ids):
        end = today_date.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0)

        last_day_in_month = end - timedelta(days=1)
        start = last_day_in_month.replace(day=1)
        return CloudAccountController._get_cloud_expenses(
            expense_ctrl, start, end, cloud_acc_ids)

    def list(self, details=False, secure=True, only_linked=None, type=None,
             **kwargs):
        organization_id = kwargs.get('organization_id')
        if organization_id:
            self._check_organization(kwargs['organization_id'])
        query = self.session.query(CloudAccount).filter(
            CloudAccount.deleted.is_(False),
        )

        if type is not None:
            try:
                type = CloudTypes(type)
                query = query.filter(CloudAccount.type == type)
            except ValueError:
                raise_invalid_argument_exception('type')

        if len(kwargs) > 0:
            query = query.filter_by(**kwargs)

        cloud_accounts = query.all()

        if only_linked:
            linked_accounts = []
            for ca in cloud_accounts:
                if ca.decoded_config.get('linked'):
                    linked_accounts.append(ca)
            cloud_accounts = linked_accounts

        if not details:
            return list(map(lambda x: x.to_dict(secure), cloud_accounts))

        cloud_acc_ids = [x.id for x in cloud_accounts]

        today = datetime.utcnow()
        expense_ctrl = ExpenseController(self._config)
        month_expenses = self._get_this_month_expenses(
            expense_ctrl, today, cloud_acc_ids
        ) if cloud_acc_ids else {}
        last_month_expenses = self._get_last_month_expenses(
            expense_ctrl, today, cloud_acc_ids
        ) if cloud_acc_ids else {}
        first_expenses = expense_ctrl.get_first_expenses_for_forecast(
            'cloud_account_id', cloud_acc_ids)

        result = {}
        discovery_infos = self._get_discovery_infos(cloud_acc_ids)
        for acc in cloud_accounts:
            default = {'cost': 0, 'count': 0}
            current_stats = month_expenses.get(acc.id, default)
            last_stats = last_month_expenses.get(acc.id, default)
            result[acc.id] = acc.to_dict(secure)
            result[acc.id]['details'] = {
                'cost': current_stats['cost'],
                'forecast': expense_ctrl.get_monthly_forecast(
                    last_stats['cost'] + current_stats['cost'],
                    current_stats['cost'], first_expenses.get(acc.id)),
                'tracked': current_stats['count'],
                'last_month_cost': last_stats['cost'],
                'discovery_infos': discovery_infos.get(acc.id, {})
            }
        return list(result.values())

    def get_employee(self, user_id, org_id):
        return self.employee_ctrl.get_employee_by_user_and_organization(
            user_id, org_id)

    def get(self, item_id, **kwargs):
        cloud_account = super().get(item_id, **kwargs)
        if cloud_account:
            self._check_organization(cloud_account.organization_id)
        return cloud_account

    def create_children_accounts(self, root_account):
        cloud_acc_type = root_account.type.value
        root_config = root_account.decoded_config
        adapter_cls = self.get_adapter(cloud_acc_type)
        adapter = adapter_cls(root_config)
        configs = adapter.get_children_configs()
        if not configs:
            return
        root_skipped_subscriptions = root_config.pop('skipped_subscriptions', {})
        skipped_subscriptions = root_skipped_subscriptions.copy()
        for c_config in configs:
            c_name = c_config.get('name')
            try:
                self.create(
                    organization_id=root_account.organization_id,
                    parent_id=root_account.id, root_config=root_config.copy(),
                    **c_config)
                if c_name in skipped_subscriptions:
                    skipped_subscriptions.pop(c_name, None)
            except Exception as ex:
                if c_name not in skipped_subscriptions:
                    # Add error reason to root config
                    # Send event only on first time error
                    error_message = 'Unable to create child account %s: %s' % (
                        c_name, str(ex))
                    LOG.info(error_message)
                    self._publish_cloud_acc_activity(
                        root_account, 'cloud_account_warning', level='ERROR',
                        reason=error_message)
                    skipped_subscriptions[c_name] = str(ex)
        if skipped_subscriptions.keys() != root_skipped_subscriptions.keys():
            root_config['skipped_subscriptions'] = skipped_subscriptions
            self.edit(root_account.id, config=root_config)

    def delete_children_accounts(self, root_account):
        children = self.session.query(CloudAccount).filter(
            CloudAccount.organization_id == root_account.organization_id,
            CloudAccount.deleted.is_(False),
            CloudAccount.parent_id == root_account.id
        ).all()
        for c in children:
            self.delete(c.id)


class CloudAccountAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return CloudAccountController
