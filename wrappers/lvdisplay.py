#!/usr/bin/env python
import subprocess
from wrappers_settings import *
import sys
if len(sys.argv) > 1:
   path = check_username(sys.argv[1])
   (stdout, _) = run_command(["lvdisplay", "-c", "%s/%s" % (LVM_ROOT, path)])
   print stdout
   sys.exit(0)
sys.exit(255)
