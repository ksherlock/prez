import io
import sys
import os
import os.path

def _validate_mode(mode):
	# strips "t" format, adds "b" format, and checks if the 
	# base file needs to be created.
	# full validation will be handled by os.open
	r = False
	w = False
	plus = False
	rmode = "b"
	for x in mode:
		if x == "r": r = True
		elif x in ["a", "x", "w"]: w = True
		elif x in ["+"]: plus = True
		else: continue
		rmode += x

	mode = ["r", "a"][w]  # create if it does not exist.
	return (mode, rmode)

# There's a better way to handle this but I don't recall it offhand.
# - open() opener=argument!  opener(file,flags) -> fd
# - ... but that can't force it to be opened in binary mode.
def _open2(file, rfile, mode):

	a = None
	b = None

	(mode, rmode) = _validate_mode(mode)
	try:
		a = io.open(file, mode)
		b = io.open(rfile, rmode)
	except Exception as e:
		raise
	finally:
		if a: a.close()

	a.close()
	return b

_finder_magic = {
	(0x00, 0x0000): b"BINApdos",
	(0x04, 0x0000): b"TEXTpdos",
	(0xff, 0x0000): b"PSYSpdos",
	(0xb3, 0x0000): b"PS16pdos",
	(0xd7, 0x0000): b"MIDIpdos",
	(0xd8, 0x0000): b"AIFFpdos",
	(0xd7, 0x0001): b"AIFCpdos",
	(0xe0, 0x0005): b"dImgdCpy",
}
_z24 = bytearray(24)
def _make_finder_data(filetype, auxtype):

	k = (filetype, auxtype)
	x = _finder_magic.get((filetype, auxtype))
	if not x:
		x = struct.pack(">cBH4s", b'p', filetype & 0xff, auxtype & 0xffff, b"pdos")

	return x

if sys.platform == "win32":

	def open_rfork(file, mode="r"):
		# protect against c -> c:stream
		file = os.path.realpath(file)
		rfile = file + ":AFP_Resource"
		return _open2(file, rfile, mode)

	def set_file_type(path, filetype, auxtype):
		path = os.path.realpath(path)
		path += ":AFP_AfpInfo"
		f = open(path, "wb")

		data = struct.pack("<IIII8s24xHI8x",
			0x00504641, 0x00010000, 0, 0x80000000,
			_make_finder_data(filetype, auxtype),
			filetype, auxtype
		)

		f.write(data)
		f.close()
		return True


elif sys.platform == "darwin":
	def open_rfork(file, mode="r"):
		file = os.path.realpath(file)
		rfile = file + "/..namedfork/rsrc"
		return _open2(file, rfile, mode)

	# os.setxattr only available in linux.
	import ctypes
	_libc = ctypes.CDLL(None)
	_setxattr = _libc.setxattr
	_setxattr.argtypes = [ctypes.c_char_p, ctypes.c_char_p,
		ctypes.c_void_p, ctypes.c_size_t,
		ctypes.c_uint32, ctypes.c_int]
	def set_file_type(path, filetype, auxtype):

		data = struct.pack(">8s24x", _make_finder_data(filetype, auxtype))
		ok = _setxattr(path.encode("utf-8"), b"com.apple.FinderInfo", data, 32, 0, 0)
		e = ctypes.get_errno()
		if ok < 0: return False
		return True

elif sys.platform == "linux":	
	def open_rfork(file, mode="r"):
		raise NotImplementedError("open_rfork")

	def set_file_type(path, filetype, auxtype):

		data = struct.pack(">8s24x", _make_finder_data(filetype, auxtype))
		os.setxattr(path, "com.apple.FinderInfo", data, 0, 0)
		return True

else:
	def open_rfork(file, mode="r"):
		raise NotImplementedError("open_rfork")

	def set_file_type(path, filetype, auxtype):
		raise NotImplementedError("set_file_type")
