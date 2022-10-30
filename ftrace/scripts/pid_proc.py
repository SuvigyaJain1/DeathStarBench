import os
import sys
import subprocess

trace_file = sys.argv[1]
pid = sys.argv[2]

output = subprocess.getoutput(f"cat {trace_file} | grep {pid}")
print(''.join(output.split("\n")[0].split()[1].split("-")[:-1]))