import logging
import os
import configparser
import argparse
import subprocess


LOG = logging.getLogger()
LOG.addHandler(logging.StreamHandler())
LOG.setLevel(logging.DEBUG)


class ConfigTemplate(object):

    connection_string = 'mysql+mysqlconnector://%s:%s@%s/%s'

    def __init__(self):
        self.path = os.path.join(os.path.abspath(os.path.dirname(__file__)))
        self.config = None

    def load(self, path, name='alembic.template'):
        config = configparser.ConfigParser()
        config.read(os.path.join(path, name))
        self.config = config
        return self.config

    def save(self, host, username, password, db, file_name='alembic.ini'):
        config = self.load(self.path)
        config.set(
            'alembic',
            'sqlalchemy.url',
            ConfigTemplate.connection_string % (username, password, host, db))
        with open(os.path.join(self.path, file_name), 'w') as fh:
            config.write(fh)


def execute(cmd, path='..'):
    LOG.debug('Executing command %s', ''.join(cmd))
    myenv = os.environ.copy()
    myenv['PYTHONPATH'] = path
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=myenv)
    out, err = proc.communicate()
    LOG.debug('Command: %s output: %s, retcode: %s', ''.join(cmd), out,
              proc.returncode)


def migrate(args):
    template = ConfigTemplate()
    template.save(args.host, args.username, args.password, args.dbname)
    cmd = ['alembic', 'revision', '--autogenerate', '-m', '"%s"' % args.name]
    execute(cmd)


def apply(args):
    config = ConfigTemplate()
    cmd = ['alembic', '-c', os.path.join(config.path, 'alembic.ini'),
           'upgrade', 'head']
    execute(cmd)


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    migrate_parser = subparsers.add_parser('migrate')
    migrate_parser.add_argument('-H', '--host', help='Database host',
                                required=True)
    migrate_parser.add_argument('-u', '--username', help='Database username',
                                required=True)
    migrate_parser.add_argument('-p', '--password', help='Database password',
                                required=True)
    migrate_parser.add_argument('-d', '--dbname', help='Database name',
                                required=True)
    migrate_parser.add_argument('-n', '--name', help='Migration name',
                                required=True)
    migrate_parser.set_defaults(func=migrate)
    apply_parser = subparsers.add_parser('apply')
    apply_parser.set_defaults(func=apply)
    args = parser.parse_args()
    vals = vars(args)
    if not any(vals.values()):
        parser.error('No arguments provided.')
    else:
        args.func(args)


if __name__ == '__main__':
    main()
