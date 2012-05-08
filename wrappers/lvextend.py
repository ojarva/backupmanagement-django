#!/usr/bin/env python
import subprocess
from wrappers_settings import *
import sys
if len(sys.argv) > 2:
   path = check_username(sys.argv[1])
   space = sys.argv[2]
   space = space.replace(".", "").replace("-", "")
   run_command(["lvextend", "-L", "+%sG" % space, "%s/%s" % (LVM_ROOT, path)])
   sys.exit(0)
sys.exit(255)
