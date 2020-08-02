# prez
iigs resource compiler

An experimental alternative to rez.

Example:

```
rMenuBar(
  rMenu(" @ ",
    rMenuItem("About My App…", export="kAboutMenuItem"),
    rMenuItem("Preferences…", ",", export="kPreferencesMenuItem")
  ),
  rMenu(" File ",
    rMenuItem("New ", "Nn", export="kNewMenuItem"),
    rMenuItem("Open…", "Oo", export="kOpenMenuItem"),
    rMenuItem("Save", "Ss", disabled=True, export="kSaveMenuItem"),
    DividerMenuItem(),
    rMenuItem("Close", "Ww", id=0xff, export="kCloseMenuItem"),
    export = "kFileMenu"
  ),
  rMenu(" Edit ",
    UndoMenuItem(), # shortcut for doing it manually,
    DividerMenuItem(),
    CutMenuItem(),
    CopyMenuItem(),
    PasteMenuItem(),
    ClearMenuItem(),
    export = "kEditMenu"
  ),
  export = "kMenuBar"
)
```

This will generate rMenuBar, rMenu, rMenuItem, and rPString resources.

Note that the input file is actually a python program that generates a 
resource fork as a side effect.


```
resource rMenuItem($00000101) {
  0x0100, /* id */
  "", "", /* chars */
  0x0000, /* check */
  0x8000, /* flags */
  0x0001 /* title ref (rPString) */
}

resource rMenuItem($00000103) {
  0x0102, /* id */
  ",", ",", /* chars */
  0x0000, /* check */
  0x8000, /* flags */
  0x0002 /* title ref (rPString) */
}

resource rMenuItem($00000105) {
  0x0104, /* id */
  "N", "n", /* chars */
  0x0000, /* check */
  0x8000, /* flags */
  0x0003 /* title ref (rPString) */
}

resource rMenuItem($00000107) {
  0x0106, /* id */
  "O", "o", /* chars */
  0x0000, /* check */
  0x8000, /* flags */
  0x0004 /* title ref (rPString) */
}

resource rMenuItem($00000109) {
  0x0108, /* id */
  "S", "s", /* chars */
  0x0000, /* check */
  0x8080, /* flags */
  0x0005 /* title ref (rPString) */
}

resource rMenuItem($0000010b) {
  0x010a, /* id */
  "", "", /* chars */
  0x0000, /* check */
  0x8080, /* flags */
  0x0006 /* title ref (rPString) */
}

resource rMenuItem($000000ff) {
  0x00ff, /* id */
  "W", "w", /* chars */
  0x0000, /* check */
  0x8000, /* flags */
  0x0007 /* title ref (rPString) */
}

resource rMenuItem($0000010c) {
  0x00fa, /* id */
  "Z", "z", /* chars */
  0x0000, /* check */
  0x8000, /* flags */
  0x0008 /* title ref (rPString) */
}

resource rMenuItem($0000010e) {
  0x010d, /* id */
  "", "", /* chars */
  0x0000, /* check */
  0x8080, /* flags */
  0x0009 /* title ref (rPString) */
}

resource rMenuItem($0000010f) {
  0x00fb, /* id */
  "X", "x", /* chars */
  0x0000, /* check */
  0x8000, /* flags */
  0x000a /* title ref (rPString) */
}

resource rMenuItem($00000110) {
  0x00fc, /* id */
  "C", "c", /* chars */
  0x0000, /* check */
  0x8000, /* flags */
  0x000b /* title ref (rPString) */
}

resource rMenuItem($00000111) {
  0x00fd, /* id */
  "V", "v", /* chars */
  0x0000, /* check */
  0x8000, /* flags */
  0x000c /* title ref (rPString) */
}

resource rMenuItem($00000112) {
  0x00fe, /* id */
  "", "", /* chars */
  0x0000, /* check */
  0x8000, /* flags */
  0x000d /* title ref (rPString) */
}

resource rPString($0000000e) {
  "About My App\$c9"
}

resource rPString($0000000f) {
  "Preferences\$c9"
}

resource rPString($00000010) {
  " @ "
}

resource rPString($00000011) {
  "New "
}

resource rPString($00000012) {
  "Open\$c9"
}

resource rPString($00000013) {
  "Save"
}

resource rPString($00000014) {
  "-"
}

resource rPString($00000015) {
  "Close"
}

resource rPString($00000016) {
  " File "
}

resource rPString($00000017) {
  "Undo"
}

resource rPString($00000018) {
  "-"
}

resource rPString($00000019) {
  "Cut"
}

resource rPString($0000001a) {
  "Copy"
}

resource rPString($0000001b) {
  "Paste"
}

resource rPString($0000001c) {
  "Clear"
}

resource rPString($0000001d) {
  " Edit "
}

resource rMenu($00000002) {
  0x0001, /* menu ID */
  0xa000, /* flags */
  0x0000001e, /* title ref (rPString) */
  {
    0x00000113,
    0x00000114
  }
}

resource rMenu($00000004) {
  0x0003, /* menu ID */
  0xa000, /* flags */
  0x0000001f, /* title ref (rPString) */
  {
    0x00000115,
    0x00000116,
    0x00000117,
    0x00000118,
    0x000000ff
  }
}

resource rMenu($00000006) {
  0x0005, /* menu ID */
  0xa000, /* flags */
  0x00000020, /* title ref (rPString) */
  {
    0x00000119,
    0x0000011a,
    0x0000011b,
    0x0000011c,
    0x0000011d,
    0x0000011e
  }
}

resource rMenuBar($00000001) {
  {
    0x00000007,
    0x00000008,
    0x00000009
  }
}
```

```
#define kAboutMenuItem 0x0000011f
#define kPreferencesMenuItem 0x00000120
#define kNewMenuItem 0x00000121
#define kOpenMenuItem 0x00000122
#define kSaveMenuItem 0x00000123
#define kCloseMenuItem 0x000000ff
#define kFileMenu 0x0000000a
#define kEditMenu 0x0000000b
#define kMenuBar 0x00000002
```
