from base import rObject, rList, rPString, rTextForLETextBox2
import struct
from rect import *
from colors import *
from utils import *


__all__ = [
	"rControlTemplate", "rControlList", "rSimpleButton",
	"rCheckControl", "rRadioControl", "rThermometerControl",
	"rRectangleControl", "rStatTextControl"
]

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
# #Define CtlInactive         $FF00
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
	procRef = None

# TODO - Colors
#
# color table (TB V1 Ch 4-87):
# word outline
# word background when not selected
# word background when selected
# word title when selected 
# word title when not selected

class rSimpleButton(rControlTemplate):
	rName = "rControlTemplate"
	rType = 0x8004
	procRef = 0x80000000


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

		self.title = rPString.make_string(title)

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
			"\t${:08x}, /* control ID */\n"
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

# TODO - colors
# color table (TB V1 Ch 4-87):
# word reserved
# word box not selected
# word box checked
# word title 
class rCheckControl(rControlTemplate):
	rName = "rControlTemplate"
	rType = 0x8004
	procRef = 0x82000000

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

		self.title = rPString.make_string(title)

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
			"\t${:08x}, /* control ID */\n"
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
			self.checked,
			0
		)
		return rv

# TODO - colors
# color table (TB V1 Ch 4-88):
# word reserved
# word box when off
# word box when on
# word title 
class rRadioControl(rControlTemplate):
	rName = "rControlTemplate"
	rType = 0x8004
	procRef = 0x84000000

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

		self.title = rPString.make_string(title)

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
			"\t${:08x}, /* control ID */\n"
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
			self.checked,
			0
		)
		return rv


#
# color table (System 6, Ch 3-11):
# word outline color $000w
# word interior color $000x
# word fore color (dotted pattern) $000y
# word fill color $p00z
#
# w, x, y, z  = color
# p = 0 for solid pattern, 8 ($8000) for dotted pattern.
#
# default colors:
# outline $0000 - black
# interior $000f - white
# fore $0000 - (not pattern)
# fill = $0004 - red, not dotted.

# TODO - colors not yet supported.
class rThermometerControl(rControlTemplate):
	rName = "rControlTemplate"
	rType = 0x8004
	procRef = 0x87FF0002

	def __init__(self, rect, *,
		id=None, attr=None,
		flags = 0x0000, moreFlags = 0x0000,
		refCon = 0x00000000, controlID=None,
		value=0,
		scale=0,
		horizontal=False,
		invisible=False, inactive=False
		):
		super().__init__(id, attr)

		if invisible: flags |= 0x0080 # ?
		if inactive: flags |= 0xff00 # ?
		if horizontal: flags |= 0x0001

		moreFlags |= 0x1000 # fCtlProcNotPtr

		# if color:
		# 	moreFlags |= 0x08 # color table is resource id


		self.flags = flags
		self.moreFlags = moreFlags
		self.rect = rect
		self.refCon = refCon
		self.controlID = controlID
		self.value = value
		self.scale = scale


	def __bytes__(self):

		controlID = self.controlID
		if controlID == None: controlID = self.get_id()
		bb = struct.pack("<HI4HIHHIHHI",
			9, # pcount
			controlID,
			*self.rect,
			0x87FF0002, # procref
			self.flags,
			self.moreFlags,
			self.refCon,
			self.value,
			self.scale,
			0, # color table
			)
		return bb

	def _rez_string(self):

		controlID = self.controlID
		if controlID == None: controlID = self.get_id()

		rv = (
			"\t${:08x}, /* control ID */\n"
			"\t{{ {:d}, {:d}, {:d}, {:d} }}, /* rect */\n"
			"\tThermometerControl {{\n"
			"\t\t${:04x}, /* flags */\n"
			"\t\t${:04x}, /* more flags */\n"
			"\t\t${:08x}, /* refcon */\n"
			"\t\t${:04x}, /* value */\n"
			"\t\t${:04x}, /* scale */\n"
			"\t\t${:08x} /* color table ref */\n"
			# "\t\t${}, /* key equiv */\n"
			"\t}}"
		).format(
			controlID,
			*self.rect,
			self.flags,
			self.moreFlags,
			self.refCon,
			self.value,
			self.scale,
			0
		)
		return rv


#
# TODO - penmask / penpattern not yet supported.
#

