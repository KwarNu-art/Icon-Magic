# Install

## Dependencies

- Jailbroken iPhone  
- **SnowBoard** package id `com.spark.snowboard` from https://www.sparkdev.me  

## Choose package

| Jailbreak style | Architecture field | Path themes land in |
|-----------------|--------------------|---------------------|
| Rootful (e.g. checkra1n-class) | `iphoneos-arm` | `/Library/Themes` |
| Rootless | `iphoneos-arm64` | `/var/jb/Library/Themes` |

## Steps

1. Transfer the `.deb` to the device.  
2. Install with Sileo / Zebra / Cydia / `dpkg -i`.  
3. Open **Settings → SnowBoard**.  
4. Enable the Icon-Magic theme under icons.  
5. Respring only if the engine prompts you.

## Uninstall

Remove the package from your package manager. Only package-owned files under Themes are removed.

## Restore stock icons

Disable the theme in SnowBoard (or uninstall the package), then respring if needed.
