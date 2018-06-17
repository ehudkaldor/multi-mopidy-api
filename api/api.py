import logging
import configparser
import asyncio
from .protocol import Protocol
from .group import Group
from .client import Client
from .stream import Stream


class API:
    _log = logging.getLogger("API")

    _clients = {}
    _streams = {}
    _groups = {}
    _version = None

    def __init__(self, host, port, methods, callbacks, loop):
        self._log.debug(f"initializing API to: {host}:{port}")
        self._loop = loop
        self._host = host
        self._port = port
        self._methods = methods
        self._protocol = Protocol(host, port, callbacks, loop)
        self._log.debug(f"API init completed. methods: {self._methods}")

    async def start(self):
        """Initiate server connection."""
        await self._do_connect()
        self._log.info('connected to snapserver on %s:%s', self._host, self._port)
        status = await self.getStatus()
        self.parseStatus(status)
        # self.synchronize(status)
        # self._on_server_connect()

    async def _do_connect(self):
        conn = await self._loop.create_connection(lambda: self._protocol, self._host, self._port)
        # self._loop.run_until_complete(factory)
        self._log.debug(f'after creating connection {conn}')
        try:
            # self._loop.run_forever()
            self._log.debug('after waiting on run_forever')
        except Exception as e:
            self._log.debug(f'exception detected: {e}')
        except KeyboardInterrupt:
            self._log.debug('keyboard interrupt detected')
        finally:
            pass

    def _transact(self, method, params=None):
        """Wrap requests."""
        self._log.debug(f'sending request to server: {method}')
        result = self._protocol.request(method, params)
        return result

        # async self._protocol.connect()

    async def getStatus(self):
        """
        Set 'get status' to the server, async
        """
        result = await self._transact(self._methods["SERVER_GETSTATUS"])
        return result

    def parseStatus(self, status):
        """
        Parses status line and updated local parameters
        """
        self._version = status.get('server').get('version')
        self._groups = {}
        self._clients = {}
        self._streams = {}
        for stream in status.get('server').get('streams'):
            self._streams[stream.get('id')] = Stream(stream)
            self._log.debug(f"stream found: {self._streams[stream.get('id')]}")
        for group in status.get('server').get('groups'):
            self._groups[group.get('id')] = Group(self, group)
            self._log.debug(f"group found: {self._groups[group.get('id')]}")
            for client in group.get('clients'):
                self._clients[client.get('id')] = Client(self, client)
                self._log.debug(f"client found: {self._clients[client.get('id')]}")
        self._log.debug(f"parsed snapcast status:\nversion: {self._version}\n\ngroups: {self._groups}\n\nclients: {self._clients}\n\nstreams: {self._streams}")



    def getJsonRpcVersion(self):
        """
        Return the JSON RPC version used by server
        """
        _log.info('getJsonRpcVersion')
        result = yield from self._transact(self._methods["SERVER_GETRPCVERSION"])
        _log.info(f'getJsonRpcVersion result: {result}')
        return result

    def server_on_update():
        pass

    def stream_on_update():
        pass

    def client_on_connect():
        pass

    def client_on_disconnect():
        pass

    def client_on_volume_changed():
        pass

    def client_on_latency_changed():
        pass

    def client_on_name_changed():
        pass

    def group_on_mute():
        pass

    def group_on_stream_changed():
        pass
