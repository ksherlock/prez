
import sys
import io
import argparse
import time

from base import rObject

# from base import *
# from window import *
# from control import *
# from menu import *
# from sound import *
# from rect import rect, point, size


def rez_scope():
	import base
	import window
	import control
	import menu
	import sound
	import rect

	scope = {}
	for mod in (base, window, control, menu, sound, rect):

		if hasattr(mod, '__all__'): keys = mod.__all__
		else: keys = [x for x in dir(mod) if x[0] != '_']

		for key in keys:
			scope[key] = getattr(mod, key)

	return scope

		

def execute(filename):
	scope = rez_scope()
	try:
		with open(filename, 'r', encoding="utf-8") as f:
			src = f.read()
			code = compile(src, filename, "exec")
			exec(code, {}, scope)
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
        rObject.dump_rez()

        rObject.dump_exports()
        sys.exit(0)
