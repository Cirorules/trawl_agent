import requests
import json
import time
from trawl_agent.common import util

HEADERS = {'content-type': 'application/json'}
agent_config = util.ReadAgentConf().read_section('global_config')
TRAWL_URL = agent_config['trawl_url']
SYSCONFIG = '/etc/sysconfig/trawl.cfg'


class UploadLogs():
    def __init__(self):
        self.url = TRAWL_URL + '/in/logs/'
        #self.logs = get_config(SYSCONFIG, 'HOST', 'logs')

    def upload_weblogs(self, res):
        res['company'] = {'api_key': agent_config['api_key']}
        res['host'] = agent_config['host_name']
        j = json.dumps(res)

        req = None
        while req is None:
            try:
                req = requests.put(self.url, headers=HEADERS, data=j)
            except:
                time.sleep(10)

        if req.status_code != 201:
            return j


class UploadStats(object):
    def __init__(self):
        self.url = TRAWL_URL + '/in/stats/'

    def upload_stats(self, stats):
        res = {'company': {'api_key': agent_config['api_key']}, 'host': agent_config['host_name'], 'stats': stats}
        j = json.dumps(res)

        req = None
        while req is None:
            try:
                req = requests.put(self.url, headers=HEADERS, data=j)
            except Exception:
                time.sleep(10)

        if req.status_code != 201:
            return j


class APICall(object):
    def get(self, url, api_key):
        res = {'api_key': api_key}
        j = json.dumps(res)
        try:
            req = requests.get(url, headers=HEADERS, data=j)
        except:
            print(url)
            raise
        if req.status_code != 200:
            print(req.status_code)
        return req.json()
