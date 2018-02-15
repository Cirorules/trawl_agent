from trawl_agent.common import hoststats
from trawl_agent.common import util
import time
from trawl_agent.common import api_handler


class CollectStats(object):
    def __init__(self):
        self.first_run = True

    @staticmethod
    def collect_host_stats():
        hs = hoststats.HostStats()
        stats = {'NET': hs.net_stats(), 'MEM': hs.mem_stats(), 'CPU': hs.cpu_stats(),
                 'DISK_USED': hs.disk_space_stats('used'), 'DISK_TOTAL': hs.disk_space_stats('total'),
                 }

        return stats

    @staticmethod
    def collect_httpd_stats(url):
        from trawl_agent.webservers import httpd
        try:
            stats = httpd.httpd_stats(url)
        except Exception as e:
            print(str(e))
            raise

        return stats

    @staticmethod
    def collect_nginx_stats(url):
        from trawl_agent.webservers import nginx
        try:
            stats = nginx.nginx_stats(url)
        except Exception as e:
            print(str(e))
            raise

        return stats

    @staticmethod
    def collect_postgres_stats(host, port, user=None, password=None):
        from trawl_agent.rdbms import postgres
        stats = {}
        pstats = postgres.PostgresStats()
        for q in pstats.query.keys():
            r = pstats.execute_query(pstats.query[q], host, port, user, password)
            stats[q] = r[0]

        stats = {k : float(v) for k,v in stats.iteritems()}
        return stats

    def collect_stats(self, *args):
        stats = {}
        if 'apache' in args:
            conf = util.read_conf('apache')
            url = conf['instances']['apache_status_url']
            stats['apache'] = self.collect_httpd_stats(url)
        if 'nginx' in args:
            conf = util.read_conf('nginx')
            url = conf['instances']['nginx_status_url']
            stats['nginx'] = self.collect_nginx_stats(url)
        if 'postgres' in args:
            conf = util.read_conf('postgres')
            host = conf['instances']['host']
            port = conf['instances']['port']
            if 'user' in conf['instances'].keys():
                user = conf['instances']['user']
            else:
                user = None
            if 'password' in conf['instances'].keys():
                password = conf['instances']['password']
            else:
                password = None
            stats['postgres'] = self.collect_postgres_stats(host, port, user, password)
        stats['host_stats'] = self.collect_host_stats()
        return stats

    def run_collector(self, mods, interval):
        up = api_handler.UploadStats()
        while True:
            try:
                stats = self.collect_stats(*mods)
                if self.first_run is True:
                    last_run = stats['host_stats']['NET']
                    del stats['host_stats']['NET']
                    self.first_run = False
                else:
                    this_run = {}
                    for k, v in stats['host_stats']['NET'].iteritems():
                        this_run[k] = stats['host_stats']['NET'][k] - last_run[k]
                    last_run = stats['host_stats']['NET']
                    stats['host_stats']['NET'] = this_run
                up.upload_stats(stats)
            except Exception as e:
                print(str(e))
            time.sleep(interval * 60)


