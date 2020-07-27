import struct
from bisect import bisect_left
from rect import rect, point

# helper functions
def str_to_bytes(text):
	if isinstance(text, str): return text.encode("macroman")
	if isinstance(text, bytes): return text
	if isinstance(text, bytearray): return bytes(text)
	raise TypeError("Bad text type: {}".format(type(text)))


def make_string(text, rType=None):
	if not rType: rType = rPString
	if type(text) == rType: return text
	if type(text) in (str, bytes, bytearray): return rType(text)
	raise TypeError("Bad text type: {}".format(type(text)))


#define KeyEquiv  array[1]{ char; char; _mybase_ word; _mybase_ word; }

# ( "Ss", 0x..., 0x.... )

class rObject:
	rName = None
	rType = None

	_rmap = {}
	_resources = {}

	# also a define=proeprty to trigger export in equ file?
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


		rr = range(1,0x07FEFFFF)
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
				print("{}(${:08x}) {{".format(r.rName, r.get_id()))
				print("\t$\"" + bb.hex() + "\"")
				print("}\n")

	@staticmethod
	def dumprez():
		for rType,rList in rObject._resources.items():
			for r in rList:
				content = r._rez_string()

				print("{}(${:08x}) {{".format(r.rName, r.get_id()))
				print(content)
				print("}\n")



class rTextObject(rObject):
	def __init__(self, text, *, id=None, attr=None):
		super().__init__(id=id, attr=attr)
		# text is a string or bytes.
		# bytes is assumed to be macroman
		self.text = text
		self._text = str_to_bytes(text)

	def __bytes__(self):
		return self._text

	def _rez_string(self):
		# todo - should extended chars be macroman?
		return '"' + self._text.decode("ascii") + '"'


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


class rControlList(rObject):
	rName = "rControlList"
	rType = 0x8003

	def __init__(self, children, *, id=None, attr=None):
		super().__init__(id, attr)
		self.children = children[:]
		for x in children:
			if not isinstance(x, rControl):
				raise TypeError("bad type: {}".format(type(x)))

	def __bytes__(self):
		bb = b""
		for x in self.children:
			bb += struct.pack("<I", x.get_id())
		bb += "\x00\x00\x00\x00" # 0-terminate
		return bb


class rMenuBar(rObject):
	rName = "rMenuBar"
	rType = 0x8008

	def __init__(self, *children, id=None, attr=None):
		super().__init__(id, attr)
		self.children = children[:]
		for x in children:
			if not isinstance(x, rMenu):
				raise TypeError("bad type: {}".format(type(x)))

	def __bytes__(self):
		bb = struct.pack("<HH", 0, 0x8000) # version, resIDs
		for x in self.children:
			bb += struct.pack("<I", x.get_id())
		bb += b"\x00\x00\x00\x00" # 0-terminate
		return bb

	def _rez_string(self):

		rv = "\t{\n"
		kiddos = [x.get_id() for x in self.children]
		rv += ",\n".join(["\t\t${:08x}".format(x) for x in kiddos])
		if kiddos: rv += "\n"
		rv += "\t}"
		return rv



class rMenu(rObject):
	rName = "rMenu"
	rType = 0x8009

	# /*-------------------------------------------------------*/
	# /* Equates for Menu Flags
	# /*-------------------------------------------------------*/
	# #Define rmAllowCache        $0008
	# #Define rmCustom            $0010
	# #Define rmNo_Xor            $0020
	# #Define rmDisabled          $0080

	#flags = all off = a080 (disabled)

	def __init__(self, title, *children, id=None, attr=None,
		flags=0x0000, menuID=None, 
		**kwargs
		):
		super().__init__(id, attr)
		self.title = make_string(title, rPString)
		self.children = children[:]
		self.menuID = menuID


		flags |= 0xa000 # title ref is resource, menus are resources
		if kwargs.get("allowCache"): flags |= 0x0008
		if kwargs.get("custom"): flags |= 0x0010
		if kwargs.get("xor"): flags |= 0x0020
		if kwargs.get("disabled"): flags |= 0x0080
		if kwargs.get("mChoose"): flags |= 0x0100

		self.flags = flags

		for x in children:
			if not isinstance(x, rMenuItem):
				raise TypeError("bad type: {}".format(type(x)))

	def __bytes__(self):
		menuID = self.menuID
		if menuID == None: menuID = self.get_id()
		bb = struct.pack("<HHHI", 0,
			menuID, self.flags, self.title.get_id()
		)
		for x in self.children:
			bb += struct.pack("<I", x.get_id())
		bb += b"\x00\x00\x00\x00" # 0-terminate
		return bb		

	def _rez_string(self):

		menuID = self.menuID
		if menuID == None: menuID = self.get_id()
		rv = (
			"\t${:04x}, /* menu ID */\n"
			"\t${:04x}, /* flags */\n"
			"\t${:08x}, /* title ref */\n"
		).format(menuID, self.flags, self.title.get_id())
		rv += "\t{\n"
		kiddos = [x.get_id() for x in self.children]
		rv += ",\n".join(["\t\t${:08x}".format(x) for x in kiddos])
		if kiddos: rv += "\n"
		rv += "\t}"
		return rv


