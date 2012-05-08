#!/usr/bin/env python
import subprocess
from wrappers_settings import *
import sys
if len(sys.argv) > 3:
   path = check_username(sys.argv[1])
   size = sys.argv[2]
   lvm_name = sys.argv[3]
   run_command(["lvcreate", "-n", path, "-L%sG" % size, lvm_name])
   sys.exit(0)
sys.exit(255)
