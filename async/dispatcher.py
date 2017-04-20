import json
import logging

from django.conf import settings

import redis

from channels import Group

from .constants import (
    ACTION_TYPES, USER_SUBS_POOL_PREFIX, ONLINE_USER_KEY,
    CALL
)

logger = logging.getLogger(__name__)


class MessageDispatchException(Exception):
    pass


class MessageDispatcher(object):
    """Websocket dispatcher.
       Manages connections, messages and rpc calls"""

    def __init__(self, *args, **kwargs):
        self._registry = {}
        self.redis = redis.StrictRedis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            charset="utf-8",
            decode_responses=True
        )

    def get_user_pool_key(self, message):
        """Returns user pool key based on
           websoket channel name and user id"""
        return '{uid}_{reply}'.format(
            uid=message.user.id,
            reply=message.reply_channel.name.split('!')[1]
        )

    def get_user_group(self, message):
        """Returns django-channels group for user"""
        return Group(self.get_user_pool_key(message))

    def connect(self, message):
        """Adds user django-channels group and redis key
           for define this user as online"""
        self.get_user_group(message).add(message.reply_channel)
        self.redis.lpush(ONLINE_USER_KEY, self.get_user_pool_key(message))

    def disconnect(self, message):
        """Discards user django-channels group and
           removes redis key for define this user as offline"""
        self.get_user_group(message).discard(message.reply_channel)
        self.redis.lrem(
            ONLINE_USER_KEY, 1,
            self.get_user_pool_key(message))
        self.redis.delete(
            USER_SUBS_POOL_PREFIX + self.get_user_pool_key(message))

    def register(self, endpoint, func):
        """Register rpc endpoint"""
        self._registry[endpoint] = func

    def dispatch(self, message):
        """Dispatch websocket message to needed action"""
        from . import methods
        logger.debug("dispatch message {}".format(message.items()))
        parsed = json.loads(message.content['text'])
        action = parsed.pop('action')
        endpoint = parsed.pop('endpoint')
        if not action or action not in ACTION_TYPES:
            raise MessageDispatchException('Unknown Action')
        method = getattr(methods, action, None)
        args = parsed.pop('args', [])
        kwargs = parsed.pop('kwargs', {})
        kwargs['user_pool_key'] = self.get_user_pool_key(message)
        if action == CALL:
            kwargs['callee_uuid'] = parsed.get('callee_uuid')
        method(endpoint, *args, **kwargs)


dispatcher = MessageDispatcher()