class rMenuItem(rObject):
	rName = "rMenuItem"
	rType = 0x800a

	# /* --------------------------------------------------*/
	# /* flag word for menu item
	# /* --------------------------------------------------*/
	# #Define fBold               $0001
	# #Define fItalic             $0002
	# #Define fUnderline          $0004
	# #Define fXOR                $0020
	# #Define fDivider            $0040
	# #Define fDisabled           $0080
	# #Define fItemStruct         $0400
	# #Define fOutline            $0800
	# #Define fShadow             $1000
	# #define ItemStructRefShift  $0100
	# #Define ItemTitleRefShift   $4000


	def __init__(self, title, keys="", *, id=None, attr=None, 
		checkMark=None, itemID=None, flags=0x0000,
		**kwargs):
		super().__init__(id, attr)

		self.title = make_string(title, rPString)

		flags |= 0x8000 # title ref is resource
		if kwargs.get("bold"): flags |= 0x0001
		if kwargs.get("italic"): flags |= 0x0002
		if kwargs.get("underline"): flags |= 0x0004
		if kwargs.get("xor"): flags |= 0x0020
		if kwargs.get("divider"): flags |= 0x0040
		if kwargs.get("disabled"): flags |= 0x0080
		if kwargs.get("outline"): flags |= 0x0800
		if kwargs.get("shadow"): flags |= 0x1000

		self.flags = flags

		self.itemChar = 0
		self.altItemChar = 0
		self.itemID = itemID
		self.checkMark = 0


		if checkMark:
			if checkMark == True: checkMark = 0x12
			else: checkMark = ord(str_to_bytes(checkMark))
			self.checkMark = checkMark 

		if keys:
			bb = str_to_bytes(keys)
			if len(bb) >= 1:
				self.itemChar = bb[0]
				self.altItemChar = bb[0] # upper to lower?
			if len(bb) >= 2:
				self.altItemChar = bb[1]
			if len(bb) > 2:
				raise ValueError("keys too long: {}".format(keys))


	def __bytes__(self):
		itemID = self.itemID
		if itemID == None: itemID = self.get_id()
		bb = struct.pack("<HHBBHHI",
			0, itemID,
			self.itemChar, self.altItemChar,
			self.checkMark, self.flags,
			self.title.get_id()
		)

		return bb	

	def _rez_string(self):

		itemID = self.itemID
		if itemID == None: itemID = self.get_id()

		return (
			"\t${:04x}, /* id */\n"
			"\t{}, {}, /* chars */\n"
			"\t${:04x}, /* check */\n"
			"\t${:04x}, /* flags */\n"
			"\t${:04x} /* title ref */\n"
		).format(
			itemID,
			to_char_string(self.itemChar),
			to_char_string(self.altItemChar),
			self.checkMark,
			self.flags,
			self.title.get_id()
		)

def to_char_string(x):
	if not x: return '""'
	if x == 0x0a: return "\\n"
	if x == ord('"'): return "\""
	if x >= 32 and x < 0x7e: return '"' + chr(x) + '"'
	return "\\x{:02x}".format(x)

