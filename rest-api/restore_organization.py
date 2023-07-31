import argparse
import logging
import os
import uuid
import config_client.client
from datetime import datetime
from rest_api_server.controllers.register import RegisterController
from rest_api_server.controllers.employee import EmployeeController
from rest_api_server.controllers.live_demo import LiveDemoController
from rest_api_server.models.db_base import BaseDB
from rest_api_server.models.db_factory import DBType, DBFactory

SERVICE_EMAIL_TEMPLATE = 'recover_%s@hystax.com'
SERVICE_USER_NAME_TEMPLATE = 'Bot_%s'
DEFAULT_ETCD_HOST = 'etcd'
DEFAULT_ETCD_PORT = 80


class RestoreOrganization(LiveDemoController):
    def __init__(self, db_session, config, password, org_name, path):
        super().__init__(db_session, config)
        self.password = password
        self.path = path
        self.organization_name = org_name
        self._object_group_duplicated_func_map = {}

    @property
    def multiplier(self):
        return 1

    def create_auth_user(self, email, password, name):
        _, response = self.auth_client.user_exists(email, user_info=True)
        if response['exists']:
            _, auth_user = self.auth_client.user_get(
                response['user_info']['id'])
        else:
            auth_user = super().create_auth_user(email, password, name)
        return auth_user

    def _get_auth_user_params(self, auth_user_data):
        email = auth_user_data['user_email']
        name = auth_user_data['user_display_name']
        password = auth_user_data.get('password') or self.password
        return email, name, password

    def restore_organization(self):
        now = int(datetime.utcnow().timestamp())
        email = SERVICE_EMAIL_TEMPLATE % now
        name = SERVICE_USER_NAME_TEMPLATE % now
        auth_user = self.create_auth_user(email, str(uuid.uuid4()), name)
        organization, employee = RegisterController(
            self.session, self._config, self.token).add_organization(
            self.organization_name, auth_user)
        preset = self.load_preset(self.path)
        employee_id_to_replace = self.get_replacement_employee(preset)
        self.fill_organization(
            organization, employee_id_to_replace, employee.id, preset)
        EmployeeController(
            self.session, self._config, self.token
        ).delete(employee.id, reassign_resources=False)


def main():
    log_format = '%(asctime)-15s %(message)s'
    logging.basicConfig(format=log_format, level=logging.INFO)
    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = int(os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT))
    parser = argparse.ArgumentParser()
    req_args = ['organization_name', 'default_password', 'path']
    for k in req_args:
        parser.add_argument('--%s' % k, type=str)
    args = parser.parse_args()
    for k in req_args:
        if not getattr(args, k):
            raise Exception('--%s is not provided' % k)
    config_cl = config_client.client.Client(host=etcd_host, port=etcd_port)
    db = DBFactory(DBType.MySQL, config_cl).db
    session = BaseDB.session(db.engine)()
    restore_controller = RestoreOrganization(
        db_session=session,
        config=config_cl,
        password=args.default_password,
        org_name=args.organization_name,
        path=args.path
    )
    try:
        restore_controller.restore_organization()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
