
import sys
import io
import argparse
import time
import traceback
import importlib

from . open_rfork import open_rfork
from . base import rObject


# from base import *
# from window import *
# from control import *
# from menu import *
# from sound import *
# from rect import rect, point, size


def rez_scope():
	# import all the resource types and constants into
	# a dictionary to be the exec() local scope
	# import prez.base
	# import prez.window
	# import prez.control
	# import prez.menu
	# import prez.sound
	# import prez.rect
	# import prez.version
	# import prez.tool_startup
	# import prez.icon
	# import prez.constants

	# could do: mod = importlib.import_module("base"), etc.
	scope = {}
	for m in ('base', 'window', 'control', 'menu', 'sound', 'rect', 'version', 'tool_startup', 'icon', 'constants'):
		mod = importlib.import_module('.' + m, 'prez')
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
		print(traceback.format_exc())
		return False

def main():

	p = argparse.ArgumentParser(prog='prez')
	p.add_argument('files', metavar='file', type=str, nargs='+')
	p.add_argument('--rez', action='store_true', help="Generate REZ code")
	p.add_argument('--hex', action="store_true", help="Generate REZ data")

	p.add_argument('-D', type=str, nargs='+', help='define a variable')
	p.add_argument('--data-fork', action="store_true", help="Write to a regular file")
	p.add_argument('-o', metavar='file', type=str, help="Specify output file")

	opts = p.parse_args()

	opts.data_fork = opts.data_fork or not sys.platform in ("win32", "darwin")


	scope = rez_scope()
	errors = 0
	for f in opts.files:
		ok = execute(f, scope)
		if not ok: errors += 1

	if errors > 0 : sys.exit(1)

	if not opts.o: opts.rez = True

	if opts.rez or opts.hex:
		print("/* Generated on {} */".format(time.ctime()))
		print('#include "types.rez"\n')
		if opts.hex: rObject.dump_hex()
		else: rObject.dump_rez()
	else:
		opener = open_rfork
		if opts.data_fork: opener = io.open
		with opener(opts.o, "wb") as f:
			rObject.save_resources(f)

	rObject.dump_exports()
	sys.exit(0)

if __name__ == '__main__':
	main()
