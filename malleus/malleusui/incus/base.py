class IncusBase():

    def __init__(self, client):
        self._client = client

    def await_operation(self, operation_id):
        print("\nWaiting\n")
        self._client.get(f"/1.0/operations/{operation_id}/wait?timeout=-1")