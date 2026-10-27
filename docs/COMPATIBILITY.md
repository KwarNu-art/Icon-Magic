# Compatibility

Research date: **2026-10-27**

Sources:

- https://pinpal.github.io/theme-guide/  
- https://github-wiki-see.page/m/Aizacktf/Snowboard/wiki/Home-Screen-Icons  
- https://www.sparkdev.me  
- https://repo.dynastic.co/snowboard  

## Format (iOS SnowBoard, not SnowBoardTV)

- Folder: `Name.theme/IconBundles/{bundleId}-large.png`  
- Recommended size: **180×180** (engine may rescale)  
- `Info.plist`: `PackageName`, `ThemeType=Icons`  

## Matrix

| Target | Status |
|--------|--------|
| Theme structure / PNG pipeline | verified against public docs |
| Package build on Linux CI | build-tested |
| iPhone 7 Plus + SnowBoard | **not tested on device** |
| Dynamic Clock/Calendar live digits | **not supported** in v1 (static glyph only) |
| Icon Effects / Masks extensions | optional; not required for base theme |

## Dynamic Clock / Calendar

SnowBoard can theme live Calendar via `CalendarIconDateSettings` in Info.plist. v1 ships a **static** calendar glyph only. Live date text is **not claimed**.
