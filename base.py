import struct
from bisect import bisect_left
from rect import *
from utils import *
import sys

from resource_writer import ResourceWriter

from constants import *

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
	_rnames = {}

	def __init__(self, id=None, attr=0, **kwargs):
		rType = self.rType


		if kwargs.get("attrPage", False): attr |= attrPage
		if kwargs.get("attrNoSpec", False): attr |= attrNoSpec
		if kwargs.get("attrNoCross", False): attr |= attrNoCross
		if kwargs.get("resPreLoad", False): attr |= resPreLoad
		if kwargs.get("resProtected", False): attr |= resProtected
		if kwargs.get("attrPurge1", False): attr |= attrPurge1
		if kwargs.get("attrPurge2", False): attr |= attrPurge2
		if kwargs.get("attrPurge3", False): attr |= attrPurge3
		if kwargs.get("resAbsLoad", False): attr |= resAbsLoad
		if kwargs.get("resConverter", False): attr |= resConverter
		if kwargs.get("attrFixed", False): attr |= attrFixed
		if kwargs.get("attrLocked", False): attr |= attrLocked

		if kwargs.get("attrPurge", False): attr |= attrPurge

		self._id = id
		self._attr = attr

		self._export = None
		self._name = None

		self._check_id()

		if "export" in kwargs: self._export = kwargs["export"]
		if "name" in kwargs: 
			self.name(kwargs["name"])


	def _check_id(self):

		rType = self.rType
		rID = self._id

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


	def name(self, name):
		if not name: return

		self._name = name

		rType = self.rType
		if self.rType in self._rnames:
			r = self._rnames[rType]
		else:
			r = rResName(id = 0x00010000 + rType)
			self._rnames[rType] = r

		r.add(self)

		return self

	def export(self, name):
		self._export = name
		return self

	# .attr(attrNoSpec, attrLocked, attrFixed)
	# .attr(attrNoSpec + attrLocked + attrFixed)
	def attr(self, *attrs):
		for x in attrs:
			self._attr |= x
		return self

	def get_id(self):
		rID = self._id
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
	def dump_exports(type="c", io=None):
		type = type.lower()
		if type not in ("c", "equ", "gequ"): return

		fmt = {
			"c": "#define {} 0x{:08x}",
			"equ": "{} equ ${:08x}",
			"gequ": "{} gequ ${:08x}",
		}[type]

		for rType,rList in rObject._resources.items():
			for r in rList:
				if r._export:
					print(fmt.format(r._export, r.get_id()), file=io)

	def _format_attr(self):
		attr = self._attr
		if not attr: return ""
		opts = [""]
		if attr & attrPage: opts.append("attrPage")   
		if attr & attrNoSpec: opts.append("attrNoSpec") 
		if attr & attrNoCross: opts.append("attrNoCross")
		if attr & resPreLoad: opts.append("resPreLoad")
		if attr & resProtected: opts.append("resProtected")
		if attr & attrPurge1: opts.append("attrPurge1")
		if attr & attrPurge2: opts.append("attrPurge2")
		if attr & attrPurge3: opts.append("attrPurge3")
		if attr & resAbsLoad: opts.append("resAbsLoad")
		if attr & resConverter: opts.append("resConverter")
		if attr & attrFixed: opts.append("attrFixed")
		if attr & attrLocked: opts.append("attrLocked")
		return ", ".join(opts)

	@staticmethod
	def dump(io=None):
		for rType,rList in rObject._resources.items():
			for r in rList:
				print("${:04x} {} - ${:08x}".format(rType, r.rName, r.get_id()), file=io)


	@staticmethod
	def dump_hex(io=None):
		for rType,rList in rObject._resources.items():
			for r in rList:
				bb = bytes(r)

				data = [bb[x*16:x*16+16] for x in range(0, len(bb)+15>>4)]

				print("data {}(0x{:08x}{}) {{".format(
					r.rName, r.get_id(), r._format_attr()
				), file=io)
				for x in data:
					print("\t$\"" + x.hex() + "\"", file=io)
				print("}\n", file=io)

	@staticmethod
	def dump_rez(io=None):
		for rType,rList in rObject._resources.items():
			for r in rList:
				content = r._rez_string()

				print("resource {}(0x{:08x}{}) {{".format(
					r.rName, r.get_id(), r._format_attr()
				), file=io)
				print(content, file=io)
				print("}\n", file=io)


	@staticmethod
	def save_resources(io):
		rw = ResourceWriter()

		for rType,rList in rObject._resources.items():
			if rType == 0x8014: continue # rResName handled via rw

			for r in rList:

				rw.add_resource(
					rType,
					r.get_id(),
					bytes(r),
					attr = r._attr,
					name = r._name
				)

		rw.write(io)



