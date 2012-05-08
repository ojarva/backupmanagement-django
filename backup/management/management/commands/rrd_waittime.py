import subprocess
from django.core.management.base import BaseCommand, CommandError
import os.path
from django.conf import settings
import subprocess


class Command(BaseCommand):
    args = "(none)"
    help = "Graph IO wait times"

    def __get_waittime(self):
        f = open("/proc/diskstats", "r")
        id = None
        (waitsum, written, read, yread, ywritten) = (0,0,0,0,0)
        for line in f:
            line = line.split()
            waitsum += int(line[11])
            read += int(line[5])*4/1024 #MB
            written += int(line[9])*4/1024 #MB
        f.close()
        return (waitsum, read, written)

    def handle(self, *args, **kwargs):
        (waitsum, read, written) = self.__get_waittime()

        p = subprocess.Popen(["rrdtool", "update", "%s/lib/readwrite.rrd" % settings.ROOT_DIR, "N:%s:%s" % (read, written)])
        p.wait()
        p = subprocess.Popen(["rrdtool", "graph", "%s/static/readwrite.png" % settings.ROOT_DIR, "--start", "now-1d", "--end", "now", "-t", "Read/write", "DEF:read=%s/lib/readwrite.rrd:read:AVERAGE" % settings.ROOT_DIR, "DEF:write=%s/lib/readwrite.rrd:write:AVERAGE" % settings.ROOT_DIR, "LINE1:read#FF0000", "LINE1:write#00FF00"], stdout=subprocess.PIPE)
        p.communicate()
        p.wait()
        p = subprocess.Popen(["rrdtool", "graph", "%s/static/read.png" % settings.ROOT_DIR, "--start", "now-1d", "--end", "now", "-t", "Read", "-v", "MB", "DEF:read=%s/lib/readwrite.rrd:read:AVERAGE" % settings.ROOT_DIR, "LINE1:read#FF0000"], stdout=subprocess.PIPE)
        p.communicate()
        p.wait()
        p = subprocess.Popen(["rrdtool", "graph", "%s/static/write.png" % settings.ROOT_DIR, "--start", "now-1d", "--end", "now", "-t", "Write", "-v", "MB", "DEF:write=%s/lib/readwrite.rrd:write:AVERAGE" % settings.ROOT_DIR, "LINE1:write#00FF00"], stdout=subprocess.PIPE)
        p.communicate()
        p.wait()
        p = subprocess.Popen(["rrdtool", "update", "%s/lib/waittime.rrd" % settings.ROOT_DIR, "N:%s" % waitsum])
        p.wait()
        p = subprocess.Popen(["rrdtool", "graph", "%s/static/waittime.png" % settings.ROOT_DIR, "--start", "now-1d", "--end", "now", "-t", "IO Wait", "-v", "Requests", "DEF:waittime=%s/lib/waittime.rrd:waittime:MAX" % settings.ROOT_DIR, "LINE1:waittime#FF0000"], stdout=subprocess.PIPE)
        p.communicate()
        p.wait()
