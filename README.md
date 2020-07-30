# prez
iigs resource compiler

An experimental alternative to rez.

Example:

```
rMenuBar(
  rMenu("@",
    rMenuItem("About My App..."),
    rMenuItem("Preferences...")
  ),
  rMenu(" File ",
    rMenuItem("New", "Nn"),
    rMenuItem("Open", "Oo"),
    rMenuItem("Save", "Ss"),
    rMenuItem("Print", "Pp")
  ),
)
```
This will generate rMenuBar, rMenu, rMenuItem, and rPString resources.
