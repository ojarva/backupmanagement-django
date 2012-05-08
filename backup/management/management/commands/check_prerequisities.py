import subprocess
from django.core.management.base import BaseCommand, CommandError
import os.path
from django.conf import settings


class Command(BaseCommand):
    args = "(none)"
    help = "Checks prerequisites for backup management project"

    def check_executables(self, check_sudo=False):
        search_paths = ["/bin", "/sbin", "/usr/bin", "/usr/sbin", "/usr/local/bin", "/usr/local/sbin"]
        required_commands = [("python", True), ("lvdisplay", True), ("df", False), ("dmsetup", True), ("pwgen", False), ("smbpasswd", True), ("mount", True), ("lvcreate", True), ("mkfs.ext4", True), ("mkdir", True), ("chown", True), ("setfacl", True), ("lvextend", True), ("resize2fs", True), ("lvremove", True)]
        if settings.AUTOMATIC_USER_MANAGEMENT:
             required_commands += [("useradd", True), ("deluser", True)]
        for (command, sudo) in required_commands:
            for path in search_paths:
                if os.path.exists("%s/%s" % (path, command)):
                    if check_sudo and sudo:
                        print "Testing sudo %s/%s" % (path, command)
                        p = subprocess.Popen(["sudo", "%s/%s" % (path, command), "-h"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        p.communicate()
                        if p.returncode != 0:
                            print "%s sudo configuration is wrong." % command
                    break
            else:
                if not check_sudo:
                    print "Couldn't find %s, which is required for correct operation." % command            

    def check_paths(self):
        if not os.path.exists(settings.LVM_ROOT) or not os.path.isdir(settings.LVM_ROOT):
            print "LVM_ROOT doesn't exist or it's not a directory. Please check. Current value is %s" % settings.LVM_ROOT
        if not os.path.exists(settings.DIRECTORIES_ROOT) or not os.path.isdir(settings.DIRECTORIES_ROOT):
            print "DIRECTORIES_ROOT doesn't exist or it's not a directory. Please check. Current value is %s" % settings.DIRECTORIES_ROOT

    def handle(self, *args, **options):
        print "Testing executables:"
        self.check_executables()
        print "Testing sudoers configuration; if program hangs, you have wrong sudo configuration. Just press control+c and figure out what's wrong. If sudo asks for password, you have wrong configuration."
        self.check_executables(True)

        self.check_paths()
