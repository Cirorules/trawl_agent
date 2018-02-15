from trawl_agent.common import api_handler
import os
from datetime import datetime
import re
import time
import shelve

def put_lines(loginfo):
    runfile = '/var/run/trawl.run'
    cur = datetime.now()
    up = api_handler.UploadLogs()
    loginfo = loginfo.split(':')
    logname = loginfo[0]
    logtype = loginfo[1]
    if logtype == 'apache':
        access_parts = [r'(?P<remoteIP>\S+)', r'\S+', r'(?P<user>\S+)', r'\[(?P<time>.+)\]', r'"(?P<method>.+)',
                        r'(?P<request>.+)', r'(?P<proto>\w+/.+)"', r'"(?P<server>\S+)"', r'"(?P<referer>.*)"',
                        r'"(?P<agent>.*)"', r'(?P<status>[0-9]+)', r'(?P<request_length>[0-9]+)']

        error_parts = [r'\[(?P<date>\w+\s+\w+\s+\d+\s+\d+:\d+:.+\s+\d+)\]', r'\[(?P<core>\w+):(?P<error>\w+)\]',
                       r'\[pid\s+(?P<pid>\d+)\]', r'(?P<message>.+)']
    else:
        access_parts = [r'(?P<remoteIP>\S+)', r'\S+', r'(?P<user>\S+)', r'\[(?P<time>.+)\]', r'"(?P<method>.+)',
                        r'(?P<request>.+)', r'(?P<proto>\w+/.+)"', r'"(?P<server>\S+)"', r'"(?P<referer>.*)"',
                        r'"(?P<agent>.*)"', r'(?P<status>[0-9]+)', r'(?P<request_length>[0-9]+)']

        error_parts = [r'(?P<date>\d+/\d+/\d+\s\d+:\d+:\d+)', r'\[(?P<level>\w+)\]', r'(?P<pid>\d+)#(?P<tid>\d+):',
                       r'\*(?P<cid>\d+)', r'(?P<function>\S+)', r'\"(?P<uri>\S+)\"', r'(?P<error>.+),',
                       r'client:\s+(?P<client>\S+),', r'server:\s+(?P<server>\S+),', r'request:\s+\"(?P<request>.+)\",',
                       r'host:\s+\"(?P<host>\S+)\"']

    # Error parts datetime conversion from string: datetime.datetime.strptime(dt, '%a %b %d %I:%M:%S.%f %Y')
    access_pattern = re.compile(r'\s+'.join(access_parts)+r'\s*\Z')
    error_pattern = re.compile(r'\s+'.join(error_parts)+r'\s*\Z')
    current = open(logname, 'r')
    curnode = os.fstat(current.fileno()).st_ino

    def readrun():
        f = shelve.open(runfile)
        if logname in f.keys():
            loc = f[logname]
        else:
            loc = 0
            f[logname] = loc
        f.close()
        return loc


    def writerun(loc):
        f = shelve.open(runfile)
        f[logname] = loc
        f.close()

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

                if m is not None:
                    res = {}
                    res['log_data'] = m.groupdict()
                    res['log_data']['time'] = re.sub('\s-\d{4}', '', res['log_data']['time'])
                    time_now = datetime.now()
                    res['date'] = datetime.strftime(time_now, '%Y-%m-%d %H:%M:%S')
                    res['log_data']['log_file'] = logname
                    res['log_type'] = logtype
                    try:
                        res['log_data']['request_length'] = int(res['log_data']['request_length'])
                    except ValueError:
                        res['log_data']['request_length'] = 0

                    try:
                        up.upload_weblogs(res)
                    except Exception:
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

        time.sleep(1)
        writerun(current.tell())