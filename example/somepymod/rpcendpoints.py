import logging

from async.decorators import register
from .models import SomeModel


logger = logging.getLogger(__name__)


@register('com.example.heavy')
def heavy(announcer, *args, **kwargs):
    model_id = kwargs.get('model_id')
    logger.debug(
        "Handle heavy call for model {}".format(
            model_id))
    somemodel = SomeModel.objects.get(id=model_id)
    announcer.progress('Start heavy method')
    result = somemodel.some_heavy_method()
    announcer.result(result)
