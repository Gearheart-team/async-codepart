from .methods import publish


class RPCCallAnnouncer(object):
    """Publishes result or pregress messages about RPC call"""

    def __init__(self, callee_uuid, *args, **kwargs):
        self.uuid = callee_uuid

    def progress(self, message):
        publish(self.uuid, {'complete': False, 'message': message})

    def result(self, message):
        publish(self.uuid, {'complete': True, 'message': message})