class rRectangleControl(rControlTemplate):
	rName = "rControlTemplate"
	rType = 0x8004
	procRef = 0x87FF0003

	_colorMap = {
		Black : 0b10,
		Grey1 : 0b01,
		Grey2 : 0b01,
		Transparent: 0b00,
		0b00: 0b00,
		0b01: 0b01,
		0b10: 0b10
	}

	def __init__(self, rect, *,
		id=None, attr=None,
		flags = 0x0000, moreFlags = 0x0000,
		refCon = 0x00000000, controlID=None,
		penHeight=1,
		penWidth=2,
		invisible=False, inactive=False,
		color = Black
		):
		super().__init__(id, attr)

		if invisible: flags |= 0x0080
		if inactive: flags |= 0xff00
		if color != None:
			if color in self._colorMap:
				flags |= self._colorMap[color]
			else:
				raise ValueError("Invalid rectangle color: {}}".format(color))

		moreFlags |= 0x1000 # fCtlProcNotPtr


		self.flags = flags
		self.moreFlags = moreFlags
		self.rect = rect
		self.refCon = refCon
		self.controlID = controlID
		self.penHeight = penHeight
		self.penWidth = penWidth

	def __bytes__(self):

		controlID = self.controlID
		if controlID == None: controlID = self.get_id()
		bb = struct.pack("<HI4HIHHIHH",
			8, # pcount
			controlID,
			*self.rect,
			0x87FF0003, # procref
			self.flags,
			self.moreFlags,
			self.refCon,
			self.penHeight,
			self.penWidth
			)
		return bb

	def _rez_string(self):

		controlID = self.controlID
		if controlID == None: controlID = self.get_id()

		# penmask / pen pattern not yet supported.
		rv = (
			"\t${:08x}, /* control ID */\n"
			"\t{{ {:d}, {:d}, {:d}, {:d} }}, /* rect */\n"
			"\tRectangleControl {{\n"
			"\t\t${:04x}, /* flags */\n"
			"\t\t${:04x}, /* more flags */\n"
			"\t\t${:08x}, /* refcon */\n"
			"\t\t${:04x}, /* pen height */\n"
			"\t\t${:04x}, /* pen width */\n"
			"\t}}"
		).format(
			controlID,
			*self.rect,
			self.flags,
			self.moreFlags,
			self.refCon,
			self.penHeight,
			self.penWidth
		)
		return rv


fSquishText         = 0x0010   # 6.0.1
fTextCanDim         = 0x0008
fBlastText          = 0x0004
fSubstituteText     = 0x0002
fSubTextIsPascal    = 0x0001
fSubTextIsC         = 0x0000

# leftJustify = 0
# centerJustify = 1
# fullJustify = 2
# rightJustify = -1

class rStatTextControl(rControlTemplate):
	rName = "rControlTemplate"
	rType = 0x8004
	procRef = 0x81000000


	def __init__(self, rect, text, *,
		id=None, attr=None,
		flags = 0x0000, moreFlags = 0x0000,
		refCon = 0x00000000, controlID=None,
		invisible=False, inactive=False,
		fSquishText = False,
		fBlastText = False,
		fTextCanDim = False,
		fSubstituteText = False,
		fSubTextIsC = False,
		fSubTextIsPascal = False,
		just = 0,
		leftJust = False,
		centerJust = False,
		rightJust = False,
		fullJust = False,
		):
		super().__init__(id, attr)

		if invisible: flags |= 0x0080
		if inactive: flags |= 0xff00

		moreFlags |= 0x1000 # fCtlProcNotPtr
		moreFlags |= 0b10 # text is resource

		if fSquishText: flags |= 0x0010
		if fTextCanDim: flags |= 0x0008
		if fBlastText: flags |= 0x0004
		if fSubstituteText: flags |= 0x0002
		if fSubTextIsPascal: flags |= 0x0001| 0x0002
		if fSubTextIsC != None: flags |= 0x0002

		if leftJust: just = 0
		elif centerJust: just = 1
		elif fullJust: just = 2
		elif rightJust: just = -1

		self.text = rTextForLETextBox2.make_string(text)

		self.flags = flags
		self.moreFlags = moreFlags
		self.rect = rect
		self.refCon = refCon
		self.controlID = controlID

		self.justification = just


		# warnings -
		# fSquishText only effective w/ fBlastText
		# fBlastText not compatible w/ string substitution or formatting.

	def __bytes__(self):

		controlID = self.controlID
		if controlID == None: controlID = self.get_id()
		bb = struct.pack("<HI4HIHHIIHH",
			9, # pcount
			controlID,
			*self.rect,
			0x81000000, # procref
			self.flags,
			self.moreFlags,
			self.refCon,
			self.text.get_id(),
			0,
			self.justification & 0xffff
			)
		return bb

	def _rez_string(self):

		controlID = self.controlID
		if controlID == None: controlID = self.get_id()

		# penmask / pen pattern not yet supported.
		rv = (
			"\t${:08x}, /* control ID */\n"
			"\t{}, /* rect */\n"
			"\tStatTextControl {{\n"
			"\t\t${:04x}, /* flags */\n"
			"\t\t${:04x}, /* more flags */\n"
			"\t\t${:08x}, /* refcon */\n"
			"\t\t${:08x}, /* text ref (rTextForLETextBox2) */\n"
			"\t\t${:04x}, /* text size */\n"
			"\t\t{:d}, /* text justification */\n"
			"\t}}"
		).format(
			controlID,
			format_rect(self.rect),
			self.flags,
			self.moreFlags,
			self.refCon,
			self.text.get_id(),
			0,
			self.justification & 0xffff
		)
		return rv




class rControlList(rList):
	rName = "rControlList"
	rType = 0x8003
	rChildType = rControlTemplate