# /*-------------------------------------------------------*/
# /* Control List Descriptors
# /*-------------------------------------------------------*/
# #define singlePtr           $0000
# #define singleHandle        $0001
# #define singleResource      $0002
# #define ptrToPtr            $0003
# #define ptrToHandle         $0004
# #define ptrToResource       $0005
# #define handleToPtr         $0006
# #define handleToHandle      $0007
# #define handleToResource    $0008
# #define ResourceToResource  $0009
#
# /*-------------------------------------------------------*/
# /* Common Flag equates.
# /*-------------------------------------------------------*/
# #define ctlInvis            $0080
# #define ctlVisible          $0000
# #Define CtlInactive         $FF00#
#
#
# /*-------------------------------------------------------*/
# /* Common MoreFlags equates.
# /*-------------------------------------------------------*/
# #define FctlTarget          $8000
# #define FctlCanBeTarget     $4000
# #define FctlWantsEvents     $2000
# #define FCtlWantEvents      $2000   /* spelling variant */
# #define FctlProcNotPtr      $1000
# #define FctlTellAboutSize   $0800
# #define FctlIsMultiPart     $0400

class rControlTemplate(rObject):
	rName = "rControlTemplate"
	rType = 0x8004	

class rSimpleButton(rControlTemplate):
	rName = "rControlTemplate"
	rType = 0x8004
	# /*-------------------------------------------------------*/
	# /* Flag equates for simple buttons.
	# /*-------------------------------------------------------*/
	# #Define NormalButton        $0000
	# #Define DefaultButton       $0001
	# #Define SquareButton        $0002
	# #Define SquareShadowButton  $0003
	def __init__(self, rect, title, *,
		id=None, attr=None,
		flags = 0x0000, moreFlags = 0x0000,
		refCon = 0x00000000, controlID=None,
		**kwargs):
		super().__init__(id, attr)

		if kwargs.get("invisible"): flags |= 0x0080
		if kwargs.get("inactive"): flags |= 0xff00
		if kwargs.get("default"): flags |= 0x0001
		if kwargs.get("square"): flags |= 0x0002

		if kwargs.get("keys"):
			moreFlags |= 0x2000 # fCtlWantEvents
		moreFlags |= 0x1000 # fCtlProcNotPtr

		# if color:
		# 	moreFlags |= 0x08 # color table is resource id
		if title:
			moreFlags |= 0x02 # title is resource id

		self.title = make_string(title)

		self.flags = flags
		self.moreFlags = moreFlags
		self.rect = rect
		self.refCon = refCon
		self.controlID = controlID


	def __bytes__(self):
		# pcount, id:4, rect, procref:4, flags, moreFlags, refcon, title, color table, keys

		controlID = self.controlID
		if controlID == None: controlID = self.get_id()
		bb = struct.pack("<HI4HIHHIII", # missing keys
			9, # pcount
			controlID,
			*self.rect,
			0x80000000, # procref
			self.flags,
			self.moreFlags,
			self.refCon,
			self.title.get_id(),
			0, # color table
			# keys...
			)
		return bb

	def _rez_string(self):

		controlID = self.controlID
		if controlID == None: controlID = self.get_id()

		rv = (
			"\t${:04x}, /* control ID */\n"
			"\t{{ {:d}, {:d}, {:d}, {:d} }}, /* rect */\n"
			"\tSimpleButtonControl {{\n"
			"\t\t${:04x}, /* flags */\n"
			"\t\t${:04x}, /* more flags */\n"
			"\t\t${:08x}, /* refcon */\n"
			"\t\t${:08x}, /* title ref */\n"
			"\t\t${:08x} /* color table ref */\n"
			# "\t\t${}, /* key equiv */\n"
			"\t}}"
		).format(
			controlID,
			*self.rect,
			self.flags,
			self.moreFlags,
			self.refCon,
			self.title.get_id(),
			0
		)
		return rv

