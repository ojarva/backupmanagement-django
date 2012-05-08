#!/usr/bin/env python
import subprocess
from wrappers_settings import *
import sys
(stdout, _) = run_command(["dmsetup", "ls"])
print stdout
sys.exit(0)
