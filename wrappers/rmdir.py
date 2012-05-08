#!/usr/bin/env python
from wrappers_settings import *
import sys
if len(sys.argv) > 1:
   path = check_username(sys.argv[1])
   run_command(["rmdir", "%s/%s" % (DIRECTORIES_ROOT, path)])
   sys.exit(0)
sys.exit(255)
