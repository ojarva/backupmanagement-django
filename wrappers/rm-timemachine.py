#!/usr/bin/env python
import subprocess
import glob
from wrappers_settings import *
import sys
if len(sys.argv) > 1:
   path = check_username(sys.argv[1])
   sparsebundles = glob.glob("%s/%s/*.sparsebundle" % (DIRECTORIES_ROOT, path))
   for sp in sparsebundles:
       run_command(["rm", "-r", sp], False)
   sys.exit(0)
sys.exit(255)
