# coding=utf-8
import logging

from .dispatcher import dispatcher
from .auth import rest_token_request_parameter

logger = logging.getLogger(__name__)


# Connected to websocket.connect
@rest_token_request_parameter
def ws_connect(message):
    dispatcher.connect(message)
    message.reply_channel.send({"accept": True})
    logger.info(
        'User {0} connected'.format(
            message.user.username
        )
    )


@rest_token_request_parameter
def ws_message(message):
    dispatcher.dispatch(message)


@rest_token_request_parameter
def ws_disconnect(message):
    dispatcher.disconnect(message)
    logger.info(
        'User {0} diconnected'.format(
            message.user.username
        )
    )
