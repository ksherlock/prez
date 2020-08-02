
from base import rObject
import audioop
import struct
import re
import sys
import os
from math import log2

__all__ = ["rSoundSample"]

# See: IIgs TechNote #76 Miscellaneous Resource Formats
# See: HCGS TechNote #3 Pitching Sampled Sounds

# HyperCard assumes a sample rate of 26.32 KHz (DOC rate w/ 32 oscillators)
# and a pitch of 261.63 Hz (Middle C, C4)
# See HyperCard IIgs Tech Note #3: Pitching Sampled Sounds
def relative_pitch(fS, fW = None):
	# fW = frequency of sample
	# fS = sampling rate

	r = 0
	if fW: r = (261.63 * fS) / (26320 * fW)
	else: r = fS / 26320


	offset = round(3072 * log2(r))
	if (offset < -32767) or (offset > 32767):
		raise Exception("Audio error: offset too big")
	if offset < 0: offset = 0x8000 | abs(offset)
	return offset


def pitch_to_hz(p):
	if p == None: return 261.63
	if type(p) in (int, float): return float(p)
	if type(p) == str:
		m = re.match("^([A-Ga-g])([#b])?([0-8])$", p)
		if not m: return None
		note = m1[1].upper(); accidental = m[2]; octave = int(m[3])

		a = "CxDxEFxGxAxB".index(note)-9
		if accidental == "#": a += 1
		if accidental == "b": a -= 1

		f = 440.0 * (2 ** (a/12))
		f *= 2 ** (octave-4)
		return f

	return None

def open_audio(file):

	_, ext = os.path.splitext(os.path.basename(file))
	ext = ext.lower()

	# if ext in (".wav", ".wave"):
	# 	import wave
	# 	return wave.open(file, "rb"), 'little', 128


	if ext in (".aiff", ".aifc", ".aif"):
		import aifc
		return aifc.open(file, "rb"), 'big', 'AIFF'

	if ext in (".au", ".snd"):
		import sunau
		return sunau.open(file, "rb"), 'big', 'SUN'

	# default
	import wave
	return wave.open(file, "rb"), 'little', 'WAVE'


class rSoundSample(rObject):
	"""
	filename: input file to read. format is .wav, .au, .aiff, or .aifc
	pitch: audio pitch, if this is a note. specify hz (eg 261.63) or name (eg c4)
	rate: down/upsample audio to this rate (eg 26320)
	channel: stereo channel 

	Native samples are 26320 khz, c4 (261.63 hz)
	"""

	rName = "rSoundSample"
	rType = 0x8024

	def __init__(self, filename, pitch=None, rate=None, channel=0, **kwargs):

		super().__init__(**kwargs)

		new_rate = rate
		freq = pitch_to_hz(pitch)
		if not freq: raise ValueError("Invalid pitch: {}".format(pitch))

		# audio conversion

		verbose = False
		# if verbose: print("Input File: {}".format(filename))


		rv = bytearray()
		tr = b"\x01" + bytes(range(1,256)) # remap 0 -> 1


		rv += struct.pack("<10x") # header filled in later

		src, byteorder, fmt = open_audio(filename)

		width = src.getsampwidth()
		channels = src.getnchannels()
		rate = src.getframerate()
		bias = 128
		swap = width > 1 and sys.byteorder != byteorder
		if width == 1 and fmt == 'wave': bias = 0

		if verbose:
			print("Input:  {} ch, {} Hz, {}-bit, {} ({} frames)".format(
					channels,
					rate,
					width*8,
					fmt,
					src.getnframes()
			))

		if channels > 2:
			raise Exception("{}: Too many channels ({})".format(filename, channels))


		cookie = None
		while True:
			frames = src.readframes(32)
			if not frames: break

			if swap:
				frames = audioop.byteswap(frames, width)

			if channels > 1:
				frames = audioop.tomono(frames, width, 0.5, 0.5)

			if new_rate:
				frames, cookie = audioop.ratecv(frames, width, 1, rate, new_rate, cookie)

			if width != 1:
				frames = audioop.lin2lin(frames, width, 1)
			if bias:
				frames = audioop.bias(frames, 1, bias)

			frames = frames.translate(tr)
			rv += frames
		src.close()

		# based on system 6 samples, pages rounds down....
		# probably a bug.
		pages = (len(rv)-10+255) >> 8
		hz = new_rate or rate
		rp = relative_pitch(hz, freq)

		struct.pack_into("<HHHHH", rv, 0,
			0, # format
			pages, # wave size in pages
			rp,
			channel, # stereo
			hz # hz
		)

		self.data = bytes(rv)
		self.pages = pages
		self.channel = channel
		self.relative_pitch = rp
		self.sample_rate = hz

		if verbose:
			print("Output: 1 ch, {} Hz, 8-bit, rSoundSample ({} frames, {:.02f} Hz)".format(
				hz, len(rv)-10, freq or 261.63))
			print()




	def __bytes__(self):
		return self.data

	def _rez_string(self):
		return (
			"\t0, /* format */\n"
			"\t{}, /* size (pages) */\n"
			"\t0x{:04x}, /* relative pitch */\n"
			"\t0x{:04x}, /* stereo channel */\n"
			"\t{:d}, /* sample rate */\n"
			"\t..."
			).format(
				self.pages,
				self.relative_pitch,
				self.channel,
				self.sample_rate
			)


