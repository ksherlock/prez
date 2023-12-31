import struct
import enum

from . base import *
from . utils import *
from . icon import rIcon


__all__ = [
	'rMenuBar',
	'rMenu',
	'rMenuItem',
	'rItemStruct',

	'UndoMenuItem',
	'CutMenuItem',
	'CopyMenuItem',
	'PasteMenuItem',
	'ClearMenuItem',
	'CloseMenuItem',
	'DividerMenuItem'
]


def export_enum(cls):
	global __all__

	members = cls.__members__
	globals().update(members)
	if __all__ != None: __all__.extend(list(members))
	return cls	

@export_enum
class MenuFlags(enum.Flag):
	# menu item flags (duplicate menu flags.)
	mPlain            = 0x0000
	mBold             = 0x0001
	mItalic           = 0x0002
	mUnderline        = 0x0004
	mXOR              = 0x0020
	mDivider          = 0x0040
	mDisabled         = 0x0080
	# menuIItemStruct       = 0x0400
	mOutline          = 0x0800
	mShadow           = 0x1000

	# menu flags
	mAllowCache        = 0x0008
	mCustom            = 0x0010
	# rmNo_Xor            = 0x0020
	# rmDisabled          = 0x0080



# see:
# Programmer's Reference for System 6 (Ch 13 Menu Manager Update, pg 103+)
# TB Vol 3 Chapter 37
# TB Vol 1 Chapter 13

# A menu ID must be unique for each menu; that is, no two menus
# can have the same ID or the system will fall. Similarly, no two
# items can have the same Item ID.

_menu_ids = {}
_menu_item_ids = {}


# ref is resource flag for the text is stored in the menu item flags
# icon could be null but in that case, why are you using an rItemStruct????
class rItemStruct(rObject):
	rName = "rItemStruct"
	rType = 0x8028

	def __init__(self, text, icon, **kwargs):
		super().__init__(**kwargs)

		self.text = rPString.make_string(text)
		if type(icon) != rIcon:
			raise TypeError("rItemStruct: bad icon type: {}".format(type(icon)))

		self.icon = icon

	def __bytes__(self):
		return struct.pack("<HII",
			0x8000 + 0b10, # icon present, icon is resource
			self.text.get_id(),
			self.icon.get_id()
		)

	def _rez_string(self):
		return (
			"\t0x{:04x}, /* flags */\n"
			"\t0x{:08x}, /* text (rPString) */\n"
			"\t0x{:08x} /* icon (rIcon) */\n"
		).format(
			0x8000 + 0b10,
			self.text.get_id(),
			self.icon.get_id()
		)



class rMenuBar(rObject):
	rName = "rMenuBar"
	rType = 0x8008

	def __init__(self, *children, **kwargs):
		super().__init__(**kwargs)

		for x in children:
			if not isinstance(x, rMenu):
				raise TypeError("rMenuBar: bad type: {}".format(type(x)))

		self.children = children


	def __bytes__(self):
		bb = struct.pack("<HH", 0, 0x8000) # version, resIDs
		for x in self.children:
			bb += struct.pack("<I", x.get_id())
		bb += b"\x00\x00\x00\x00" # 0-terminate
		return bb

	def _rez_string(self):

		rv = "\t{\n"
		kiddos = [x.get_id() for x in self.children]
		rv += ",\n".join(["\t\t0x{:08x}".format(x) for x in kiddos])
		if kiddos: rv += "\n"
		rv += "\t}"
		return rv


