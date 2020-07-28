

from base import *
from window import *
from control import *
from menu import *
from rect import rect, point, size

rPString("hello")
rCString("goodbye")

# rMenuItem("Hello")

rMenuBar(
	rMenu("@",
		rMenuItem("About..."),
		rMenuItem("Preferences...")
	),
	rMenu( " File ",
		rMenuItem("New", "Nn"),
		rMenuItem("Open", "Oo")
	),
	id=1
)

rTwoRects(rect(x=0,y=0,height=10, width=10), (1,2,3,4))
rRectList(rect(x=0,y=0,height=10, width=10), (1,2,3,4))

rSimpleButton(rect(x=10, y=10, height=13, width=90), "Save",default=True)


rWindParam1(rect(x = 20, y = 20, height=100, width=100), "hello")

rControlList(
	rThermometerControl( (5, 5, 10, 55), value = 10, scale=100)
)


rObject.dumphex()
rObject.dumprez()
