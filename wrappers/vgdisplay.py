#!/usr/bin/env python
import subprocess
from wrappers_settings import *
import sys
if len(sys.argv) == 1:
   path = LVM_ROOT
   (stdout, _) = run_command(["vgdisplay", "-c", path])
   print stdout
   sys.exit(0)
sys.exit(255)