# valid menu ids: $0001-$fffe
class rMenu(rObject):
	rName = "rMenu"
	rType = 0x8009
	# rChildType = rMenuItem
	rRange = range(0x0001,0xffff)

	# /*-------------------------------------------------------*/
	# /* Equates for Menu Flags
	# /*-------------------------------------------------------*/
	# #Define rmAllowCache        $0008
	# #Define rmCustom            $0010
	# #Define rmNo_Xor            $0020
	# #Define rmDisabled          $0080

	#flags = all off = a080 (disabled)

	def __init__(self, title, *children,
		menuID=None,
		**kwargs
		):
		super().__init__(**kwargs)

		flags = 0xa000 # title ref is resource, menus are resources
		self.title = rPString.make_string(title)
		self.menuID = menuID
		self.children = []

		VALID = mAllowCache | mCustom | mXOR | mDisabled
		for x in children:
			if type(x) == MenuFlags:
				if x not in VALID:
					raise ValueError("rMenu: bad flag: {}".format(x))
				flags |= x.value
				continue
			if isinstance(x, rMenuItem):
				self.children.append(x)
				continue
			raise TypeError("rMenu: bad type: {}".format(type(x)))

		self.flags = flags


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
			"\t0x{:04x}, /* menu ID */\n"
			"\t0x{:04x}, /* flags */\n"
			"\t0x{:08x}, /* title ref (rPString) */\n"
		).format(menuID, self.flags, self.title.get_id())
		rv += "\t{\n"
		kiddos = [x.get_id() for x in self.children]
		rv += ",\n".join(["\t\t0x{:08x}".format(x) for x in kiddos])
		if kiddos: rv += "\n"
		rv += "\t}"
		return rv


miUndo = 0xfa
miCut = 0xfb
miCopy = 0xfc
miPaste = 0xfd
miClear = 0xfe
miClose = 0xff


# valid menu item ids: $0100-$fffe

class rMenuItem(rObject):
	rName = "rMenuItem"
	rType = 0x800a
	rRange = range(0x100,0xffff)

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


	def __init__(self, title, keys="", *, 
		checkMark=None, itemID=None, flags=0x0000,
		**kwargs):
		super().__init__(**kwargs)

		if isinstance(title, rItemStruct):
			self.title = title
			flags |= 0b0000_0110_0000_0000 # title is rItem struct, is resource 
		else:
			self.title = rPString.make_string(title)

		flags |= 0x8000 # title ref is resource
		if kwargs.get("bold"): flags |= 0x0001
		if kwargs.get("italic"): flags |= 0x0002
		if kwargs.get("underline"): flags |= 0x0004
		if kwargs.get("xor"): flags |= 0x0020
		if kwargs.get("divider"): flags |= 0x0040
		if kwargs.get("disabled"): flags |= 0x0080
		if kwargs.get("outline"): flags |= 0x0800
		if kwargs.get("shadow"): flags |= 0x1000

		# bit 15 of flags set if title ref is actually an
		# item struct ref.

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
			"\t0x{:04x}, /* id */\n"
			"\t{}, {}, /* chars */\n"
			"\t0x{:04x}, /* check */\n"
			"\t0x{:04x}, /* flags */\n"
			"\t0x{:04x} /* title ref ({}) */"
		).format(
			itemID,
			format_char(self.itemChar),
			format_char(self.altItemChar),
			self.checkMark,
			self.flags,
			self.title.get_id(),
			self.title.rName
		)


def _singleton(func):
	value = None
	def inner():
		nonlocal value
		if not value: value = func()
		return value
	return inner


def DividerMenuItem():
	return rMenuItem("-", flags = 0x0080) # disabled

def EditMenu(*children, **kwargs):
	return rMenu("  Edit  ", 
		UndoMenuItem(),
		CutMenuItem(),
		CopyMenuItem(),
		PasteMenuItem(),
		ClearMenuItem(),
		*children,
		**kwargs
	)

@ _singleton
def UndoMenuItem():
	# normally underlined....
	return rMenuItem("Undo", "Zz", itemID = miUndo)

@ _singleton
def CutMenuItem():
	return rMenuItem("Cut", "Xx", itemID = miCut)

@ _singleton
def CopyMenuItem():
	return rMenuItem("Copy", "Cc", itemID = miCopy)

@ _singleton
def PasteMenuItem():
	return rMenuItem("Paste", "Vv", itemID = miPaste)

@ _singleton
def ClearMenuItem():
	return rMenuItem("Clear", "", itemID = miClear)

@ _singleton
def CloseMenuItem():
	return rMenuItem("Close", "Ww", itemID = miClose)
