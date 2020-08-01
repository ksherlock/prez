from base import *
from control import rControlTemplate, rControlList
from utils import *

import struct

__all__ = ['rWindParam1']



fHilited            = 0x0001
fZoomed             = 0x0002
fAllocated          = 0x0004
fCtlTie             = 0x0008
fInfo               = 0x0010
fVis                = 0x0020
fQContent           = 0x0040
fMove               = 0x0080
fZoom               = 0x0100
fFlex               = 0x0200
fGrow               = 0x0400
fBScroll            = 0x0800
fRScroll            = 0x1000
fAlert              = 0x2000
fClose              = 0x4000
fTitle              = 0x8000



def format_plane(x):
	if x == -1: return "infront"
	if x == 0: return "behind"
	return "{:d}".format(x)

class rWindParam1(rObject):
	rName = "rWindParam1"
	rType = 0x800e

	def __init__(self, position, title=None, *controls, 

		frameBits = 0,
		refCon = 0,
		zoomRect = (0, 0, 0, 0),
		origin = (0, 0),
		dataSize = (0, 0),
		# contentRegion = (0, 0, 0, 0)
		maxSize = (0, 0),
		scroll = (0, 0),
		page = (0, 0),
		infoRefCon = 0,
		infoHeight = 0,
		plane = -1, # inFront
		# inFront = True,
		id = None,
		attr = None,
		**kwargs):

		super().__init__(id=id, attr=attr)

		self.frameBits = frameBits
		if title: self.title = rPString.make_string(title)
		self.zoomRect=zoomRect
		self.color = None
		self.origin = origin
		self.dataSize = dataSize
		self.maxSize = maxSize
		self.scroll = scroll
		self.page = page
		self.refCon = refCon
		self.infoRefCon = infoRefCon
		self.infoHeight = infoHeight
		self.position = position

		self.plane = plane

		verb = 0

		if self.color:
			verb |= 0b10 << 10
		if self.title:
			verb |= 0b10 << 8

		controlList = None
		# controls could be (), (rControlList), or (rControl [, rControl]* )

		if not controls:
			pass

		elif len(controls) == 1:
			controlList = controls[0]
			if isinstance(controlList, rControlList):
				verb |= 0x0009 # resourceToResource
			elif isinstance(controlList, rControlTemplate):
				verb |= 0x0002 # singleResource
			else:
				raise TypeError("Bad control type: {}".format(type(controlList)))
		else:
			# generate an rControlList
			controlList = rControlList(*controls)
			verb |= 0x0009 # resourceToResource


		self.controlList = controlList
		self.verb = verb


	def __bytes__(self):

		bb = struct.pack("<HH II 4H I 2H 2H 2H 2H 2H IHIII 4H II H",

			0x50, #length
			self.frameBits,
			self.title.get_id() if self.title else 0, 
			self.refCon,
			*self.zoomRect,
			0, # color
			*self.origin,
			*self.dataSize,
			*self.maxSize,
			*self.scroll,
			*self.page,
			self.infoRefCon,
			self.infoHeight,
			0,0,0, # procs
			*self.position,
			self.plane & 0xffffffff,
			self.controlList.get_id() if self.controlList else 0,
			self.verb
		)
		return bb

	def _rez_string(self):
		return (
			"\t0x{:04x}, /*frame bits */\n"
			"\t0x{:08x}, /* title */\n"
			"\t0x{:08x}, /* refCon */\n"
			"\t{}, /* zoom rect */\n"
			"\t0x{:08x}, /* color table */\n"
			"\t{}, /* origin */\n"
			"\t{}, /* data height/width */\n"
			"\t{}, /* max height/width */\n"
			"\t{}, /* scroll vert/horz */\n"
			"\t{}, /* page vert/horz */\n"
			"\t0x{:08x}, /* info refCon */\n"
			"\t{:d}, /* info height */\n"
			"\t{}, /* position */\n"
			"\t{}, /* plane */\n"
			"\t0x{:08x}, /* controlList */\n"
			"\t0x{:04x}, /* verb */"
		).format(
			self.frameBits,
			self.title.get_id() if self.title else 0,
			self.refCon,
			format_rect(self.zoomRect),
			0,
			format_point(self.origin),
			format_size(self.dataSize), 
			format_size(self.maxSize), 
			format_point(self.scroll),
			format_point(self.page),
			self.infoRefCon,
			self.infoHeight,
			format_rect(self.position),
			format_plane(self.plane),
			self.controlList.get_id() if self.controlList else 0,
			self.verb
		)

