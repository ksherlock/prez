# point(h,v) or point(x=.., y=..)

import struct

__all__ = ['point', 'rect', 'size']


# struct Point {
#    short v;
#    short h;
#    };

# struct Rect {
#    short v1;
#    short h1;
#    short v2;
#    short h2;
#    };

def all_defined(*args): return args.count(None)==0
def all_none(*args): return args.count(None)==len(args)
def is_listy(x): return type(x) in (tuple, list)


def old_point(*args, x=None, y=None, h=None, v=None):

	if len(args) == 2: return args

	if len(args) == 1:
		a, = args
		if is_listy(a) and len(a) == 2:
			return a

	if not args:
		if all_defined(x,y): return (y, x)
		if all_defined(h,v): return (v, h)
	raise ValueError("bad point parameter")


class point_class:
	"""docstring for point_class"""
	__slots__ = ('x', 'y')
	def __init__(self, *args, x=None, y=None, h=None, v=None):
		self.x = 0
		self.y = 0

		if len(args) == 2:
			self._assign(*args)
			return

		if len(args) == 1:
			other = args[0]
			if (type(other) == point_class):
				self.x = other.x;
				self.y = other.y
				return

			if is_listy(other) and len(other) == 2:
				self._assign(*other)
				return

		if not args:
			if all_defined(x,y):
				self.x = x
				self.y = y
				return
			if all_defined(h,v):
				self.x = h
				self.y = v
				return

		raise ValueError("bad point parameter")

	def _assign(self, v, h):
		self.x = h
		self.y = v

	def __str__(self):
		return "{{ {:d}, {:d} }}".format(self.y, self.x)

	def __bytes__(self):
		return struct.pack("2H", self.y, self.x)

	def __iter__(self):
		return (self.y, self.x).__iter__()

	def __eq__(self, other):
		return type(other) == point_class and self.x == other.x and self.y == other.y

	def __add__(self, other):
		if type(other) != point_class: ValueError("bad point parameter")
		return point_class(x = self.x + other.x, y = self.y + other.y)

	def __sub__(self, other):
		if type(other) != point_class: ValueError("bad point parameter")
		return point_class(x = self.x - other.x, y = self.y - other.y)


class size_class:
	__slots__ = ('height', 'width')
	def __init__(self, *args, height=None, width=None):

		self.height = 0
		self.width = 0

		if len(args) == 2:
			self._assign(*args)
			return

		if len(args) == 1:
			other = args[0]
			if type(other) == size_class:
				self.height = other.height
				self.width = other.width
				return

			if is_listy(other) and len(other) == 2:
				self._assign(*other)
				return

		if not args:
			if all_defined(height,width):
				self.height = height
				self.width = width
				return

		raise ValueError("bad size parameter")

	def _assign(self, height, width):
		self.height = height
		self.width = width

	def __eq__(self, other):
		return type(other) == size_class and self.height == other.height and self.width == other.width

	def __str__(self):
		return "{{ {:d}, {:d} }}".format(self.height, self.width)

	def __bytes__(self):
		return struct.pack("2H", self.height, self.width)

	def __iter__(self):
		return (self.height, self.width).__iter__()


def old_size(*args, height=None, width=None):

	if len(args) == 2: return args

	if len(args) == 1:
		a, = args
		if is_listy(a) and len(a) == 2:
			return a

	if not args:
		if all_defined(height,width): return (height, width)
	raise ValueError("bad size parameter")


def old_rect(*args,
	x=None,y=None,height=None,width=None,
	h1=None,h2=None,v1=None,v2=None,
	top=None,left=None,right=None,bottom=None):

	if len(args) == 4: return args

	if len(args) == 2:
		a, b = args
		if is_listy(a) and is_listy(b):
			if len(a) == 2 and len(b) == 2:
				return ( *a, *b )

	if len(args) == 1:
		a, = args
		if is_listy(a) and len(a) == 4: return a

	if not args:
		if all_defined(x,y,height,width):
			return (y, x, y + height, x + width)
		if all_defined(h1,h2,v1,v2):
			return (v1, h1, v2, h2)
		if all_defined(top,left,bottom,right):
			return (top, left, bottom, right)

	raise ValueError("bad rect parameter")


