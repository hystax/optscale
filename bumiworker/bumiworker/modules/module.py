import glob
from os import pathsep, environ
from os.path import dirname, basename, isfile, join


class UnknownModuleException(Exception):
    pass


def list_modules(folder_name):
    modules = glob.glob(join(dirname(__file__), folder_name, "*.py"))
    return [basename(f)[:-3] for f in modules
            if isfile(f) and not f.endswith('__init__.py')]


def import_module(module_name, module_type):
    if not module_name:
        return
    pythonpath = environ['PYTHONPATH'].split(pathsep)[0]
    modules = list_modules(module_type)
    if module_name not in modules:
        raise UnknownModuleException(
            'Module %s is unknown in %s scope' % (module_name, module_type))
    import_base = dirname(__file__)[len(pythonpath):]
    import_base = import_base.replace('/', '.')
    return __import__('%s.%s.%s' % (import_base, module_type, module_name),
                      globals(), locals(), modules, 0)


def call_module(module_name, module_type, organization_id, config_client,
                created_at, **kwargs):
    module = import_module(module_name, module_type)
    # main function is entrypoint so each module MUST have it
    return module.main(
        organization_id=organization_id, config_client=config_client,
        created_at=created_at, **kwargs)


def get_email_module_name(module_name):
    module = import_module(module_name, module_type='recommendations')
    return module.get_module_email_name()
