#!/usr/bin/python
from django.core.management import execute_manager

import datetime
""" Really ugly hack to fix problems with unpickle. Should probably migrate to JSON for transferring data between separate python programs """
class BackupInfo():
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
    def __init__(self):
        self.total_size = None
        self.backups = []
        self.cleartext = None
    def add(self, backup):
        self.backups.append(backup)
    def get_backups(self):
        tmp = sorted(self.backups, key=lambda backupinfo: backupinfo.timestamp)
        tmp.reverse()
        return tmp

try:
    import settings # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

if __name__ == "__main__":
    execute_manager(settings)