class rect_class:
	__slots__ = ('x', 'y', 'height', 'width')
	def __init__(self, *args,
		x=None,y=None,height=None,width=None,
		h1=None,h2=None,v1=None,v2=None,
		top=None,left=None,right=None,bottom=None):

		self.x = 0
		self.y = 0
		self.height = 0
		self.width = 0

		if len(args) == 4:
			self._assign(*args)
			return

		if len(args) == 2:
			a, b = args
			if type(a) == point_class and type(b) == point_class:
				self.x = a.x
				self.y = a.y
				self.width = b.x - a.x
				self.height = b.y - a.y
				return

			if type(a) == point_class and type(b) == size_class:
				self.x = a.x
				self.y = a.y
				self.height = b.height
				self.width = b.width
				return

			if is_listy(a) and is_listy(b):
				if len(a) == 2 and len(b) == 2:
					self._assign(*a, *b)
					return

		if len(args) == 1:
			args = args[0]
			if type(args) == rect_class:
				self.x = args.x
				self.y = args.y
				self.height = args.height
				self.width = args.width
				return

			if is_listy(args) and len(args) == 4:
				self._assign(*args)
				return

		if not args:
			if all_defined(x,y,height,width):
				self.x = x
				self.y = y
				self.height = height
				self.width = width
				return

			if all_defined(h1,h2,v1,v2):
				self._assign(v1, h1, v2, h2)
				return

			if all_defined(top,left,bottom,right):
				self._assign(top, left, bottom, right)
				return

		raise ValueError("bad rect parameter")


	def _assign(self, v1, h1, v2, h2):
		self.x = h1
		self.y = v1
		self.width = h2 - h1
		self.height = v2 - v1

	def center(self, width = 640, height = 200):
		x = (width - self.width) // 2
		y = (height - self.height) // 2
		return self.offset_to(x, y)


	def center_640(self):
		x = (640 - self.width) // 2
		y = (200 - self.height) // 2
		return self.offset_to(x, y)
	
	def center_320(self):
		x = (320 - self.width) // 2
		y = (200 - self.height) // 2
		return self.offset_to(x, y)

	def inset_by(self, horizontal, vertical):
		return rect_class(
			x = self.x + horizontal,
			y = self.y + vertical,
			width = self.width - horizontal,
			height = self.height - vertical
		)

	def offset_to(self, x, y):
		return rect_class(
			x = x,
			y = y,
			width = self.width,
			height = self.height
		)

	def offset_by(self, horizontal, vertical):
		return rect_class(
			x = self.x + horizontal,
			y = self.y + vertical,
			width = self.width,
			height = self.height
		)

	def top_left(self):
		return point_class(x = self.x, y = self.y)

	def top_right(self):
		return point_class(x = self.x + self.width, y = self.y)

	def bottom_left(self):
		return point_class(x = self.x, y = self.y + self.height)


	def bottom_right(self):
		return point_class(x = self.x + self.width, y = self.y + self.height)


	def __str__(self):
		return "{{ {:d}, {:d}, {:d}, {:d} }}".format(self.y, self.x, self.y + self.height, self.x + self.width)

	def __bytes__(self):
		return struct.pack("4H", self.y, self.x, self.y + self.height, self.x + self.width)

	def __iter__(self):
		return (self.y, self.x, self.y + self.height, self.x + self.width).__iter__()

	def __eq__(self, other):
		return type(other) == rect_class and \
		self.x == other.x and self.y == other.y and \
		self.width == other.width and self.height == other.height

	def __bool__(self):
		# check if valid
		return self.width >= 0 and self.height >= 0

	def __and__(self, other):
		# intersection
		if type(other) != rect_class: ValueError("bad rect parameter")

		x1 = max(self.x, other.x)
		y1 = max(self.y, other.y)
		x2 = min(self.x + self.width, other.x + other.width)
		y2 = min(self.y + self.height, other.y + other.height)

		return rect_class(v1 = y1, h1 = x1, v2 = y2, h2 = x2)

	def __or__(self, other):
		# union
		if type(other) != rect_class: ValueError("bad rect parameter")

		x1 = min(self.x, other.x)
		y1 = min(self.y, other.y)
		x2 = max(self.x + self.width, other.x + other.width)
		y2 = max(self.y + self.height, other.y + other.height)

		return rect_class(v1 = y1, h1 = x1, v2 = y2, h2 = x2)

point = point_class
rect = rect_class
size = size_class
