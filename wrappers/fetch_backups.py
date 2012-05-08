#!/usr/bin/env python
import subprocess
from wrappers_settings import *
import sys
import os.path
if len(sys.argv) > 1:
   path = check_username(sys.argv[1])
   (stdout, stderr) = run_command(["/usr/bin/python", "%s/fetch_backups_lib.py" % os.path.join(os.path.dirname(__file__)), path])
   print stdout
   sys.exit(0)
sys.exit(255)
