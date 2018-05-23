import telnetlib
import json
import asyncio
import logging
from socket import gaierror

class SnapcastTelnet:

    HOST = "worker-pi3.local"
    PORT = 1705
    # logging.basicConfig(filename='error.log',level=logging.DEBUG)
    log = logging.getLogger(__name__)

    def doRequestToSnapcast(self, request):
        request = json.dumps(request)
        # logging.info ('starting doRequestToSnapChat with ' + json.loads(request))
        try:
            telnet = telnetlib.Telnet(self.HOST, self.PORT)
        except gaierror as err:
            self.log.error(f"could not resolve {self.HOST}")
            return
        except ConnectionRefusedError as err:
            self.log.error(f"connection refused connecting to {self.HOST}:{self.PORT}")
            return
        jobj = json.loads(request)
        self.log.info ('json.loads: ' + json.dumps(jobj))
        file = request.replace('\n', '') + "\r\n"
        self.log.info ('file: ' + file)
#    	  log.debug(file  + "\r\n")
        requestId = jobj['id']
        telnet.write(file.encode('ascii'))
        while (True):
#		log.info ('Still true ')
            response = telnet.read_until("\r\n".encode('ascii'), 2)
            jResponse = json.loads(response)
            if 'id' in jResponse:
                if jResponse['id'] == requestId:
                    self.log.info(f'respone: {jResponse}')
                    return jResponse;
        return
