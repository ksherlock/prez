
from base import rObject
from utils import *
import enum
import struct

__all__ = ["rToolStartup"]

# can't be in utils since that's a different __all__
def export_enum(cls):
	global __all__

	members = cls.__members__
	globals().update(members)
	if __all__ != None: __all__.extend(list(members))
	return cls	


@export_enum
class Flags(enum.Flag):
	mode320 = 0
	mode640 = 0x80
	fFastPortAware = 0x4000
	fUseShadowing = 0x8000

class rToolStartup(rObject):
	"""
		mode: 320 or 640
		tools: tool number or (tool number, version)
	"""
	rName = "rToolStartup"
	rType = 0x8013


	# mode | 0x4000 - fastport aware
	# mode | 0x8000 - hardware shadowing
	def __init__(self, mode, *tools, **kwargs):
		super().__init__(**kwargs)

		if type(mode) == Flags: mode = mode.value
		elif type(mode) == int: pass
		else: raise TypeError("rToolStartup: bad mode: {} ({})".format(mode, type(mode)))
		self.mode = mode

		for x in tools:
			if type(x) == int: continue
			if type(x) == tuple and len(x) == 2:
				a,b = x
				if type(a) == int and type(b) == int: continue
			raise TypeError("rToolStartup: bad tool: {}".format(x))

		self.tools = [x if type(x) == tuple else (x, 0) for x in tools]



	def __bytes__(self):
		bb = struct.pack("<HHHIH",
			0, # flags,
			self.mode,
			0, 0,
			len(self.tools)
		)

		for a,b in self.tools:
			bb += struct.pack("<HH", a, b)

		return bb

	def _rez_string(self):
		mode = None
		if self.mode in (0x00, 0x80):
			mode = {0x00: "mode320", 0x80: "mode640"}[self.mode]
		else:
			mode = "0x{:04x}".format(self.mode)

		rv = (
			"\t{}, /* mode */\n"
			"\t{{\n".format(
				mode
			))

		tmp = []
		for a, b in self.tools:
			tmp.append("\t\t{}, 0x{:04x}".format(a, b))

		rv += ",\n".join(tmp)

		if self.tools: rv += "\n"
		rv += "\t}"
		return rv
