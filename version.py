
from base import rObject
from utils import *
import enum
import struct
import re

__all__ = ["rVersion"]

class Region(enum.Enum):

	verUS = 0
	verFrance = 1
	verBritain = 2
	verGermany = 3
	verItaly = 4
	verNetherlands = 5
	verBelgiumLux = 6
	verFrBelgiumLux = 6 # alias
	verSweden = 7
	verSpain = 8
	verDenmark = 9
	verPortugal = 10
	verFrCanada = 11
	verNorway = 12
	verIsrael = 13
	verJapan = 14
	verAustralia = 15
	verArabia = 16
	verArabic = 16 # alias
	verFinland = 17
	verFrSwiss = 18
	verGrSwiss = 19
	verGreece = 20
	verIceland = 21
	verMalta = 22
	verCyprus = 23
	verTurkey = 24
	verYugoslavia = 25
	verYugoCroatian = 25 # alias
	verIndia = 33
	verIndiaHindi = 33 # alias
	verPakistan = 34

	verLithuania = 41
	verPoland = 42
	verHungary = 43

	verEstonia = 44
	verLatvia = 45
	verLapland = 46
	verFaeroeIsl = 47
	verIran = 48
	verRussia = 49
	verIreland = 50
	verKorea = 51

	verChina = 52
	verTaiwan = 53
	verThailand = 54


# import enums.
globals().update(Region.__members__)
__all__.extend(list(Region.__members__))

def _version_to_version(vstr):
	# 1 - major
	# 1.2 - major.minor
	# 1.2.3 - major.minor.bug
	# 1.2.3 [dabfr] - major.minor.bug develop/alpha/beta/final/release
	# 1.2.3r4 - major.minor.bug stage release version

	# release implies release version of 0.

	major = 0
	minor = 0
	bug = 0
	stage = 'r'
	release = 0

	m = re.match(r"([0-9.]+)([dabfr])(\d+)?$", vstr)
	if not m: raise ValueError("Bad version string: {}".format(vstr))

	stage = m[2]
	release = int(m[3], 10)

	vv = m[1].split('.')
	if len(vv) < 1 or len(vv) > 3 or not all(vv):
		raise ValueError("Bad version string: {}".format(vstr))

	if len(vv) >= 1: major = int(vv[0], 10)
	if len(vv) >= 2: minor = int(vv[1], 10)
	if len(vv) >= 3: bug = int(vv[2], 10)

	# convert to bcd format.  25 (base 10) -> 0x25 (base 16)
	if major > 99: raise ValueError("major version too big: {}".format(major))
	if minor > 9: raise ValueError("minor version too big: {}".format(minor))
	if bug > 9: raise ValueError("bug version too big: {}".format(bug))
	if release > 99: raise ValueError("release version too big: {}".format(release))

	major = (major % 10) + (major // 10) * 16
	release = (release % 10) + (release // 10) * 16

	return (major, minor, bug, stage, release)

class rVersion(rObject):
	rName = "rVersion"
	rType = 0x8029

	def __init__(self, version, region, short, long, **kwargs):
		super().__init__(**kwargs)

		self.version = _version_to_version(version)
		self.region = region
		self.short = str_to_bytes(short)
		self.long = str_to_bytes(long)

	def __bytes__(self):
		major, minor, bug, stage, release = self.version

		stagemap = {
			'd': 0b0010_0000,
			'a': 0b0100_0000,
			'b': 0b0110_0000,
			'f': 0b1000_0000,
			'r': 0b1010_0000,
		}

		bb = struct.pack("<4BH",
			release,
			stagemap[stage],

			(minor << 4) + (bug),
			major,

			self.region.value
		)

		bb += bytes( (len(self.short), ) )
		bb += self.short

		bb += bytes( (len(self.long), ) )
		bb += self.long

		return bb

	def _rez_string(self):

		stagemap = {
			'd': 'develop',
			'a': 'alpha',
			'b': 'beta',
			'f': 'final',
			'r': 'release',
		}
		major, minor, bug, stage, release = self.version

		return (
			"\t{{ ${:02x}, ${:02x}, ${:02x}, {}, ${:02x} }}, /* version */\n"
			"\t{}, /* region */\n"
			"\t{}, /* short name */\n"
			"\t{} /* more info */".format(
				major, minor,bug, stagemap[stage], release,
				self.region.name,
				format_string(self.short),
				format_string(self.long)
		))
