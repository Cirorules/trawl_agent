import ConfigParser
import json
import os
import platform
import socket

import requests

from trawl_agent.common import api_handler
from trawl_agent.common import hoststats


class Register():
    TRAWL_URL = 'http://<< url >>'
    REG_URL = TRAWL_URL + '/in/register/'
    VALID_URL = TRAWL_URL + '/in/validate/'
    ADDLOG_URL = TRAWL_URL + '/in/add_applog/'
    HEADERS = {'content-type': 'application/json'}
    SYSCONFIG = '/etc/sysconfig/trawl.cfg'

    def register_host(self, key):
        try:
            validate = trawlers.trawl_agent.common.api_handler.APICall()
            result = validate.get(self.VALID_URL, key)
        except:
            raise

        if result['hosts'] < result['subs']:
            u = os.uname()
            distro = platform.linux_distribution()
            host = {'host_os': u[0], 'host_name': u[1], 'host_os_ver': u[2], 'api_key': key, 'distro_name': distro[0], 'distro_version': distro[1]}
            h = hoststats.HostStats()
            nets = h.net_stats()
            nets = nets.keys()
            host['net_devs'] = nets
            host['disk_parts'] = h.get_parts()
            try:
                os.remove(self.SYSCONFIG)
            except:
                pass
            config = ConfigParser.ConfigParser()
            config.add_section('API')
            config.set('API', 'api_key', key)
            config.add_section('HOST')
            config.set('HOST', 'name', host['host_name'])
            with open(self.SYSCONFIG, 'wb') as configfile:
                try:
                    config.write(configfile)
                except:
                    return "Unable to write conf.d file"

            j = json.dumps(host)

            try:
                requests.put(self.REG_URL, headers=self.HEADERS, data=j)
            except:
                raise
            print("Registered successfully")
        else:
            print("You have reached your host limit for your subscription.")

    def register_logs(self, app_name, log_path):
        config = ConfigParser.ConfigParser()
        config.readfp(open(self.SYSCONFIG))
        key = config.get('API', 'api_key')
        try:
            logs = config.get('HOST', 'logs')
            logs = eval(logs)
        except:
            logs = {}

        try:
            logs[log_path] = app_name
        except:
            raise

        config.set('HOST', 'logs', logs )
        with open('/etc/sysconfig/trawl.cfg', 'wb') as configfile:
            try:
                config.write(configfile)
            except:
                return "Unable to write conf.d file"

        log = {}
        log['host'] = socket.gethostname()
        log['log_type'] = app_name
        log['api_key'] = key
        log['log_location'] = log_path
        j = json.dumps(log)
        req = requests.put(self.ADDLOG_URL, headers=self.HEADERS, data=j)
        return req

    def find_logs(self):
        app_logs = ['httpd', 'nginx']
        search_dirs = ('/var/log/',)
        dirs = []
        for directory in search_dirs:
            for d in os.listdir(directory):
                if d in app_logs:
                    dirs.append([d, directory + d])

        app_log_files = []
        for directory in dirs:
            for f in os.listdir(directory[1]):
                if not f.__contains__('gz'):
                    app_log_files.append([directory[0], directory[1] + '/' + f])

        return app_log_files