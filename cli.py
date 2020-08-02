
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
	# import all the resource types and constants into
	# a dictionary to be the exec() local scope
	import base
	import window
	import control
	import menu
	import sound
	import rect
	import constants

	# could do: mod = importlib.import_module("base"), etc.
	scope = {}
	for mod in (base, window, control, menu, sound, rect, constants):
		if hasattr(mod, '__all__'): keys = mod.__all__
		else: keys = [x for x in dir(mod) if x[0] != '_']

		for key in keys:
			scope[key] = getattr(mod, key)

	return scope

		

def execute(filename, scope):
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
	p.add_argument('--rez', action='store_true', help="Generate REZ code")
	p.add_argument('-D', type=str, nargs='+', help='define a variable')
	p.add_argument('--df', action="store_true", help="Write to a regular file")
	p.add_argument('-o', metavar='file', type=str, help="Specify output file")

	opts = p.parse_args()

	scope = rez_scope()
	for f in opts.files:
		ok = execute(f, scope)


	print("/* Generated on {} */".format(time.ctime()))
	print('#include "types.rez"\n')
	rObject.dump_rez()

	rObject.dump_exports()
	sys.exit(0)
