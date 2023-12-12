import glob
from os import pathsep, environ
from os.path import dirname, basename, isfile, join


def create_report(module_name, organization_id, report_data, config_client):
    if not module_name:
        return
    modules = glob.glob(join(dirname(__file__), "*.py"))
    modules = [basename(f)[:-3] for f in modules
               if isfile(f) and not f.endswith('__init__.py')]
    pythonpath = environ['PYTHONPATH'].split(pathsep)[0]
    import_base = dirname(__file__)[len(pythonpath):]
    import_base = import_base.replace('/', '.')
    module = __import__(f'{import_base}.{module_name}',
                        globals(), locals(), modules, 0)
    # main function is entrypoint so each module MUST have it
    return module.main(
        organization_id=organization_id, report_data=report_data,
        config_client=config_client)
