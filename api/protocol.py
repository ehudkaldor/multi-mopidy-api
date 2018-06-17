import asyncio
# import json
import json
import logging

_nextClientId = 1
_jsonrpc = "2.0"
_log = logging.getLogger("protocol-obj")

def _getNextId():
    # _nextClientId += 1
    return _nextClientId

def generateRequest(method, params = None):
    id = _getNextId()
    request = json.dumps({
        'id': id,
        'jsonrpc': _jsonrpc,
        'method': method,
        'params': params or {}
    })
    _log.debug(f'generated request from {method}: {request}')
    return (id, f'{request}\r\n'.encode())

class Protocol(asyncio.Protocol):

    _log = logging.getLogger("Protocol")

    def __init__(self, host, port, callbacks, loop):
        self._log.debug(f"initializing Protocol to: {host}:{port}")
        self._host = host
        self._port = port
        self._callbacks = callbacks
        self._buffer = {}
        self._data_buffer = ''
        # self._loop = asyncio.get_event_loop()
        self._loop = loop
        self._log.debug(f"Protocol init completed")

    def connection_made(self, transport):
        """
        Called when a connection is made
        """
        self._log.debug(f'connection_made. transport: {transport}')
        self._transport = transport
        self._log.debug('connection from {}'.format(self._transport.get_extra_info('peername')))

    def connection_lost(self, exception):
        """
        Called when a connection is lost
        """
        self._log.debug(f'connection_lost. exception: {transport}')
        self._log.debug(f'calling onDisconnect callback: {self._callbacks.get(SERVER_ONDISCONNECT)}')
        self._callbacks.get(SERVER_ONDISCONNECT)(exception)

    def data_received(self, data):
        """
        Called when data is received
        """
        self._data_buffer += data.decode()
        self._log.debug(f"decoded data: {self._data_buffer}")
        if not self._data_buffer.endswith('\r\n'):
            return
        data = self._data_buffer
        self._data_buffer = ''  # clear buffer
        for cmd in data.strip().split('\r\n'):
            data = json.loads(cmd)
            if not isinstance(data, list):
                data = [data]
            for item in data:
                # self._log.debug(f"data_received: {item}")
                self.handle_data(item)

    def handle_data(self, data):
        """
        called with the product of data_received, to decide if it is a response
        to a query (has an id that matches an id stored in _buffer) or a notification
        (has a method that corresponds to one of the callbacks)
        """
        if 'id' in data:
            # self._log.debug(f"got response to query id {data['id']}")
            self.handle_response(data)
        elif 'method' in data:
            # self._log.debug(f"got notification by method {data['method']}")
            self.handle_notification(data)
        else:
            self._log.error(f"received data with no id or method: {data}")

    def handle_response(self, data):
        """
        Handle resposnes to requests
        """
        id = data.get('id')
        self._log.debug(f"got response to query id {id}")
        self._buffer[id]['data'] = data.get('result')
        self._buffer[id]['flag'].set()

    def handle_notification(self, data):
        """
        Handles notification coming from snapcast
        """
        self._log.debug(f"handle_notification {data}")
        if data.get('method') in self._callbacks:

            self._callbacks.get(data.get('method'))(data.get('params'))


    async def request(self, method, params):
        """
        Send a JSONRPC request
        """
        id, req = generateRequest(method, params)
        self._log.debug(f'request: {req}, id: {id}')
        self._transport.write(req)
        self._buffer[id] = {'flag': asyncio.Event()}
        self._log.debug(f'flag set for request id: {id}: {self._buffer[id]}')
        await self._buffer[id]['flag'].wait()
        self._log.debug(f'request returned: {self._buffer}')
        result = self._buffer[id]['data']
        del self._buffer[id]
        return result
