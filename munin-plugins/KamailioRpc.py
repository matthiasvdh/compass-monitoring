import re
import requests
import json


# A generic utility class to perform Kamailio RPC
class KamailioRpc:

    # http://pythoncentral.io/real-world-regular-expressions-for-python/
    KEY_VALUE_REGEX = re.compile(r'^\s*(.+?)\s*=\s*(.+?)\s*$')

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def send_rpc(self, method, args = None, opts = None):
        """
        Send a RPC command to Kamailio
        :param method: method as string
        :param args: optional list of arguments
        :param opts: optional dict of options to add in the rpc json
        :return:
        """
        data = {
            'method': method,
            'params': args if args else [],
            'jsonrpc': '2.0',
            'id': 1
        }
        if opts:
            data.update(opts)

        url = "http://%s:%s/RPC" % (self.host, self.port)
        resp = requests.post(url, json.dumps(data))
    
        if resp.status_code >= 300:
            raise Exception("Server replied with error: " + resp.text)
        
        return resp.json()

    def parse_key_values(self, array):
        values = {}
        for line in array:
            res = KamailioRpc.KEY_VALUE_REGEX.search(line)
            if res:
                values[res.group(1)] = res.group(2)
            else:
                #self.debug("Unparseable: " + line)
                pass
        return values
