from base import *
import struct
from rect import *





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


class rThermometerControl(rControlTemplate):
	rName = "rControlTemplate"
	rType = 0x8004

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


class rControlList(rList):
	rName = "rControlList"
	rType = 0x8003
	rChildType = rControlTemplate
