from enum import Enum, Flag


class rTypes(Enum):
	rIcon = 0x8001                    # Icon type 
	rPicture = 0x8002                 # Picture type 
	rControlList = 0x8003             # Control list type 
	rControlTemplate = 0x8004         # Control template type 
	rC1InputString = 0x8005           # GS/OS class 1 input string 
	rPString = 0x8006                 # Pascal string type 
	rStringList = 0x8007              # String list type 
	rMenuBar = 0x8008                 # MenuBar type 
	rMenu = 0x8009                    # Menu template 
	rMenuItem = 0x800A                # Menu item definition 
	rTextForLETextBox2 = 0x800B       # Data for LineEdit LETextBox2 call 
	rCtlDefProc = 0x800C              # Control definition procedure type 
	rCtlColorTbl = 0x800D             # Color table for control 
	rWindParam1 = 0x800E              # Parameters for NewWindow2 call 
	rWindParam2 = 0x800F              # Parameters for NewWindow2 call 
	rWindColor = 0x8010               # Window Manager color table 
	rTextBlock = 0x8011               # Text block 
	rStyleBlock = 0x8012              # TextEdit style information 
	rToolStartup = 0x8013             # Tool set startup record 
	rResName = 0x8014                 # Resource name 
	rAlertString = 0x8015             # AlertWindow input data 
	rText = 0x8016                    # Unformatted text 
	rCodeResource = 0x8017
	rCDEVCode = 0x8018
	rCDEVFlags = 0x8019
	rTwoRects = 0x801A                # Two rectangles 
	rFileType = 0x801B                # Filetype descriptors--see File Type Note $42 
	rListRef = 0x801C                 # List member 
	rCString = 0x801D                 # C string 
	rXCMD = 0x801E
	rXFCN = 0x801F
	rErrorString = 0x8020             # ErrorWindow input data 
	rKTransTable = 0x8021             # Keystroke translation table 
	rWString = 0x8022                 # not useful--duplicates $8005 
	rC1OutputString = 0x8023          # GS/OS class 1 output string 
	rSoundSample = 0x8024
	rTERuler = 0x8025                 # TextEdit ruler information 
	rFSequence = 0x8026
	rCursor = 0x8027                  # Cursor resource type 
	rItemStruct = 0x8028              # for 6.0 Menu Manager 
	rVersion = 0x8029
	rComment = 0x802A
	rBundle = 0x802B
	rFinderPath = 0x802C
	rPaletteWindow = 0x802D           # used by HyperCard IIgs 1.1
	rTaggedStrings = 0x802E
	rPatternList = 0x802F
	rRectList = 0xC001
	rPrintRecord = 0xC002
	rFont = 0xC003


class rAttr(Flag):

	attrPage = 0x0004   
	attrNoSpec = 0x0008 
	attrNoCross = 0x0010
	resChanged = 0x0020
	resPreLoad = 0x0040
	resProtected = 0x0080
	attrPurge1 = 0x0100
	attrPurge2 = 0x0200
	attrPurge3 = 0x0300
	resAbsLoad = 0x0400
	resConverter = 0x0800
	attrFixed = 0x4000
	attrLocked = 0x8000

	attrPurge = 0x0300

