#!/usr/bin/env python
import subprocess
from wrappers_settings import *
import sys
if len(sys.argv) > 1:
   path = check_username(sys.argv[1])
   if len(sys.argv) > 2:
       # Inodes
       (stdout, stderr) = run_command(["df", "-P", "-i", "%s/%s" % (DIRECTORIES_ROOT, path)])
   else:
       # File sizes
       (stdout, stderr) = run_command(["df", "-P", "%s/%s" % (DIRECTORIES_ROOT, path)])
   print stdout
   sys.exit(0)
sys.exit(255)

