# Creality Ender-3 S1 Pro - Cura Thumbnail + Info

This repository contains two Cura integrations for the same Creality thumbnail logic:

- `CuraPlugin/Creality_S1_Pro_Thumbnail_Info.py`: post-processing script
- `CuraAutoPlugin/CrealityS1ProAutoThumbnail`: auto-run Cura plugin

Tested against UltiMaker Cura 5.11 and Ender-3 S1 Pro.

## Features

- 300x300 JPEG thumbnail block for Creality firmware
- Auto-run export processing in plugin mode
- Save to Disk support
- Save to Removable Drive support
- Optional leveling injection with `M420 S1` or `G29`

## Auto-run plugin install

Copy:

`CuraAutoPlugin\CrealityS1ProAutoThumbnail`

to:

`%APPDATA%\cura\5.11\plugins\CrealityS1ProAutoThumbnail`

Restart Cura.

The plugin adds:

`Extensions -> S1 Pro Auto Thumbnail`

Default behavior is enabled automatically for G-code exports.

## Post-processing script install

Copy:

`CuraPlugin\Creality_S1_Pro_Thumbnail_Info.py`

to:

`%APPDATA%\cura\5.11\scripts\Creality_S1_Pro_Thumbnail_Info.py`

Restart Cura, then add it from:

`Extensions -> Post Processing -> Modify G-Code -> Add a script`

## Recommended defaults

- Thumbnail size: `300`
- JPEG quality: `85`
- Line prefix: `; `
- Base64 line length: `76`
- Creality tail numbers: `1 197 500`

## Troubleshooting

- If the printer shows no preview, try renaming the `.gcode` file because the printer can cache previews.
- If Cura fails to start after adding the plugin, remove it from `%APPDATA%\cura\5.11\plugins\`.
- If Cura fails to start after adding the script, remove it from `%APPDATA%\cura\5.11\scripts\`.

## License

MIT
