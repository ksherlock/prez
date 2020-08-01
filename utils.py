


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


# def make_string(text, rType=None):
# 	if not rType: rType = rPString
# 	if type(text) == rType: return text
# 	if type(text) in (str, bytes, bytearray): return rType(text)
# 	raise TypeError("Bad text type: {}".format(type(text)))

