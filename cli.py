
import sys
import io
import argparse
import time
from open_rfork import open_rfork
import traceback

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
	import version
	import constants

	# could do: mod = importlib.import_module("base"), etc.
	scope = {}
	for mod in (base, window, control, menu, sound, rect, version, constants):
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

if __name__ == '__main__':
	p = argparse.ArgumentParser(prog='prez')
	p.add_argument('files', metavar='file', type=str, nargs='+')
	p.add_argument('--rez', action='store_true', help="Generate REZ code")
	p.add_argument('-x', action="store_true", help="Generate REZ data")

	p.add_argument('-D', type=str, nargs='+', help='define a variable')
	p.add_argument('--df', action="store_true", help="Write to a regular file")
	p.add_argument('-o', metavar='file', type=str, help="Specify output file")

	opts = p.parse_args()


	df = opts.df or not sys.platform in ("win32", "darwin")


	scope = rez_scope()
	errors = 0
	for f in opts.files:
		ok = execute(f, scope)
		if not ok: errors += 1

	if errors > 0 : sys.exit(1)

	if not opts.o: opts.rez = True
	if opts.x: opts.rez = True

	if df or opts.rez:
		open_rfork = io.open

	if opts.rez:
		print("/* Generated on {} */".format(time.ctime()))
		print('#include "types.rez"\n')
		if opts.x: rObject.dump_hex()
		else: rObject.dump_rez()
	else:
		with open_rfork(opts.o, "wb") as io:
			rObject.save_resources(io)

	rObject.dump_exports()
	sys.exit(0)
