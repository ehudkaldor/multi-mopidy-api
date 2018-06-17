import logging

class Group:
    _log = logging.getLogger("Group")

    def __init__(self, api, group):
        self._log.debug(f"creating group: {group}")
