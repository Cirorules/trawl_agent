"""
    ***
    Modified generic daemon class
    ***

    Author:     http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
                Matt Iavarone for Trawl
    License:    http://creativecommons.org/licenses/by-sa/3.0/
"""

import atexit
import sys
import time
from multiprocessing import Pool, Process
from signal import SIGTERM
import os

from trawl_agent.common import util
from trawl_agent.common import collect
from trawl_agent.webservers import weblogs


class Daemon(object):
    def __init__(self, pidfile='/var/run/trawl.pid', stdin='/var/log/trawl',
                 stdout='/var/log/trawl', stderr='/var/log/trawl'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
        if not os.path.isfile(stdout):
            os.mknod(stdout)

    def daemonize(self):
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.stderror))
            sys.exit(1)

        os.chdir("/")
        os.setsid()
        os.umask(0)

        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        atexit.register(self.delpid)
        pid = str(os.getpid())
        file(self.pidfile, 'w+').write("%s\n" % pid)

    def delpid(self):
            os.remove(self.pidfile)

    def start(self):
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = "pidfile %s already exists. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)
        self.daemonize()
        self.run()

    def stop(self):
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return

        try:
                while 1:
                    os.kill(pid, SIGTERM)
                    time.sleep(0.1)
        except OSError as err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                sys.stderr.write(err)
                sys.exit(1)

    def status(self):
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        try:
            procfile = file("/proc/%d/status" % pid, 'r')
            procfile.close()
        except IOError:
            sys.stdout.write("there is not a process with the PID specified in %s\n" % self.pidfile)
            sys.exit(0)
        except TypeError:
            sys.stdout.write("pidfile %s does not exist\n" % self.pidfile)
            sys.exit(0)

        sys.stdout.write("the process with the PID %d is running\n" % pid)

    def restart(self):
        self.stop()
        self.start()

    def run(self):
        agent_config = util.ReadAgentConf().read_section('global_config')
        #stat_thread_count = agent_config['stats']['number_of_threads']
        log_thread_count = agent_config['web_logs']['number_of_threads']
        interval = agent_config['check_interval']
        mods = util.confd_modules()
        log_list = []
        cull = collect.CollectStats()
        cull_thread = Process(target=cull.run_collector, args=(mods, interval))
        cull_thread.start()
        if 'apache' in mods:
            apache_config = util.read_conf('apache')
            log_config = apache_config['instances']['apache_logs']
            log_dir = log_config['log_directory']
            logs = log_config['logs']
            for i in logs:
                log_full = (log_dir + i if log_dir[-1:] == '/' else log_dir + '/' + i + ':apache')
                log_list.append(log_full)

        if 'nginx' in mods:
            nginx_config = util.read_conf('nginx')
            log_config = nginx_config['instances']['nginx_logs']
            log_dir = log_config['log_directory']
            logs = log_config['logs']
            for i in logs:
                log_full = (log_dir + i if log_dir[-1:] == '/' else log_dir + '/' + i + ':nginx')
                log_list.append(log_full)

        log_pool = Pool(processes=log_thread_count)
        log_pool.map(weblogs.put_lines, log_list)
