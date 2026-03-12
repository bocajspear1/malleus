import logging

logger = logging.getLogger('IncusBase')


class IncusBase():

    def __init__(self, client):
        self._client = client

    def await_operation(self, operation_id):
        logger.info("Waiting for operation %s", operation_id)
        self._client.get(f"/1.0/operations/{operation_id}/wait?timeout=-1")