import struct
from bisect import bisect_left
from rect import *
from utils import *

__all__ = ["rObject", "rText", "rTextBlock", "rTextForLETextBox2", 
	"rAlertString", "rErrorString", "rComment", "rPString", 
	"rCString", "rWString", "rC1InputString", "rStringList",
	"rTwoRects", "rRectList"]

#define KeyEquiv  array[1]{ char; char; _mybase_ word; _mybase_ word; }

# ( "Ss", 0x..., 0x.... )

class rObject:
	rName = None
	rType = None
	rRange = range(1,0x07FF0000)

	_rmap = {}
	_resources = {}

	# also a define=property to trigger export in equ file?
	def __init__(self, id=None, attr=None):
		rType = self.rType
		self.id = id
		self.attr = attr

		self._check_id(rType, id)

	def _check_id(self, rType, rID):

		if rType in self._resources:
			xx = self._resources[rType]
		else:
			xx = []
			self._resources[rType] = xx
		xx.append(self)

		if type(rID) == int:
			if rType in self._rmap:
				xx = self._rmap[rType]
			else:
				xx = set()
				self._rmap[rType] = xx

			if rID in xx:
				raise ValueError("{} (${:04x}) ${:08x} already defined".format(self.rName, rType, rID))


	def get_id(self):
		rID = self.id
		rType = self.rType
		if type(rID) == int: return rID


		if rType in self._rmap:
			xx = self._rmap[rType]
		else:
			xx = set()
			self._rmap[rType] = xx

		used = list(xx)
		used.sort()


		rr = self.rRange
		if type(rID) == range:
			rr = rID

		ix = bisect_left(used, rr.start)

		for rID in rr:
			if ix >= len(used) or used[ix] > rID :
				self.id = rID
				xx.add(self.id)
				return self.id
			ix += 1
		raise Exception("Unable to allocate id for resource")

		# # just append
		# if len(xx) == 0:
		# 	self.id = 1
		# 	xx.add(self.id)
		# 	return self.id

		# rID = used[-1] + 1
		# self.id = rID
		# xx.add(self.id)
		# return self.id

	@staticmethod
	def dump():
		for rType,rList in rObject._resources.items():
			for r in rList:
				print("${:04x} {} - ${:08x}".format(rType, r.rName, r.get_id()))


	@staticmethod
	def dumphex():
		for rType,rList in rObject._resources.items():
			for r in rList:
				bb = bytes(r)

				data = [bb[x*16:x*16+16] for x in range(0, len(bb)+15>>4)]

				print("{}(${:08x}) {{".format(r.rName, r.get_id()))
				for x in data:
					print("\t$\"" + x.hex() + "\"")
				print("}\n")

	@staticmethod
	def dumprez():
		for rType,rList in rObject._resources.items():
			for r in rList:
				content = r._rez_string()

				print("{}(${:08x}) {{".format(r.rName, r.get_id()))
				print(content)
				print("}\n")

# container for a 0-terminated list of resource ids.

class rList(rObject):
	def __init__(self, *children, id=None, attr=None):
		super().__init__(id=id, attr=attr)
		self.children = children
		tt = self.rChildType
		for x in self.children:
			if not isinstance(x, tt):
				raise TypeError("bad type: {}".format(type(x)))

	def __bytes__(self):
		bb = bytearray(4 + len(self.children) * 4)
		offset = 0
		for x in self.children:
			struct.pack_into("<I", bb, offset, x.get_id())
			offset += 4
		return bytes(bb)

	def _rez_string(self):
		if not self.children: return "\t{}"
		rv = "\t{\n"

		ids = [x.get_id() for x in self.children]

		rv += ",\n".join(["\t\t${:08x}".format(x) for x in ids])

		rv += "\n\t}"
		return rv


def _generate_map():
	map = { x: "\\${:02x}".format(x) for x in range(0, 256) if x < 32 or x > 126 }
	map[0x0d] = "\\n" # intentionally backwards.
	map[0x0a] = "\\r" # intentionally backwards.
	map[0x09] = "\\t"
	# \b \f \v \? also supported. 
	map[ord('"')] = '\\"'
	map[ord("'")] = "\\'"
	map[ord("\\")] = "\\\\"
	# map[0x7f] = "\\?" # rubout

	return map

