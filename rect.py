# point(h,v) or point(x=.., y=..)

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


def point(*args, x=None, y=None, h=None, v=None):

	if len(args) == 2: return args

	if len(args) == 1:
		a, = args
		if is_listy(a) and len(a) == 2:
			return a

	if not args:
		if all_defined(x,y): return (y, x)
		if all_defined(h,v): return (v, h)
	raise ValueError("bad point parameter")

def size(*args, height=None, width=None):

	if len(args) == 2: return args

	if len(args) == 1:
		a, = args
		if is_listy(a) and len(a) == 2:
			return a

	if not args:
		if all_defined(height,width): return (height, width)
	raise ValueError("bad size parameter")


def rect(*args,
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