# container for a 0-terminated list of resource ids.
# NOT EXPORTED BY DEFAULT
class rList(rObject):
	def __init__(self, *children, **kwargs):
		super().__init__(**kwargs)
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

		rv += ",\n".join(["\t\t0x{:08x}".format(x) for x in ids])

		rv += "\n\t}"
		return rv

# NOT EXPORTED BY DEFAULT
# id = 0x0001xxxx where xxxx = resource type
#
class rResName(rObject):
	rName = "rResName"
	rType = 0x8014

	def __init__(self, id, attr=None):
		super().__init__(id=id, attr=attr)
		self.children = []

	def add(self, r):
		self.children.append(r)

	def __bytes__(self):
		count = len(self.children)
		bb = struct.pack("<HI",
			1, # version
			count
		)
		for x in self.children:
			name = str_to_bytes(x._name)
			id = x.get_id()
			bb += struct.pack("<IB", id, len(name))
			bb += str_to_bytes(name)

		return bb

	def _rez_string(self):
		rv = "\t1, /* version */\n\t{\n"

		tmp = [
			"\t\t0x{:08x},\n\t\t{}".format(
				x.get_id(), format_string(str_to_bytes(x._name))
			)
			for x in self.children
		]

		rv += ",\n".join(tmp)
		rv += "\n\t}"
		return rv

# NOT EXPORTED BY DEFAULT
# abstract parent for text objects.
class rTextObject(rObject):

	@classmethod
	def make_string(cls, text):
		rType = cls
		# if not rType: rType = rPString
		if type(text) == rType: return text
		if type(text) in (str, bytes, bytearray): return rType(text)
		raise TypeError("Bad text type: {}".format(type(text)))



	def __init__(self, *text, **kwargs): # id=None, attr=None):
		super().__init__(**kwargs) # id=id, attr=attr
 		# text is a string or bytes.
		# bytes is assumed to be macroman
		# self.text = str_to_bytes(text)

		self.text = b"".join([str_to_bytes(x) for x in text])

	def __len__(self):
		return len(self.text)

	def __bytes__(self):
		return self.text

	def _rez_string(self):

		if not self.text: return '\t""\n'

		return multi_format_string(self.text, "\t")


class rText(rTextObject):
	rName = "rText"
	rType = 0x8016

class rTextBlock(rTextObject):
	rName = "rTextBlock"
	rType = 0x8011

class rTextForLETextBox2(rTextObject):
	rName = "rTextForLETextBox2"
	rType = 0x800b

# TODO - rAlertString and rError string are
# both formatted c-strings used by AlertWindow.
# see TB 3 52-6.  size, optional icon, text, buttons.
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

	def __init__(self, *strings, **kwargs):
		super().__init__(**kwargs)
		self.children = [str_to_bytes(x) for x in strings]

	def __bytes__(self):
		bb = struct.pack("<H", len(self.children))
		for x in self.children:
			bb += bytes( [len(x)] ) # pstring
			bb += x
		return bb

	def _rez_string(self):
		rv = "\t{\n"
		rv += ",\n".join([multi_format_string(x, "\t\t") for x in self.children])
		if self.children: rv += "\n"
		rv += "\t}"
		return rv



class rTwoRects(rObject):
	rName = "rTwoRects"
	rType = 0x801a

	def __init__(self, r1, r2, **kwargs):
		super().__init__(**kwargs)
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

	def __init__(self, *rects, **kwargs):
		super().__init__(**kwargs)
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
