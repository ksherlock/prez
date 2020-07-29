

class Color:
	__slots__ = ("value")
	def __init__(self, value):
		self.value = value
# 640 mode colors

Transparent = Color(None)
Black = Color(0x00)
Blue = Color(0x01)
Olive = Color(0x02)
Gray1 = Color(0x03)
Red = Color(0x04)
Purple = Color(0x05)
Orange = Color(0x06)
Salmon = Color(0x07)
Green = Color(0x08)
Turquoise = Color(0x09)
BrightGreen = Color(0x0a)
DullGreen = Color(0x0b)
Gray2 = Color(0x0c)
LightBlue = Color(0x0d)
Yellow = Color(0x0e)
White = Color(0x0f)

# synonyms
Grey1 = Gray1
Grey2 = Gray2
DarkBlue = Blue
DarkGreen = Green
