def register(endpoint):
    """
    Registers the given rpc endpoint
    """
    from async.dispatcher import dispatcher

    def _endpoint_wrapper(func):
        if not endpoint:
            raise ValueError('Endpoint must be passed to register.')

        dispatcher.register(endpoint, func)

        return func
    return _endpoint_wrapper
