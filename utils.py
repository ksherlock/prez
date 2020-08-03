


# __all__ = ("str_to_bytes", "make_string", "format_rect", "format_point", "format_size")

# helper functions
def str_to_bytes(text):
	if isinstance(text, str): return text.encode("macroman")
	if isinstance(text, bytes): return text
	if isinstance(text, bytearray): return bytes(text)
	raise TypeError("Bad text type: {}".format(type(text)))



def format_rect(x):
	return "{{ {:d}, {:d}, {:d}, {:d} }}".format(*x)

def format_point(x):
	return "{{ {:d}, {:d} }}".format(*x)

def format_size(x):
	return "{{ {:d}, {:d} }}".format(*x)


def _generate_map():
	map = { x: "\\${:02x}".format(x) for x in range(0, 256) if x < 32 or x > 126 }
	map[0x0d] = "\\n" # intentionally backwards.
	map[0x0a] = "\\r" # intentionally backwards.
	map[0x09] = "\\t"
	# \b \f \v \? also supported. 
	map[ord('"')] = '\\"'
	map[ord("'")] = "\\'"
	map[ord("\\")] = "\\\\"
	# map[0x7f] = "\\?" # rubout

	return map

_map = _generate_map()

def format_string(bstring, quote=True):
	s = "".join([_map[x] if x in _map else chr(x) for x in bstring])
	if quote: return '"' + s + '"'
	return s

def format_char(x):
	c = _map.get(x, chr(x))
	return "'" + c + "'"

def multi_format_string(bstring, indent=""):
	q = '"'

	rv = []
	tmp = [indent + q]
	for x in bstring:
		if x in _map: tmp.append(_map[x])
		else: tmp.append(chr(x))
		if len(tmp) > 32 or x == 0x0a:
			tmp.append(q)
			rv.append("".join(tmp))
			tmp = [indent + q]
	if len(tmp)>1:
		tmp.append(q)
		rv.append("".join(tmp))
	return ("\n").join(rv)