class ResourceWriter(object):

	def __init__(self):
		self._resources = []
		self._resource_ids = set()
		self._resource_names = {}


	def unique_resource_id(self, rtype, range):
		if type(rtype) == rTypes: rtype = rtype.value
		if rtype < 0 or rtype > 0xffff:
			raise ValueError("Invalid resource type ${:04x}".format(rtype))

		if range > 0xffff:
			raise ValueError("Invalid range ${:04x}".format(range))
		if range > 0x7ff and range < 0xffff:
			raise ValueError("Invalid range ${:04x}".format(range))

		min = range << 16
		max = min + 0xffff
		if range == 0:
			min = 1
		elif range == 0xffff:
			min = 1
			max = 0x07feffff

		used = [x[1] for x in self._resource_ids if x[0] == rtype and x[1] >= min and x[1] <= max]
		if len(used) == 0: return min

		used.sort()
		# if used[0] > min: return min

		id = min
		for x in used:
			if x > id: return id
			id = x + 1
		if id >= max:
			raise OverflowError("No Resource ID available in range")
		raise id

	def add_resource(self, rtype, rid, data, *, attr=0, reserved=0, name=None):
		if type(rtype) == rTypes: rtype = rtype.value
		if rtype < 0 or rtype > 0xffff:
			raise ValueError("Invalid resource type ${:04x}".format(rtype))

		if rid < 0 or rid > 0x07ffffff:
			raise ValueError("Invalid resource id ${:08x}".format(rid))

		if (rid, rtype) in self._resource_ids:
			raise ValueError("Duplicate resource ${:04x}:${:08x}".format(rtype, rid))

		# don't allow standard res names since they're handled elsewhere.
		if rtype == rTypes.rResName.value and rid > 0x00010000 and rid < 0x00020000:
			raise ValueError("Invalid resource ${:04x}:${:08x}".format(rtype, rid))


		if name:
			if type(name) == str: name = name.encode('macroman')
			if len(name) > 255: name = name[0:255]
			self._resource_names[(rtype, name)]=rid

		self._resources.append((rtype, rid, attr, data, reserved))
		self._resource_ids.add((rtype, rid))



	def set_resource_name(rtype, rid, name):
		if type(rtype) == rTypes: rtype = rtype.value
		if rtype < 0 or rtype > 0xffff:
			raise ValueError("Invalid resource type ${:04x}".format(rtype))

		if rid < 0 or rid > 0x07ffffff:
			raise ValueError("Invalid resource id ${:08x}".format(rid))

		key = (rtype, name)
		if not name:
			self._resource_names.pop(key, None)
		else:
			if type(name) == str: name = str.encode('macroman')
			if len(name) > 255: name = name[0:255]
			self._resource_names[key] = rid



	@staticmethod
	def _merge_free_list(fl):
		rv = []
		eof = None
		for (offset, size) in fl:
			if offset == eof:
				tt = rv.pop()
				tt[1] += size
				rv.append(tt)
			else:
				rv.append((offset, size))
			eof = offset + size
		return rv

	def _build_res_names(self):
		# format:
		# type $8014, id $0001xxxx (where xxxx = resource type)
		# version:2 [1]
		# name count:4
		# [id:4, name:pstring]+
		#

		rv = []
		tmp = []

		if not len(self._resource_names): return rv
		for (rtype, rname), rid in self._resource_names.items():
			tmp.append( (rtype, rid, rname) )


		keyfunc_type = lambda x: x[0]
		keyfunc_name = lambda x: x[2]
		tmp.sort(key = keyfunc_type)
		for rtype, iter in groupby(tmp, keyfunc_type):
			tmp = list(iter)
			tmp.sort(key=keyfunc_name)
			data = bytearray()
			data += struct.pack("<HI", 1, len(tmp))
			for (_, rid, rname) in tmp:
				data += struct.pack("<IB", rid, len(rname))
				data += rname

			rv.append( (rTypes.rResName.value, 0x00010000 | rtype, 0, data, 0) )

		return rv

	def write(self,io):
		# only need 1 free list entry (until reserved space is supported)

		# free list always has extra blank 4-bytes at end.
		# free list available grows by 10?

		resources = self._build_res_names()

		resources.extend(self._resources)

		index_used = len(resources)
		index_size = 10 + index_used // 10 * 10

		# remove reserved space from the last entry
		ix = len(resources)
		if ix and resources[ix-1][4]:
			(rid, rtype, attr, data, _) = resources[ix-1]
			resources[ix-1] = (rid, rtype, attr, data, 0)


		freelist_used = 1
		for x in resources:
			if x[4]: freelist_used += 1
		freelist_size = 10 + freelist_used // 10 * 10

		extra = freelist_size * 8 + 4 + index_size * 20

		map_size = 32 + extra
		map_offset = 0x8c

		# version, offset to map, sizeof map, 128 bytes (reserved) 
		rheader = struct.pack("<III128x", 0, map_offset, map_size)

		# handle:4, flags:2, offset:4, size:4, toindex:2, filenum:2, id:2,
		# indexSize:4, indexUsed:4, flSize:2,flUsed:2,
		rmap = struct.pack("<IHIIHHHIIHH",
			0, 0, map_offset, map_size,
			32 + freelist_size * 8 + 4, 
			0, 0,
			index_size, index_used,
			freelist_size, freelist_used
		)

		eof = 0x8c + map_size
		fl = []

		index = bytearray()
		for (rtype, rid, attr, data, reserved) in resources:
			# type:2, id:4, offset:4, attr:2, size:4, handle:4
			index += struct.pack("<HIIHII",
				rtype, rid, eof, 
				attr, len(data), 0
			)
			eof += len(data)
			if reserved:
				fl.append((eof, reserved))
				eof += reserved

		index += bytes(20 * ((index_size - index_used)))

		fl.append((eof, 0xffffffff-eof))

		fl = self._merge_free_list(fl)

		freelist = bytearray()
		for (offset, size) in fl:
			freelist += struct.pack("<II", offset, size)
		freelist += bytes(8 * (freelist_size - freelist_used) + 4)


		io.write(rheader)
		io.write(rmap)
		io.write(freelist)
		io.write(index)

		for (_, _, attr, data, reserved) in resources:
			io.write(data)
			if reserved: io.write(bytes(reserved))

		return eof