class rCheckControl(rControlTemplate):
	rName = "rControlTemplate"
	rType = 0x8004

	def __init__(self, rect, title, *,
		id=None, attr=None,
		flags = 0x0000, moreFlags = 0x0000,
		refCon = 0x00000000, controlID=None,
		checked=False,
		invisible=False, inactive=False,
		keys=None
		):
		super().__init__(id, attr)

		if invisible: flags |= 0x0080
		if inactive: flags |= 0xff00

		if keys:
			moreFlags |= 0x2000 # fCtlWantEvents
		moreFlags |= 0x1000 # fCtlProcNotPtr

		# if color:
		# 	moreFlags |= 0x08 # color table is resource id
		if title:
			moreFlags |= 0x02 # title is resource id

		self.title = make_string(title)

		self.flags = flags
		self.moreFlags = moreFlags
		self.rect = rect
		self.refCon = refCon
		self.controlID = controlID
		self.checked = int(checked)


	def __bytes__(self):

		controlID = self.controlID
		if controlID == None: controlID = self.get_id()
		bb = struct.pack("<HI4HIHHIIHI", # missing keys
			10, # pcount
			controlID,
			*self.rect,
			0x82000000, # procref
			self.flags,
			self.moreFlags,
			self.refCon,
			self.title.get_id(),
			self.checked,
			0, # color table
			# keys...
			)
		return bb

	def _rez_string(self):

		controlID = self.controlID
		if controlID == None: controlID = self.get_id()

		rv = (
			"\t${:04x}, /* control ID */\n"
			"\t{{ {:d}, {:d}, {:d}, {:d} }}, /* rect */\n"
			"\tCheckControl {{\n"
			"\t\t${:04x}, /* flags */\n"
			"\t\t${:04x}, /* more flags */\n"
			"\t\t${:08x}, /* refcon */\n"
			"\t\t${:08x}, /* title ref */\n"
			"\t\t${:04x}, /* initial value */\n"
			"\t\t${:08x} /* color table ref */\n"
			# "\t\t${}, /* key equiv */\n"
			"\t}}"
		).format(
			controlID,
			*self.rect,
			self.flags,
			self.moreFlags,
			self.refCon,
			self.title.get_id(),
			self.checked
			0
		)
		return rv

class rRadioControl(rControlTemplate):
	rName = "rControlTemplate"
	rType = 0x8004

	def __init__(self, rect, title, *,
		id=None, attr=None,
		flags = 0x0000, moreFlags = 0x0000,
		refCon = 0x00000000, controlID=None,
		checked=False,
		invisible=False, inactive=False,
		keys=None,
		family=0
		):
		super().__init__(id, attr)

		if invisible: flags |= 0x0080
		if inactive: flags |= 0xff00

		flags |= family & 0x7f

		if keys:
			moreFlags |= 0x2000 # fCtlWantEvents
		moreFlags |= 0x1000 # fCtlProcNotPtr

		# if color:
		# 	moreFlags |= 0x08 # color table is resource id
		if title:
			moreFlags |= 0x02 # title is resource id

		self.title = make_string(title)

		self.flags = flags
		self.moreFlags = moreFlags
		self.rect = rect
		self.refCon = refCon
		self.controlID = controlID
		self.checked = int(checked)


	def __bytes__(self):

		controlID = self.controlID
		if controlID == None: controlID = self.get_id()
		bb = struct.pack("<HI4HIHHIIHI", # missing keys
			10, # pcount
			controlID,
			*self.rect,
			0x84000000, # procref
			self.flags,
			self.moreFlags,
			self.refCon,
			self.title.get_id(),
			self.checked,
			0, # color table
			# keys...
			)
		return bb

	def _rez_string(self):

		controlID = self.controlID
		if controlID == None: controlID = self.get_id()

		rv = (
			"\t${:04x}, /* control ID */\n"
			"\t{{ {:d}, {:d}, {:d}, {:d} }}, /* rect */\n"
			"\tRadioControl {{\n"
			"\t\t${:04x}, /* flags */\n"
			"\t\t${:04x}, /* more flags */\n"
			"\t\t${:08x}, /* refcon */\n"
			"\t\t${:08x}, /* title ref */\n"
			"\t\t${:04x}, /* initial value */\n"
			"\t\t${:08x} /* color table ref */\n"
			# "\t\t${}, /* key equiv */\n"
			"\t}}"
		).format(
			controlID,
			*self.rect,
			self.flags,
			self.moreFlags,
			self.refCon,
			self.title.get_id(),
			self.checked
			0
		)
		return rv




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


rPString("hello")
rCString("goodbye")

# rMenuItem("Hello")

rMenuBar(
	rMenu("@",
		rMenuItem("About..."),
		rMenuItem("Preferences...")
	),
	rMenu( " File ",
		rMenuItem("New", "Nn"),
		rMenuItem("Open", "Oo")
	),
	id=1
)

rTwoRects(rect(x=0,y=0,height=10, width=10), (1,2,3,4))
rRectList(rect(x=0,y=0,height=10, width=10), (1,2,3,4))

rSimpleButton(rect(x=10, y=10, height=13, width=90), "Save",default=True)

rObject.dumphex()
rObject.dumprez()
