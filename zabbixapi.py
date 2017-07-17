import requests
import json
from functools import wraps

class ZabbixApi(object):
    def __init__(self, server):
        self.session = requests.Session()
        self.id = 0
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
            "id": self.id,
        }
        self.id += 1
        login_request = self.session.post(self.server, data=json.dumps(data))
        self.token = login_request.json()['result']

    def post_requests(func):
        def wrapper(self, *args):
            method, params = func(self, *args)
            data = {
                "jsonrpc": "2.0",
                "method": method,
                "params": params,
                "auth": self.token,
                "id": self.id,
            }
            self.id += 1
            query = self.session.post(self.server, data=json.dumps(data))
            return query.json()
        return wrapper

    @post_requests
    def get_host_list(self, method, params):
        return method, params

    def __getattr__(self, item):
        return ZabbixObjectApi(item, self)


class ZabbixObjectApi(object):
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent

    def __getattr__(self, item):
        method = '{}.{}'.format(self.name, item)
        def func(*args, **kwargs):
            return self.parent.get_host_list(method, args or kwargs)
        return func
