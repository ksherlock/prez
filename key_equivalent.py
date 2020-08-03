# key equivalants
import enum
from utils import *
import struct

__all__ = ["KeyEquiv"]

def export_enum(cls):
	global __all__

	members = cls.__members__
	globals().update(members)
	if __all__ != None: __all__.extend(list(members))
	return cls	

@export_enum
class Keys(enum.Flag):
	appleKey = 0x0100 		# set if Apple key down
	shiftKey = 0x0200 		# set if shift key down
	capsLock = 0x0400 		# set if caps lock key down
	optionKey = 0x0800 		# set if option key down
	controlKey = 0x1000 	# set if Control key down
	keyPad = 0x2000 		# set if keypress from key pad


# See: TB Volume 3, 28-47

# def KeyEquivalent(keys, keyModifiers=None, keyCareBits=None):

#define KeyEquiv  array[1]{ char; char; _mybase_ word; _mybase_ word; }
class KeyEquivalent:

	"""
	keys: ascii character(s) for the upper and lower-case keys.
	keyModifiers:  appleKey|shiftKey|capsLock|optionKey|controlKey|keyPad
	keyCareBits:  default = keyModifiers

	"""

	__slots__ = ("keys", "keyModifiers", "keyCareBits")

	def __init__(self, keys, keyModifiers=None, keyCareBits=None):
		if keyModifiers == None: keyModifiers = 0
		elif type(keyModifiers) == Keys: keyModifiers = keyModifiers.value
		elif type(keyModifiers) == int: pass
		else:
			raise TypeError("KeyEquivalent: bad modifier type: {}".format(type(keyModifiers)))

		if keyCareBits == None: keyCareBits = keyModifiers
		elif type(keyCareBits) == Keys: keyCareBits = keyCareBits.value
		elif type(keyCareBits) == int: pass
		else:
			raise TypeError("KeyEquivalent: bad modifier type: {}".format(type(keyCareBits)))


		if type(keys) not in (bytes, str):
			raise TypeError("KeyEquivalent: bad keys type: {}".format(type(keys)))

		keys = str_to_bytes(keys)
		if len(keys) == 1: keys *= 2

		if len(keys) != 2:
			raise ValueError("KeyEquivalent: bad keys: {}".format(keys))

		self.keys = keys
		self.keyModifiers = keyModifiers
		self.keyCareBits = keyModifiers

		# return (keys, keyModifiers, keyCareBits)

	def __bytes__(self):
		return struct.pack("<BBHH", *self.keys, self.keyCareBits, self.keyModifiers)

	def __str__(self):
		return  "{{ {}, {}, 0x{:04x}, 0x{:04x} }}".format(
			format_char(self.keys[0]),
			format_char(self.keys[1]),
			self.keyModifiers,
			self.keyCareBits
		)
