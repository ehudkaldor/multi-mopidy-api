import logging
import configparser
import asyncio
from .protocol import Protocol


class API:
    _log = logging.getLogger("API")

    def __init__(self, host, port, methods, callbacks, loop):
        self._log.debug(f"initializing API to: {host}:{port}")
        self._loop = loop
        self._host = host
        self._port = port
        self._methods = methods
        # self._loop = asyncio.get_event_loop()
        self._protocol = Protocol(host, port, callbacks, loop)
        self._log.debug(f"API init completed. methods: {self._methods}")

    async def start(self):
        """Initiate server connection."""
        await self._do_connect()
        self._log.info('connected to snapserver on %s:%s', self._host, self._port)
        status = await self.getStatus()
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
        """System status."""
        result = await self._transact(self._methods["SERVER_GETSTATUS"])
        return result


    def getJsonRpcVersion(self):
        """
        Return the JSON RPC version used by server
        """
        _log.info('getJsonRpcVersion')
        result = yield from self._transact(self._methods["SERVER_GETRPCVERSION"])
        _log.info(f'getJsonRpcVersion result: {result}')
        return result

    def serverOnUpdate():
        pass

    def streamOnUpdate():
        pass

    def clientOnConnect():
        pass

    def clientOnDisconnect():
        pass

    def clientOnVolumeChanged():
        pass

    def clientOnLatencyChanged():
        pass

    def clientOnNameChanged():
        pass

    def groupOnMute():
        pass

    def groupOnStreamChanged():
        pass
