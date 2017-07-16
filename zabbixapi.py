import requests
import json

class ZabbixApi(object):
    def __init__(self, server):
        self.session = requests.Session()
        self.is_authed = False
        self.username = None
        self.password = None
        self.token = None
        if server.endswith('/'):
            self.server = server + 'api_jsonrpc.php'
        else:
            self.server = server + '/api_jsonrpc.php'
        self.session.headers.update({'Content-Type': 'application/json-rpc'})

    def get_auth_token(self, username, password):
        data = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": username,
                "password": password
            },
            "id": 1,
        }
        login_request = self.session.post(self.server, data=json.dumps(data))
        self.token = login_request.json()['result']

    def post_requests(self, method, params):
        data = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "auth": self.token,
            "id": 1,
        }
        return self.session.post(self.server, data=json.dumps(data))

    def get_host_list(self):
        method = 'host.get'
        params = {
            "output": [
                "hostid",
                "host"
            ],
            "selectInterfaces": [
                "interfaceid",
                "ip"
            ]
        }
        query = self.post_requests(method, params)
        return query.json()
