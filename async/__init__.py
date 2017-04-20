from django.utils.module_loading import autodiscover_modules
from async.dispatcher import dispatcher

default_app_config = 'async.apps.AsyncConfig'


def autodiscover():
    autodiscover_modules('rpcendpoints', register_to=dispatcher)
