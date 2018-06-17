import logging

class Client:
    _log = logging.getLogger("Client")

    def __init__(self, api, client):
        self._log.debug(f"creating client: {client}")
