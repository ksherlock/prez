

class _Color:
	__slots__ = ("value")
	def __init__(self, value):
		self.value = value
# 640 mode _colors

Transparent = _Color(None)
Black = _Color(0x00)
Blue = _Color(0x01)
Olive = _Color(0x02)
Gray1 = _Color(0x03)
Red = _Color(0x04)
Purple = _Color(0x05)
Orange = _Color(0x06)
Salmon = _Color(0x07)
Green = _Color(0x08)
Turquoise = _Color(0x09)
BrightGreen = _Color(0x0a)
DullGreen = _Color(0x0b)
Gray2 = _Color(0x0c)
LightBlue = _Color(0x0d)
Yellow = _Color(0x0e)
White = _Color(0x0f)

# synonyms
Grey1 = Gray1
Grey2 = Gray2
DarkBlue = Blue
DarkGreen = Green
