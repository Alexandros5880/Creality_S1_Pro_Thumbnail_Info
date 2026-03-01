# Creality S1 Pro Auto Thumbnail

Auto-run Cura extension plugin for Creality-compatible JPG thumbnails.

## Install

For manual installation, extract the packaged archive and copy the plugin folder to:

`%APPDATA%\cura\5.11\plugins\CrealityS1ProAutoThumbnail`

Restart UltiMaker Cura.

The distributable archive is built by running:

`powershell -ExecutionPolicy Bypass -File .\build_package.ps1`

## Behavior

- Runs automatically on `Save to Disk`
- Runs automatically on `Save to Removable Drive`
- Adds a Creality JPG thumbnail block to `.gcode`
- Can optionally insert `M420 S1` or `G29` after the first `G28`
- Settings are stored in Cura preferences

## Notes

- `plugin.json` and `__init__.py` are included for Cura plugin loading
- `build_package.ps1` creates a clean zip without `__pycache__` files
- Marketplace publication still requires UltiMaker account/submission steps outside this repo
