
import sys
import io
import argparse
import time

from base import *
from window import *
from control import *
from menu import *
from rect import rect, point, size

def execute(filename):
	try:
		with open(filename, 'r', encoding="utf-8") as f:
			src = f.read()
			code = compile(src, filename, "exec")
			exec(code, None, {})
			return True
		pass
	except Exception as e:
		print(e)
		return False

if __name__ == '__main__':
        p = argparse.ArgumentParser(prog='prez')
        p.add_argument('files', metavar='file', type=str, nargs='+')
        p.add_argument('--rez', action='store_true',
        	help="Generate REZ code")
        opts = p.parse_args()

        for f in opts.files:
        	ok = execute(f)


        print("/* Generated on {} */".format(time.ctime()))
        print('#include "types.rez"\n')
        rObject.dumprez()
        sys.exit(0)
