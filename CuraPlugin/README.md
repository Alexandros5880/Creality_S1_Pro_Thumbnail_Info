# Creality S1 Pro Auto Thumbnail

Auto-run Cura extension plugin for Creality-compatible JPG thumbnails.

## Install

Copy this folder to:

`%APPDATA%\cura\5.11\plugins\CrealityS1ProAutoThumbnail`

Restart UltiMaker Cura.

## Behavior

- Runs automatically on `Save to Disk`
- Runs automatically on `Save to Removable Drive`
- Adds a Creality JPG thumbnail block to `.gcode`
- Optional bed leveling commands are stored in Cura preferences

## Notes

- `plugin.json` and `__init__.py` are included for Cura plugin loading
- `build_package.ps1` in the parent folder creates a distributable zip
- Marketplace publication still requires UltiMaker account/submission steps outside this repo
