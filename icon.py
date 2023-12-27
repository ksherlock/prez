from base import rObject
import struct


__all__ = ["rIcon"]

def rez_hex(bb, width=16, indent = 0, comma = False):

	max = (len(bb) + width-1) // width
	data = [bb[x*width:x*width+width] for x in range(0, max)]

	prefix = "\t" * indent 

	tmp = "\n".join([prefix + '$"' + x.hex() + '"' for x in data])
	if comma: tmp += ",\n"
	else: tmp += "\n"
	return tmp


class rIcon(rObject):
	rName = "rIcon"
	rType = 0x8001

	def __init__(self, *,
		height = None,
		width = None,
		# size = None, # height / width tuple
		image = None, # bytes/byte array
		mask = None, # bytes/ bytearray
		color = True,
		**kwargs
		):
		super().__init__(**kwargs)

		if height == None and width == None:
			raise TypeError("rIcon: missing height/width or size")

		if type(image) == str: image = bytes.fromhex(image)
		if type(mask) == str: mask = bytes.fromhex(mask)

		if type(image) not in (bytes, bytearray):
			raise TypeError("rIcon: bad image type ({})".format(type(image)))

		if type(mask) not in (bytes, bytearray):
			raise TypeError("rIcon: bad mask type ({})".format(type(mask)))

		# can't support, eg 1 x 1 since that's only half a byte.
		if width & 0x01:
			raise ValueError("rIcon: width must be even.")

		expected = height * width // 2
		if len(image) != expected:
			raise ValueError("rIcon: bad image size")

		if len(mask) != expected:
			raise ValueError("rIcon: bad mask size")

		self.type = 0x8000 if color else 0x0000
		self.image = bytes(image)
		self.mask = bytes(mask)
		self.height = height
		self.width = width

	def __bytes__(self):
		bb = struct.pack("<4H",
			self.type,
			len(self.image),
			self.height,
			self.width
		)

		return b"".join([bb, self.image, self.mask])

	def _rez_string(self):

		s = (
			"\t0x{:04x}, /* type */\n"
			"\t{:d}, /* height */\n"
			"\t{:d}, /* width */\n"
		).format(self.type, self.height, self.width)
		s += "\n\t/* image */\n"
		s += rez_hex(self.image, width = self.width // 2, indent = 1, comma = True)
		s += "\n\t/* mask */\n"
		s += rez_hex(self.mask, width = self.width // 2, indent = 1, comma = False)
		return s

