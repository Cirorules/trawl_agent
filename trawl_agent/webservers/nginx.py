import re
from datetime import datetime
import os, time
from trawl_agent.common import api_handler
import requests

class NginxWeblogs():
    def __init__(self, runfile='/var/run/trawl.run'):
        self.runfile = runfile
        if not os.path.isfile(runfile):
            os.mknod(runfile)
        self.cur = datetime.now()

    def put_lines(self, logname, logtype):
        up = api_handler.UploadLogs()

        access_parts = [r'(?P<remoteIP>\S+)', r'\S+', r'(?P<user>\S+)', r'\[(?P<time>.+)\]', r'"(?P<method>.+)',
                        r'(?P<request>.+)', r'(?P<proto>\w+/.+)"', r'"(?P<server>\S+)"', r'"(?P<referer>.*)"',
                        r'"(?P<agent>.*)"', r'(?P<status>[0-9]+)', r'(?P<request_length>[0-9]+)']

        error_parts = [r'(?P<date>\d+/\d+/\d+\s\d+:\d+:\d+)', r'\[(?P<level>\w+)\]', r'(?P<pid>\d+)#(?P<tid>\d+):',
                       r'\*(?P<cid>\d+)', r'(?P<function>\S+)', r'\"(?P<uri>\S+)\"', r'(?P<error>.+),',
                       r'client:\s+(?P<client>\S+),', r'server:\s+(?P<server>\S+),', r'request:\s+\"(?P<request>.+)\",',
                       r'host:\s+\"(?P<host>\S+)\"']

        access_pattern = re.compile(r'\s+'.join(access_parts)+r'\s*\Z')
        error_pattern = re.compile(r'\s+'.join(error_parts)+r'\s*\Z')
        current = open(logname, 'r')
        curnode = os.fstat(current.fileno()).st_ino

        def readrun():
            f = open(self.runfile, 'r').read()
            try:
                d = eval(f)
            except:
                return 0
            return d[logname]

        def writerun(loc):
            with open(self.runfile, 'r+') as f:
                try:
                    d = eval(f.read())
                except:
                    d = {logname: 0}
                d[logname] = loc
                f.seek(0)
                f.write(str(d))

        checkrun = readrun()
        if not checkrun == 0:
            current.seek(checkrun)

        while True:
            while True:
                buf = current.readlines(100)
                if not buf:
                    break
                for line in buf:
                    m = access_pattern.match(line) if True else error_pattern.match(line)
                    if access_pattern.match(line):
                        m = access_pattern.match(line)
                    else:
                        m = error_pattern.match(line)

                    if m is not None:
                        res = {}
                        res['log_data'] = m.groupdict()
                        res['log_data']['time'] = re.sub('\s-\d{4}', '', res['log_data']['time'])
                        t = datetime.strptime(res['log_data']['time'],'%d/%b/%Y:%H:%M:%S')
                        res['date'] = t.isoformat()
                        res['log_data']['log_file'] = logname
                        res['log_type'] = logtype
                        try:
                            res['log_data']['request_length'] = int(res['log_data']['request_length'])
                        except ValueError:
                            res['log_data']['request_length'] = 0

                        try:
                            up.upload_weblogs(res)
                        except:
                            raise

            try:
                if os.stat(logname).st_ino != curnode:
                    new = open(logname, 'r')
                    current.close()
                    current = new
                    curnode = os.fstat(current.fileno()).st_ino
                    continue
            except IOError:
                pass

            time.sleep(10)
            writerun(current.tell())

def nginx_stats(url):
    try:
        req = requests.get(url)
    except Exception as e:
        print(str(e))
        raise

    m = re.match('Active connections:\s+(?P<num_connections>\d+)\s+\w+\s+\w+\s+\w+\s+\w+\s+(?P<accepts>\d+)'
                 '\s+(?P<handled>\d+)\s+(?P<requests>\d+)\s+Reading:\s+(?P<reading>\d+)\s+Writing:\s+(?P<writing>\d+)'
                 '\s+Waiting:\s+(?P<waiting>\d+)', req.text)
    stats = {}
    if m:
        for key, value in m.groupdict().iteritems():
            try:
                int(value)
                stats[key] = value
            except ValueError:
                pass
    return stats