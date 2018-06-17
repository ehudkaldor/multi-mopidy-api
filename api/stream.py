import logging

class Stream:
    _log = logging.getLogger("Stream")

    def __init__(self, stream):
        self._log.debug(f"creating stream: {stream}")
