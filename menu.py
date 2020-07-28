
from base import *
import struct

__all__ = ['rMenuBar', 'rMenu', 'rMenuItem']

def to_char_string(x):
	if not x: return '""'
	if x in (0x0a, 0x0d): return "\\n"
	if x == ord('"'): return "\""
	if x >= 32 and x < 0x7e: return '"' + chr(x) + '"'
	return "\\x{:02x}".format(x)

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

