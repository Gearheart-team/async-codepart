import logging

from functools import wraps
from channels.handler import AsgiRequest
from channels.sessions import channel_session

logger = logging.getLogger(__name__)

def authenticate(key):
    from django.contrib.auth.models import AnonymousUser
    from rest_framework.authtoken.models import Token
    try:
        token = Token.objects.select_related('user').get(key=key)
    except Token.DoesNotExist:
        return AnonymousUser()

    if not token.user.is_active:
        return AnonymousUser()

    return token.user


def _close_reply_channel(message):
    message.reply_channel.send({'close': True})


def rest_token_request_parameter(func):
    """
    Checks the presence of a "token" request parameter and tries to
    authenticate the user based on its content.
    """
    @channel_session
    @wraps(func)
    def inner(message, *args, **kwargs):
        # If we didn't get a session, then we don't get a user
        if not hasattr(message, "channel_session"):
            raise ValueError("Did not see a channel session to get auth from")
        if message.channel_session is None:
            # Inner import to avoid reaching into models before load complete
            from django.contrib.auth.models import AnonymousUser
            message.user = AnonymousUser()
            return func(message, *args, **kwargs)
        if message.channel_session.get('user'):
            message.user = message.channel_session['user']
            message.token = message.channel_session['token']
            return func(message, *args, **kwargs)

        # Taken from channels.session.http_session
        try:
            if "method" not in message.content:
                message.content['method'] = "FAKE"
            request = AsgiRequest(message)
        except Exception as e:
            raise ValueError("Cannot parse HTTP message - are you sure this is a HTTP consumer? %s" % e)

        token = request.GET.get("token", None)
        if token is None:
            logger.error("Missing token request parameter. Closing channel.")
            _close_reply_channel(message)
            raise ValueError("Missing token request parameter. Closing channel.")
        user = authenticate(token)
        message.channel_session['token'] = message.token = token
        message.channel_session['user'] = message.user = user
        return func(message, *args, **kwargs)
    return inner
