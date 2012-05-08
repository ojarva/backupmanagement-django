import subprocess
import sys
import re

LVM_ROOT="/dev/backupdisks"
DIRECTORIES_ROOT="/srv/userbackup"

def run_command(args, fatal=True):
    args = [ str(a) for a in args ]
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = p.communicate()
    if p.returncode is not 0 and fatal:
        print stdout, stderr
        sys.exit(p.returncode)
    return (stdout, stderr)

def check_username(username):
    invalid_usernames = ["root", "admin", "wheel", "www-data", "apache2"]
    if username in invalid_usernames:
        print "Invalid username"
        sys.exit(6)
    p = re.compile('[A-Za-z0-9-_]+')
    if p.match(username):
        return username
    else:
        print "Invalid characters in username"
        sys.exit(7)
