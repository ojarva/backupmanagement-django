from django.conf import settings
from django.core.cache import cache

import json
import os
import pickle
import subprocess
import traceback
import hashlib

import cPickle as pickle

from functools import wraps

__ALL__ = ["Disk", "chpasswd", "Filesystem", "Lvm"]

def require_mounted(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.mounted:
            raise Exception("Disk is not mounted")
        response = func(self, *args, **kwargs)
        return response
    return wrapper

def require_not_mounted(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.mounted:
            raise Exception("Disk is mounted")
        response = func(self, *args, **kwargs)
        return response
    return wrapper

def require_disk(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.exists():
            raise Exception("Disk doesn't exist %s" % self.exists())
        response = func(self, *args, **kwargs)
        return response
    return wrapper

def require_no_disk(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.exists():
            raise Exception("Disk exists")
        response = func(self, *args, **kwargs)
        return response
    return wrapper

def cache_disk_func(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        cache_key = "%s-%s-%s" % (func.__name__, hashlib.md5(pickle.dumps(args)).hexdigest(), hashlib.md5(pickle.dumps(kwargs)).hexdigest())
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        response = func(self, *args, **kwargs)
        cache.set(cache_key, response, 5)
        return response
    return wrapper


def run_sudo(command, *args):
    """ Runs wrapped commands, returns (returncode, output) tuple """
    command = ["sudo", "%s/%s.py" % (settings.WRAPPERS_PATH, command)]
    command += args
    command = [str(a) for a in command]
    p = subprocess.Popen(command, stdout=subprocess.PIPE)
    (stdout, _) = p.communicate()
    return (p.returncode, stdout)


class Lvm:
    def __init__(self, path):
        self.path = path
        self.data = {}
        self.refresh()

    def refresh(self):
        """ Get data from vgdisplay:
              1  volume group name
              2  volume group access
              3  volume group status
              4  internal volume group number
              5  maximum number of logical volumes
              6  current number of logical volumes
              7  open count of all logical volumes in this volume group
              8  maximum logical volume size
              9  maximum number of physical volumes
              10 current number of physical volumes
              11 actual number of physical volumes
              12 size of volume group in kilobytes
              13 physical extent size
              14 total number of physical extents for this volume group
              15 allocated number of physical extents for this volume group
              16 free number of physical extents for this volume group
              17 uuid of volume group

 """
        (code, raw_data) = run_sudo("vgdisplay")
        if code != 0:
            raise Exception("vgdisplay failed")
        raw_data = raw_data.strip()
        raw_data = raw_data.split(":")

        fields = [
            "name", "access", "status", "groupnumber", "max_lv_count",
            "current_lv_count", "lv_open_count", "maximum_lvsize",
            "max_pv_count", "current_pv_count", "actual_pv_count",
            "vg_size_kb", "vg_extent_size", "vg_extent_count",
            "vg_extent_allocated", "vg_extent_free", "uuid"]

        data = {}
        for c in range(0, len(fields)):
            data[fields[c]] = raw_data[c]
        self.data = data
        return data

    @property
    def free(self):
        """ Amount of free disk (GB) """
        return float(self.data["vg_extent_size"]) * float(self.data["vg_extent_free"]) / 1024 / 1024

    @property
    def used(self):
        """ Amount of used disk (GB) """
        return float(self.data["vg_extent_size"]) * float(self.data["vg_extent_allocated"]) / 1024 / 1024

    @property
    def total(self):
        """ Disk size (GB) """
        return float(self.data["vg_size_kb"]) / 1024 / 1024

class Filesystem:
    def __init__(self, path):
        self.path = path
        self.statvfs = None
        self.refresh()

    def refresh(self):
        self.statvfs = os.statvfs(self.path)

    @property
    def free(self):
        """ Get amount of free space (GB) in filesystem """
        return float(self.statvfs.f_bavail * self.statvfs.f_bsize) / 1024 / 1024 / 1024

    @property
    def used(self):
        """ Get amount of used space (GB) in filesystem """
        return float((self.statvfs.f_blocks - self.statvfs.f_bfree) * self.statvfs.f_frsize) / 1024 / 1024 / 1024

    @property
    def total(self):
        """ Get amount of total space (GB) in filesystem """
        return float(self.statvfs.f_blocks * self.statvfs.f_frsize) / 1024 / 1024 / 1024

class Disk:
    """ Presents single disk """
    def __init__(self, username):
        self.username = username
        self.size = 0
        self._mounted = None
        self.free_space = 0
        self.usepercent = 0
        self.used = 0
        self.inodes = 0
        self.inodes_used = 0
        self.iowait = 0
        self.totalbytes_read = 0
        self.totalbytes_written = 0
        self.yourbytes_read = 0
        self.yourbytes_written = 0

    def exists(self):
        """ Check whether disk exists or not """
        (returncode, output) = run_sudo("lvdisplay", self.username)
        if returncode is 5 or returncode is None or returncode != 0:
            return False
        return True


    def get_lvm_path(self):
        return "%s/%s" % (settings.LVM_ROOT, self.username)

    def get_dir_path(self):
        return "%s/%s" % (settings.DIRECTORIES_ROOT, self.username)

    @require_mounted
    @require_disk
    @cache_disk_func
    def fetch_backups(self):
        """ Get backup information with sudo, as backupmanagement user do not have direct access to user backup files """
        (returncode, output) = run_sudo("fetch_backups", self.username)
        backupset = pickle.loads(output)
        return backupset

    @property
    @require_disk
    def mounted(self):
        if self._mounted is None:
            f = open("/etc/mtab", "r")
            for line in f:
                line = line.split()
                if line[1] == (self.get_dir_path()):
                    self._mounted = True
                    break
            else:
                self._mounted = False
            f.close()
        return self._mounted

    @require_disk
    @cache_disk_func
    def get_info(self):
        """ Load disk information. Depends on specific software version. Expect having this broken in different distributions. """
        (returncode, output) = run_sudo("lvdisplay", self.username)
        if returncode is 5:
            raise Exception("No such disk (%s)" % self.get_lvm_path())
        if returncode is None or returncode != 0:
            raise Exception('Invalid returncode from lvdisplay: %s' %returncode)
        output = output.split(":")
        self.size = int(output[6]) / 2 * 1024 # 1024 / 1024 # in GB

        if self.mounted:
            (returncode, output) = run_sudo("df", self.username)
            if returncode != 0:
                raise Exception("Invalid returncode from df")
            output = output.split("\n")
            output = output[1] # First line is headers
            output = output.split()
            self.used = int(output[2]) * 1024 #/ 1024 / 1024

            (returncode, output) = run_sudo("df", self.username, "inodes")
            if returncode != 0:
                raise Exception("Invalid returncode from df")
            output = output.split("\n")
            output = output[1] # First line is headers
            output = output.split()
            #Filesystem            Inodes   IUsed   IFree IUse% Mounted on
            self.inodes = int(output[1])
            self.inodes_used = int(output[2])
            self.usepercent = round((float(self.used)) / float(self.size) * 100, 2)

    @require_disk
    @cache_disk_func
    def get_waittime(self):
        """ Get disk wait times from /proc/diskstats. Requires dmsetup for mapping dm numbers to usernames """
        f = open("/proc/diskstats", "r")
        (returncode, output) = run_sudo("dmsetup")
        output = output.strip().split("\n")
        id = None
        for device in output:
            if "backupdisks-%s" % self.username in device:
                device = device.split()
                id = device[2].replace(")", "")
        (self.iowait, self.totalbytes_written, read, yread, ywritten) = (0,0,0,0,0) # initialize
        for line in f:
            line = line.split()
            self.iowait += int(line[11])
            self.totalbytes_read += int(line[5])/512/4 * 1024 * 1024 #MB
            self.totalbytes_written += int(line[9])/512/4 * 1024 * 1024 #MB
            if line[2] == "dm-%s" % id:
                self.yourbytes_read = int(line[5])/512/4 * 1024 * 1024#MB
                self.yourbytes_written = int(line[9])/512/4 * 1024 * 1024 #MB
        f.close()
        return {"iowait": self.iowait, "totalbytes_read": self.totalbytes_read, "totalbytes_written": self.totalbytes_written, "yourbytes_read": self.yourbytes_read, "yourbytes_written": self.yourbytes_written}

    @require_disk
    @require_not_mounted
    def mount(self):
        (returncode, _) = run_sudo("mount", self.username)
        if returncode is not 0:
            return False
        return True

    @require_disk
    @require_mounted
    def umount(self):
        (returncode, _) = run_sudo("umount", self.username)
        if returncode is not 0:
            return False
        return True
  
    @require_disk
    def fsck(self):
        """ Run fsck (filesystem check). btrfs do not include working fsck tool. ext4 do not support online fsck (yet). """
        if settings.USE_FILESYSTEM == "btrfs":
            (returncode, _) = run_sudo("fsck-btrfs", self.username)
            if returncode is 0:
                return True
        return False

    @require_disk

    def defragment(self):
        """ Only btrfs requires/includes online defragment program """
        if settings.USE_FILESYSTEM == "btrfs":
            (returncode, _) = run_sudo("defragment-btrfs", self.username)
            if returncode is 0:
                return True
        return False

    @require_no_disk
    def create_storage(self, size):
        """ Creates user storage space and sets up password """

        run_sudo("lvcreate", self.username, size, "backupdisks") # TODO: static path (backupdisks)
        if settings.USE_FILESYSTEM == "ext4":
            run_sudo("mkfs-ext4", self.username)
        elif settings.USE_FILESYSTEM == "btrfs":
            run_sudo("mkfs-btrfs", self.username)
        else:
            raise ImproperlyConfigured("Invalid USE_FILESYSTEM")
        if settings.AUTOMATIC_USER_MANAGEMENT:
            run_sudo("useradd", self.username)
        run_sudo("mkdir", self.username)
        self.mount()
        run_sudo("chown", self.username)
        run_sudo("chmod", self.username)
        run_sudo("setfacl", self.username)
        run_sudo("smbpasswd", self.username, "zooPei7t")
        return True

    @require_disk
    def add_space(self, space):
        """ Add more space to user disk. TODO: progress indicator, as lvextend+resize2fs takes some time. """

        run_sudo("lvextend", self.username, space)
        run_sudo("resize2fs", self.username)
        return True

    @require_disk
    @require_mounted
    def delete_timemachine(self):
        """ Delete timemachine sparse bundle disk """
        (returncode, _) = run_sudo("rm-timemachine", self.username)
        if returncode == 0:
            return True
        return False

    @require_disk
    def delete_disk(self):
        """ Handles deleting the disk """
        if self.mounted:
            (returncode, _) = run_sudo("umount", self.username)
            if returncode != 0:
                return False
        (returncode, _) = run_sudo("lvremove", self.username)
        if returncode != 0:
            return False
        run_sudo("rmdir", self.username)
        if settings.AUTOMATIC_USER_MANAGEMENT:
             run_sudo("deluser", self.username)
        return True

def chpasswd(username, password):
    (returncode, output) = run_sudo("chpasswd", username, password)
    if returncode is not 0:
        raise Exception("Changing password failed with error code %s" % returncode)

    (returncode, output) = run_sudo("smbpasswd", username, password)
    if returncode is not 0:
        raise Exception("Changing smb password failed with error code %s. Output: %s" % (returncode, output))

    return True

