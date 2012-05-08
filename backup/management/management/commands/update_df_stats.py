import glob
from os.path import exists
import subprocess

from django.core.management.base import BaseCommand, CommandError
import os.path
from django.conf import settings


class Command(BaseCommand):
    args = "(none)"
    help = "Load free disk space information"

    def handle(self, *args, **kwargs):
        f = open("/etc/mtab", "r")
        for line in f:
            line = line.split()
            if settings.DIRECTORIES_ROOT in line[1]:
                username = (line[1]).replace(settings.DIRECTORIES_ROOT, "").replace("/", "")
                p = subprocess.Popen(["sudo", "%s/df.py" % settings.WRAPPERS_PATH, username], stdout=subprocess.PIPE)
                output = p.communicate()[0]
                returncode = p.returncode
                if returncode != 0:
                    raise Exception("Invalid returncode from df")
                output = output.split("\n")
                output = output[1] # First line is headers
                output = output.split()
                usedspace = int(output[1]) / 1024
                rrd_filename = "%s/lib/%s-space.rrd" % (settings.ROOT_DIR, username)
                if not exists(rrd_filename):
                    p = subprocess.Popen(["rrdtool", "create", rrd_filename, "--start", "now-10", "--step", "300", "DS:used:GAUGE:700:0:10000000", "RRA:AVERAGE:0.5:1:9000", "RRA:AVERAGE:0.5:5:9000", "RRA:AVERAGE:0.5:30:2000", "RRA:MAX:0.5:1:9000", "RRA:MAX:0.5:5:9000", "RRA:MAX:0.5:30:2000"])
                    p.wait()
                p = subprocess.Popen(["rrdtool", "update", rrd_filename, "N:%s" % usedspace])
                p.wait()
                p = subprocess.Popen(["rrdtool", "graph", "%s/media/userspace/%s.png" % (settings.ROOT_DIR, username), "--start", "now-30d", "--end", "now", "-v", "Megabytes", "-t", "Disk usage", "DEF:used=%s:used:AVERAGE" % rrd_filename, "LINE1:used#FF0000"], stdout=subprocess.PIPE)
                p.communicate()
                p.wait()
        f.close()

