from django.apps import apps
from importlib import import_module


def get_request_params(name, request=None, **kwargs):
    """Returns requested argument value"""
    args = {'app_name': 1, 'modal_name': 2, 'pk': 4}
    try:
        return kwargs.get(
            name, request.path.split('/')[args[name] if request else None]
        )
    except IndexError:
        pass


def get_model(**kwargs):
    """Returns model name"""
    args = [get_request_params(
        key, **kwargs) for key in ('app_name', 'model_name')]

    return apps.get_model(*args)


def get_model_instance(**kwargs):
    """
    Returns model instance based on primary key
    """
    return get_model(**kwargs).objects.get(id=kwargs.get("pk"))


def flow_config(module):
    """
    Returns flow configuration
    Importing process file from respective app
    """
    return import_module('{}.process'.format(apps.get_app_config(module).name))


def transition_config(module, activity):
    """Return all the possible steps for a process"""
    return flow_config(module).PROCESS[activity]['transitions']

