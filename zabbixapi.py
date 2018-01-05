# encoding: utf-8


from __future__ import unicode_literals
import requests
import json
import datetime
import time


class ZabbixApi(object):
    def __init__(self, server):
        self.session = requests.Session()
        self.id = 0
        self.username = 'xx'
        self.password = 'xx'
        if server.endswith('/'):
            self.server = server + 'api_jsonrpc.php'
        else:
            self.server = server + '/api_jsonrpc.php'
        self.session.headers.update({'Content-Type': 'application/json-rpc'})
        self.token = self.get_auth_token()

    def get_auth_token(self):
        data = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": self.username,
                "password": self.password
            },
            "id": self.id,
        }
        self.id += 1
        login_request = self.session.post(self.server, data=json.dumps(data))
        token = login_request.json()['result']
        return token

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
            query = self.session.post(self.server, json=data)
            return query.json()

        return wrapper

    @post_requests
    def do_action(self, method, params):
        return method, params[0]

    def __getattr__(self, item):
        return ZabbixObjectApi(item, self)


class ZabbixObjectApi(object):
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent

    def __getattr__(self, item):
        method = '{}.{}'.format(self.name, item)

        def func(*args, **kwargs):
            return self.parent.do_action(method, args or kwargs)

        return func


if __name__ == '__main__':
    server = 'xxx'
    zabbix = ZabbixApi(server)

    today = '{0} 00:00:00'.format(time.strftime('%Y-%m-%d'))
    six_days_ago = '{0} 00:00:00'.format((datetime.datetime.now() - datetime.timedelta(days=6)).strftime('%Y-%m-%d'))
    today = int(time.mktime(time.strptime(today, '%Y-%m-%d %H:%M:%S')))
    six_days_ago = int(time.mktime(time.strptime(six_days_ago, '%Y-%m-%d %H:%M:%S')))

    alert_params = {
        'filter': {
            'mediatypeid': [
                '5'
            ],
            'esc_step': [
                '1'
            ]
        },
        'sortfield': 'alertid',
        'sortorder': 'DESC',
        'time_from': six_days_ago,
        'time_till': today
    }

    results = zabbix.alert.get(alert_params)['result']
    for r in results:
        if '恢复' not in r['subject']:
            print '-' * 100
            print r['subject']
            for i in r['message'].split('|'):
                print i

