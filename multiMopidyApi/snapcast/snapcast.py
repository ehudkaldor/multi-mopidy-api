from .snapcastTelnet import SnapcastTelnet
import asyncio
import json
import logging

_jsonrpc = "2.0"
_nextClientId = 0
_log = logging.getLogger(__name__)

def _getNextId(self):
        _nextClientId += 1
        return _nextClientId

class Snapcast(asyncio.Protocol):
    # telnet = SnapcastTelnet()

    def __init__(self, methods, callbacks):
        self._transport = None
        self._buffer = {}
        self._methods = methods
        self._callbacks = callbacks
        self._data_buffer = ''
        # yield from self.start()
        # self._callbacks = {
            # CLIENT_ONCONNECT: self._on_client_connect,
            # CLIENT_ONDISCONNECT: self._on_client_disconnect,
            # CLIENT_ONVOLUMECHANGED: self._on_client_volume_changed,
            # CLIENT_ONNAMECHANGED: self._on_client_name_changed,
            # CLIENT_ONLATENCYCHANGED: self._on_client_latency_changed,
            # GROUP_ONMUTE: self._on_group_mute,
            # GROUP_ONSTREAMCHANGED: self._on_group_stream_changed,
            # STREAM_ONUPDATE: self._on_stream_update,
            # SERVER_ONDISCONNECT: self._on_server_disconnect,
            # SERVER_ONUPDATE: self._on_server_update
        # }
        _log.info(f'Snapcast created')

    def start(self):
        yield from self._do_connect()
        self._log.info('connected to snapserver on %s:%s', self._host, self._port)
        status = yield from self.status()
        self.synchronize(status)
        self._on_server_connect()

    def connection_made(self, transport):
        """When a connection is made."""
        self._transport = transport

    def connection_lost(self, exception):
        """When a connection is lost."""
        self._callbacks.get(SERVER_ONDISCONNECT)(exception)

    def synchronize(self, status):
        """Synchronize snapserver."""
        self._version = status.get('server').get('version')
        self._groups = {}
        self._clients = {}
        self._streams = {}
        for stream in status.get('server').get('streams'):
            self._streams[stream.get('id')] = Snapstream(stream)
            _log.debug('stream found: %s', self._streams[stream.get('id')])
        for group in status.get('server').get('groups'):
            self._groups[group.get('id')] = Snapgroup(self, group)
            _log.debug('group found: %s', self._groups[group.get('id')])
            for client in group.get('clients'):
                self._clients[client.get('id')] = Snapclient(self, client)
                _log.debug('client found: %s', self._clients[client.get('id')])

    def generateRequest(method, params = None):
        request = json.dumps({
            'jsonrpc': _jsonrpc,
            'id': _getNextId(),
            'method': method,
            'params': params or {}
        })
        return f'{request}\r\n'.encode()

    @asyncio.coroutine
    async def request(self, method, params):
        request = self.jsonrpc_request(method, params)
        id = request.get('id')
        self._transport.write(request)
        self._buffer[id] = {'flag': asyncio.Event()}
        yield self._buffer[id]['flag'].wait()
        result = self._buffer[id]['data']
        del self._buffer[id]['data']
        # return result

    def data_received(self, data):
        self._data_buffer += data.decode()
        if not self._data_buffer.endswith('\r\n'):
            return
        data = self._data_buffer
        self._data_buffer = ''  # clear buffer
        for cmd in data.strip().split('\r\n'):
            data = json.loads(cmd)
            if not isinstance(data, list):
                data = [data]
            for item in data:
                self.handle_data(item)

    def handle_data(self, data):
        if 'id' in data:
            identifier = data.get('id')
            self._buffer[identifier]['data'] = data.get('result')
            self._buffer[identifier]['flag'].set()
        else:
            if data.get('method') in self._callbacks:
                self._callbacks.get(data.get('method'))(data.get('params'))

    def _on_server_disconnect(self, exception):
        """Handle server disconnection."""
        self._protocol = None
        if self._on_disconnect_callback_func and callable(self._on_disconnect_callback_func):
            self._on_disconnect_callback_func(exception)
        if self._reconnect:
            self._reconnect_cb()

    # @asyncio.coroutine
    def _do_connect(self):
        _log.info('_do_connect()')
        """Perform the connection to the server."""
        _, self._protocol = yield from self._loop.create_connection(
            lambda: SnapcastProtocol(self._callbacks), self._host, self._port)

    @asyncio.coroutine
    async def _transact(self, method, params=None):
        """Wrap requests."""
        result = yield self._protocol.request(method, params)
        # return result

    def setVolumeTest(self):
        return self.telnet.doRequestToSnapcast({"id":self._getNextId(),"jsonrpc":self.jsonrpc,"method":"Client.SetVolume","params":{"id":"02:42:ac:11:00:11","volume":{"muted":False,"percent":74}}})

    def getJsonRpcVersion(self):
        # return self.telnet.doRequestToSnapcast({"id":self._getNextId(),"jsonrpc":self.jsonrpc,"method":"Server.GetRPCVersion"})
        self._log.info('getJsonRpcVersion')
        result = yield from self._transact(self.methods["SERVER_GETRPCVERSION"])
        self._log.info(f'getJsonRpcVersion result: {result}')
        return result

    def getClientStatus(self, clientId):
        return self.telnet.doRequestToSnapcast({"id":self._getNextId(),"jsonrpc":self.jsonrpc,"method":"Client.GetStatus","params":{"id":clientId}})

    def setClientVolume(self, clientId, shouldImute, volumeToSet):
        return self.telnet.doRequestToSnapcast({"id":self._getNextId(),"jsonrpc":self.jsonrpc,"method":"Client.SetVolume","params":{"id":clientId,"volume":{"muted":shouldImute,"percent":volumeToSet}}})

    def setClientLatency(self, clientId, latencyToSet):
        return self.telnet.doRequestToSnapcast({"id":self._getNextId(),"jsonrpc":self.jsonrpc,"method":"Client.SetLatency","params":{"id":clientId,"latency":latencyToSet}})

    def setClientName(self, clientId, newName):
        return self.telnet.doRequestToSnapcast({"id":self._getNextId(),"jsonrpc":self.jsonrpc,"method":"Client.SetName", "params":{"id":clientId,"name":newName}})

    def getGroupStatus(self, groupId):
        return self.telnet.doRequestToSnapcast({"id":self._getNextId(),"jsonrpc":self.jsonrpc,"method":"Group.GetStatus","params":{"id":groupId}})

    def setGroupMute(self, groupId, shouldImute):
        return self.telnet.doRequestToSnapcast({"id":self._getNextId(),"jsonrpc":self.jsonrpc,"method":"Group.SetMute","params":{"id":groupId,"mute":shouldImute}})

    def setGroupStream(self, groupId, streamId):
        return self.telnet.doRequestToSnapcast({"id":self._getNextId(),"jsonrpc":self.jsonrpc,"method":"Group.SetStream","params":{"id":groupId,"stream_id":streamId}})

    def setGroupClients(self, groupId, clientIdList):
        return self.telnet.doRequestToSnapcast({"id":self._getNextId(),"jsonrpc":self.jsonrpc,"method":"Group.SetClients","params":{"clients":clientIdList,"id":groupId}})

    def getServerStatus(self):
        self._log.info('getServerStatus')
        # return self.telnet.doRequestToSnapcast({"id":self._getNextId(),"jsonrpc":self.jsonrpc,"method":"Server.GetStatus"})
        result = yield from self._transact(self.methods["SERVER_GETSTATUS"])
        self._log.info(f'getServerStatus result: {result}')
        return result


    def deleteClient(self, clientId):
        return self.telnet.doRequestToSnapcast({"id":self._getNextId(),"jsonrpc":self.jsonrpc,"method":"Server.DeleteClient","params":{"id":clientId}})
