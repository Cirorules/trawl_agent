import os
import psutil
import trawl_agent.common.api_handler
import time
import re

class HostStats():
    def get_parts(self):
        fsignore = ['iso9660', 'cdrom']
        partitions = []
        mounts = psutil.disk_partitions(all=False)
        for mount in mounts:
            if mount.fstype not in fsignore:
                partitions.append(mount.mountpoint)

        return partitions

    def net_stats(self):

        parts = [
            r'(^|\s+)',
            r'(?P<device>\w+)\:\s+',
            r'(?P<rbytes>\d+)\s+',
            r'(?P<rpackets>\d+)\s+',
            r'(?P<rerrs>\d+)\s+',
            r'(?P<rdrop>\d+)\s+',
            r'(?P<rfifo>\d+)\s+',
            r'(?P<rframe>\d+)\s+',
            r'(?P<rcompressed>\d+)\s+',
            r'(?P<rmulticast>\d+)\s+',
            r'(?P<sbytes>\d+)\s+',
            r'(?P<spackets>\d+)\s+',
            r'(?P<serrs>\d+)\s+',
            r'(?P<sdrop>\d+)\s+',
            r'(?P<sfifo>\d+)\s+',
            r'(?P<scolls>\d+)\s+',
            r'(?P<scarrier>\d+)\s+',
            r'(?P<scompress>\d+)',
        ]
        pattern = re.compile(''.join(parts))

        net = {}
        f = open('/proc/net/dev', 'r')
        lines = f.readlines()
        for line in lines:
            m = pattern.match(line) if True else None
            if m is not None:
                    net[m.group('device')] = m.groupdict()

        devs = net.keys()
        net_total = {}
        for dev in devs:
           net_total[dev] =  ( int(net[dev]['rbytes']) + int(net[dev]['sbytes']) )

        return net_total


    def disk_space_stats(self, stat):
        partitions = self.get_parts()
        disk_usage = {}
        for part in partitions:
            p = psutil.disk_usage(part)
            if stat == 'used':
                disk_usage[part] = p.used
            else:
                disk_usage[part] = p.total

        return disk_usage

    def cpu_stats(self):
        la = os.getloadavg()
        stats = {}
        stats['la1'], stats['la5'], stats['la15'] = la[0], la[1], la[2]
        cpu_pct_stats = psutil.cpu_times_percent(interval=1)
        stats['cpu_iowait'], stats['cpu_sys'], stats['cpu_usr'], stats['cpu_idle'], stats['cpu_steal'] = cpu_pct_stats.iowait, cpu_pct_stats.system, cpu_pct_stats.user, cpu_pct_stats.idle, cpu_pct_stats.steal
        stats['cpu_count'] = psutil.cpu_count()

        return stats

    def mem_stats(self):
        vram = psutil.virtual_memory()
        stats = {'vm_total': vram[0], 'vm_avail': vram[1], 'vm_used': vram[3], 'vm_buffers': vram[7], 'vm_cache': vram[8]}

        return stats

    def swap_stats(self):
        swap = psutil.swap_memory()
        stats = {'swap_total': swap[0], 'swap_free': swap[2], 'swap_used': swap[1], 'swap_pct': swap[3]}

        return stats


    def collect(self):
        stats = {}
        stats['log_type'] = 'sysstats'
        up = trawlers.trawl_agent.common.api_handler.UploadHostStats()
        run1 = {}
        while True:
            try:
                ns = self.net_stats()
                ms = self.mem_stats()
                cs = self.cpu_stats()
                du = self.disk_space_stats('used')
                dt = self.disk_space_stats('total')
                if len(run1.keys()) == 0:
                    run1 = ns
                else:
                    nets = {}
                    for key in ns.keys():
                        nets[key] = ( ns[key] - run1[key] ) / 300

                    stats['NET'] = nets
                    stats['MEM'] = ms
                    stats['CPU'] = cs
                    stats['DISK_TOTAL'] = dt
                    stats['DISK_USED'] = du
                    up.upload_stats(stats)
                    run1 = ns
                    time.sleep(300)
            except:
                raise

