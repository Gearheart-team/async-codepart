import logging
from channels import Group

from .dispatcher import dispatcher
from .constants import USER_SUBS_POOL_PREFIX
from .message_utils import UTFJSONRenderer

logger = logging.getLogger(__name__)


def subscribe(endpoint, *args, **kwargs):
    """User subscribes websocket endpoint"""
    logger.debug("Handle subscribe method for {} endpoint".format(endpoint))
    sub_key = USER_SUBS_POOL_PREFIX + kwargs.get('user_pool_key')
    dispatcher.redis.rpush(sub_key, endpoint)


def unsubscribe(endpoint, *args, **kwargs):
    """User unsubscribes websocket endpoint"""
    logger.debug("Handle unsubscribe method for {} endpoint".format(endpoint))
    sub_key = USER_SUBS_POOL_PREFIX + kwargs.get('user_pool_key')
    dispatcher.redis.lrem(sub_key, 0, endpoint)


def publish(endpoint, message, **kwargs):
    """Publish something to websocket endpoint"""
    logger.debug("Handle publish method for {} endpoint".format(endpoint))
    target_pools = set()
    if not isinstance(message, str):
        message['endpoint'] = endpoint
        message = UTFJSONRenderer().render(message).decode('utf-8')
    else:
        message = UTFJSONRenderer().render({
            'endpoint': endpoint,
            'message': message
        }).decode('utf-8')
    user_pools = dispatcher.redis.keys('%s*' % USER_SUBS_POOL_PREFIX)
    for pool in user_pools:
        user_pool = pool.split(USER_SUBS_POOL_PREFIX)[1]
        if endpoint in dispatcher.redis.lrange(pool, 0, -1):
            target_pools.add(user_pool)
    for group_name in target_pools:
        Group(group_name).send({'text': message})


def call(endpoint, *args, **kwargs):
    """Call RPC endpoint"""
    from .rpc_utils import RPCCallAnnouncer
    logger.debug("Handle call method for {} endpoint".format(endpoint))
    func = dispatcher._registry.get(endpoint)
    if not func:
        raise Exception(
            "There are no registered endpoint {}".format(endpoint))
    callee_uuid = kwargs.pop('callee_uuid')
    announcer = RPCCallAnnouncer(callee_uuid)
    func(announcer, *args, **kwargs)
