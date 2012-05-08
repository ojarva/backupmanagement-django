""" 
This is small wrapper for getting backup information.
It searches for Windows 7 backup files (probably also Vista and Windows 2008, no idea about Windows 8),
Mac OS X Time Machine backups and rdiff-backup files

Output is printed through pickle.
"""

import sys
import datetime
import pickle
from glob import iglob
import os
from wrappers_settings import *

class BackupInfo():
    """ Represents single backup """
    def __init__(self):
        self.size = None
        self.timestamp = None
        self.age = None
        self.format = None
        self.path = None
        self.machine = None
    def get_age(self):
        return datetime.datetime.now() - self.timestamp

class BackupSet():
    """ Represents set of backups from single source """
    def __init__(self):
        self.total_size = None
        self.backups = []
        self.cleartext = None
    def add(self, backup):
        self.backups.append(backup)
    def get_backups(self):
        return sorted(self.backups, key=lambda backupinfo: backupinfo.timestamp)

def fetch_backupinfo(username):
    # Unfortunately this is not going through Django, so no django.conf available.
    folder = "%s/%s" % (DIRECTORIES_ROOT, username)
    info = ""
    backupset = BackupSet()
    for file in iglob(folder+"/*"):
       if os.path.exists("%s/Desktop.ini" % file) and os.path.exists("%s/MediaID.bin" % file):
           info += "Windows Backup: "+file.replace(folder+"/", "")+"\n"
           machine_name = file.replace(folder+"/", "")
           format = "Windows Backup"
           for backups in iglob(file+"/Backup Set *"):
               for backup in iglob(backups+"/Backup Files *"):
                   timestr = backup.replace(backups+"/", "").replace("Backup Files ", "").strip()
                   timestamp = datetime.datetime.strptime(timestr, "%Y-%m-%d %H%M%S")
                   backupinfo = BackupInfo()
                   backupinfo.timestamp = timestamp
                   backupinfo.format = format
                   backupinfo.machine = machine_name
                   backupinfo.path = backup
                   backupset.add(backupinfo)
                   info += "Backup @%s, %s ago\n" % (timestamp, datetime.datetime.now() - timestamp)
       if "WindowsImageBackup" in file:
           for computer in iglob(file+"/*"):
               id = computer.replace(file+"/", "")
               info += "Windows Restore Image: %s\n" % id
               machine_name = id
               format = "Windows Restore Image"
               for backups in iglob(computer+"/*"):
                   if "Backup " in backups:
                       timestr = backups.replace(computer+"/", "").replace("Backup ", "").strip()
                       timestamp = datetime.datetime.strptime(timestr, "%Y-%m-%d %H%M%S")
                       backupinfo = BackupInfo()
                       backupinfo.timestamp = timestamp
                       backupinfo.format = format
                       backupinfo.machine = machine_name
                       backupinfo.path = backups
                       backupset.add(backupinfo)
                       info += "Backup @%s, %s ago\n" % (timestamp, datetime.datetime.now() - timestamp)
       if os.path.exists("%s/com.apple.TimeMachine.MachineID.plist" % file) and os.path.exists("%s/bands" % file):
           machine_name = file.replace(folder+"/", "").replace(".sparsebundle", "")
           format = "Time Machine Backup"
           mtime = 0
           for band in iglob(file+"/bands/*"):
               stat = os.stat(band)
               if stat.st_mtime > mtime:
                   mtime = stat.st_mtime
           info += "Time machine backup: "+file.replace(folder+"/", "").replace(".sparsebundle", "")+"\n"
           info += "Age of last modification to backup: "+str(datetime.datetime.now() - datetime.datetime.fromtimestamp(mtime))+"\n"
           backupinfo = BackupInfo()
           backupinfo.timestamp = datetime.datetime.fromtimestamp(mtime)
           backupinfo.format = format
           backupinfo.machine = machine_name
           backupinfo.path = folder
           backupset.add(backupinfo)
       if "backintime" in file:
           machine_name = "unknown"
           format = "Back in Time (Linux)"
           info += "Back in Time\n"
           for backup in iglob(file+"/????????-??????"):
               timestr = backup.replace(file+"/", "")
               timestamp = datetime.datetime.strptime(timestr, "%Y%m%d-%H%M%S")
               info += "Backup @%s, %s ago\n" % (timestamp, datetime.datetime.now() - timestamp)
               backupinfo = BackupInfo()
               backupinfo.timestamp = timestamp
               backupinfo.format = format
               backupinfo.machine = machine_name
               backupinfo.path = backup
               backupset.add(backupinfo)
       if os.path.exists(file+"/rdiff-backup-data"):
           machine_name = "unknown"
           format = "rdiff-backup"
           info += "rdiff-backup\n"
           for backup in iglob(file+"/rdiff-backup-data/file_statistics.*.data.gz"):
               timestr = backup.replace(file+"/rdiff-backup-data/file_statistics.", "").replace(".data.gz", "").split("+")[0]
               timestamp = datetime.datetime.strptime(timestr, "%Y-%m-%dT%H:%M:%S")
               info += "Backup @%s, %s ago\n" % (timestamp, datetime.datetime.now() - timestamp)
               backupinfo = BackupInfo()
               backupinfo.timestamp = timestamp
               backupinfo.format = format
               backupinfo.machine = machine_name
               backupinfo.path = backup
               backupset.add(backupinfo)
               
    backupset.cleartext = info
    return backupset

if __name__ == '__main__':
    username = sys.argv[1]
    backupset = fetch_backupinfo(username)
    # Print to caller, which then unpickles results
    print pickle.dumps(backupset)
