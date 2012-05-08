#!/usr/bin/env python
import subprocess
from wrappers_settings import *
import sys
if len(sys.argv) > 2:
    username = check_username(sys.argv[1])
    password = sys.argv[2]
    p = subprocess.Popen(["smbpasswd", "-s", "-a", username], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (_, _) = p.communicate("%s\n%s\n" % (password, password))
    if p.returncode is not 0:
        sys.exit(3)
    sys.exit(0)
sys.exit(255)
