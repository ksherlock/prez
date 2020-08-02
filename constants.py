

# resource attributes
attrPage = 0x0004   
attrNoSpec = 0x0008 
attrNoCross = 0x0010
# resChanged = 0x0020
resPreLoad = 0x0040
resProtected = 0x0080
attrPurge1 = 0x0100
attrPurge2 = 0x0200
attrPurge3 = 0x0300
resAbsLoad = 0x0400
resConverter = 0x0800
attrFixed = 0x4000
attrLocked = 0x8000

attrPurge = 0x0300

# window constants
fHilited            = 0x0001
fZoomed             = 0x0002
fAllocated          = 0x0004
fCtlTie             = 0x0008
fInfo               = 0x0010
fVis                = 0x0020
fQContent           = 0x0040
fMove               = 0x0080
fZoom               = 0x0100
fFlex               = 0x0200
fGrow               = 0x0400
fBScroll            = 0x0800
fRScroll            = 0x1000
fAlert              = 0x2000
fClose              = 0x4000
fTitle              = 0x8000

# menu item flags (duplicate menu flags.)
rMIPlain            = 0x0000
rMIBold             = 0x0001
rMIItalic           = 0x0002
rMIUnderline        = 0x0004
rMIXOr              = 0x0020
rMIDivider          = 0x0040
rMIDisabled         = 0x0080
rMIItemStruct       = 0x0400
rMIOutline          = 0x0800
rMIShadow           = 0x1000

# menu flags
rmAllowCache        = 0x0008
rmCustom            = 0x0010
rmNo_Xor            = 0x0020
rmDisabled          = 0x0080


# common flags
ctlInvis            = 0x0080
ctlVisible          = 0x0000
ctlInactive         = 0xFF00

# more flags
ctlTarget          = 0x8000
ctlCanBeTarget     = 0x4000
ctlWantsEvents     = 0x2000
CtlWantEvents      = 0x2000   # spelling variant
ctlProcNotPtr      = 0x1000
ctlTellAboutSize   = 0x0800
ctlIsMultiPart     = 0x0400

# stat text control flags
fSquishText         = 0x0010   # 6.0.1
fTextCanDim         = 0x0008   # 6.0
fBlastText          = 0x0004   # 6.0
fSubstituteText     = 0x0002
fSubTextIsPascal    = 0x0001
fSubTextIsC         = 0x0000

# simple button flags
NormalButton        = 0x0000
DefaultButton       = 0x0001
SquareButton        = 0x0002
SquareShadowButton  = 0x0003

# Text Edit Control text flags
fNotControl             = 0x80000000
fSingleFormat           = 0x40000000
fSingleStyle            = 0x20000000
fNoWordWrap             = 0x10000000
fNoScroll               = 0x08000000
fReadOnly               = 0x04000000
fSmartCutPaste          = 0x02000000
fTabSwitch              = 0x01000000
fDrawBounds             = 0x00800000
fColorHilight           = 0x00400000
fGrowRuler              = 0x00200000
fDisableSelection       = 0x00100000
fDrawInactiveSelection  = 0x00080000

# LE Text Box 2 style.  bytes since non-ascii chars involved.
TBStylePlain        = b"\x01S\x00\x00" # $01 $53 $00 $00
TBStyleBold         = b"\x01S\x01\x00" # $01 $53 $00 $00
TBStyleItalic       = b"\x01S\x02\x00" # $01 $53 $00 $00
TBStyleUnderline    = b"\x01S\x04\x00" # $01 $53 $00 $00
TBStyleOutline      = b"\x01S\x08\x00" # $01 $53 $00 $00
TBStyleShadow       = b"\x01S\x10\x00" # $01 $53 $00 $00
TBStyleHEX          = b"\x01S"
TBForeColor         = b"\x01C"
TBBackColor         = b"\x01B"
TBColor0            = b"\x00\x00"
TBColor1            = b"\x11\x11"
TBColor2            = b"\x22\x22"
TBColor3            = b"\x33\x33"
TBColor4            = b"\x44\x44"
TBColor5            = b"\x55\x55"
TBColor6            = b"\x66\x66"
TBColor7            = b"\x77\x77"
TBColor8            = b"\x88\x88"
TBColor9            = b"\x99\x99"
TBColorA            = b"\xAA\xAA"
TBColorB            = b"\xBB\xBB"
TBColorC            = b"\xCC\xCC"
TBColorD            = b"\xDD\xDD"
TBColorE            = b"\xEE\xEE"
TBColorF            = b"\xFF\xFF"
TBLeftJust          = b"\x01J\x00\x00"
TBCenterJust        = b"\x01J\x01\x00"
TBRightJust         = b"\x01J\xFF\xFF"
TBFillJust          = b"\x01J\x02\x00"
TBLeftMargin        = b"\x01L"
TBRightMargin       = b"\x01M"
TBSpExtra           = b"\x01X"
TBEndOfLine         = b"\r"
TBFont              = b"\x01F"
TBShaston           = b"\xFE\xFF"
TBNewYork           = b"\x02\x00"
TBGeneva            = b"\x03\x00"
TBVenice            = b"\x05\x00"
TBTimes             = b"\x14\x00"
TBHelvetica         = b"\x15\x00"
TBCourier           = b"\x16\x00"