class rTextObject(rObject):
	# _map = { x: "\\${:02x}".format(x) for x in range(0, 256) if x < 32 or x > 126 }



	_map = _generate_map()

	@staticmethod
	def _encode(bb):
		map = rTextObject._map
		return "".join([map[x] if x in map else chr(x) for x in bb])

	@classmethod
	def make_string(cls, text):
		rType = cls
		# if not rType: rType = rPString
		if type(text) == rType: return text
		if type(text) in (str, bytes, bytearray): return rType(text)
		raise TypeError("Bad text type: {}".format(type(text)))





	def __init__(self, text, *, id=None, attr=None):
		super().__init__(id=id, attr=attr)
		# text is a string or bytes.
		# bytes is assumed to be macroman
		self.text = text
		self._text = str_to_bytes(text)

	def __len__(self):
		return len(self._text)

	def __bytes__(self):
		return self._text

	def _rez_string(self):

		if not self._text: return '\t""\n'

		bb = self._text
		data = [bb[x*32:x*32+32] for x in range(0, len(bb)+31>>5)]

		rv = ""
		rv = "\n".join(['\t"' + self._encode(x) + '"' for x in data])
		return rv


class rText(rTextObject):
	rName = "rText"
	rType = 0x8016

class rTextBlock(rTextObject):
	rName = "rTextBlock"
	rType = 0x8011

class rTextForLETextBox2(rTextObject):
	rName = "rTextForLETextBox2"
	rType = 0x800b

class rAlertString(rTextObject):
	rName = "rAlertString"
	rType = 0x8015

class rErrorString(rTextObject):
	rName = "rErrorString"
	rType = 0x8020

class rComment(rTextObject):
	rName = "rComment"
	rType = 0x802a

class rPString(rTextObject):
	rName = "rPString"
	rType = 0x8006

	def __bytes__(self):
		bb = super().__bytes__()
		return struct.pack("<B", len(bb)) + bb


class rCString(rTextObject):
	rName = "rCString"
	rType = 0x801d

	def __bytes__(self):
		bb = super().__bytes__()
		return bb + b"\x00"

class rWString(rTextObject):
	rName = "rWString"
	rType = 0x8022

	def __bytes__(self):
		bb = super().__bytes__()
		return struct.pack("<H", len(bb)) + bb


class rC1InputString(rTextObject):
	rName = "rC1InputString"
	rType = 0x8023

	def __bytes__(self):
		bb = super().__bytes__()
		return struct.pack("<H", len(bb)) + bb

class rStringList(rObject):
	rName = "rStringList"
	rType = 0x8007

	def __init__(self, strings, *, id=None, attr=None):
		super().__init__(id, attr)
		self.strings = strings[:]
		self._strings = [str_to_bytes(x) for x in strings]

	def __bytes__(self):
		bb = struct.pack("<H", len(self._strings))
		for x in self._strings:
			bb += x
		return bb




class rTwoRects(rObject):
	rName = "rTwoRects"
	rType = 0x801a

	def __init__(self, r1, r2, *, id=None, attr=None):
		super().__init__(id=id, attr=attr)
		self.r1 = r1
		self.r2 = r2

	def __bytes__(self):
		return struct.pack("<4H4H", *self.r1, *self.r2)

	def _rez_string(self):
		return (
			"\t{{ {:d}, {:d}, {:d}, {:d} }},\n"
			"\t{{ {:d}, {:d}, {:d}, {:d} }}\n"
		).format(*self.r1, *self.r2)

class rRectList(rObject):
	rName = "rRectList"
	rType = 0xc001

	def __init__(self, *rects, id=None, attr=None):
		super().__init__(id=id, attr=attr)
		self.rects = rects

	def __bytes__(self):
		bb = struct.pack("<H", len(self.rects))
		for x in self.rects:
			bb += struct.pack("<4H", *x)
		return bb

	def _rez_string(self):
		rv = "\t{\n"

		fx = lambda x: "\t\t{{ {:d}, {:d}, {:d}, {:d} }}".format(*x)

		rv += ",\n".join([fx(x) for x in self.rects])

		if self.rects: rv += "\n"
		rv += "\t}"
		return rv;
