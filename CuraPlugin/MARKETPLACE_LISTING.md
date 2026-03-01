# Marketplace Listing Draft

This file contains ready-to-use listing text for publishing the plugin package.

## Plugin Name

Creality S1 Pro Auto Thumbnail

## Short Description

Automatically injects a Creality-compatible JPG thumbnail block into exported G-code files in UltiMaker Cura.

## Full Description

Creality S1 Pro Auto Thumbnail is an auto-run Cura extension for Creality-style preview thumbnails.

It processes G-code automatically when you use:

- Save to Disk
- Save to Removable Drive

The plugin inserts a Creality-compatible JPG thumbnail block near the top of the exported `.gcode` file, so compatible Creality printer screens can show a preview image.

It also includes optional bed leveling command injection after `G28`:

- `M420 S1` to enable a saved mesh
- `G29` to probe a fresh mesh

The plugin includes a settings window inside Cura where you can configure:

- Enable or disable automatic processing
- Thumbnail size
- JPEG quality
- Base64 line length
- Line prefix
- Creality tail values
- Bed leveling mode

## Key Features

- Automatic processing during G-code export
- Creality JPG thumbnail block generation
- Save to Disk support
- Save to Removable Drive support
- Optional leveling command injection
- Cura-integrated settings dialog

## Compatibility

- Tested target: UltiMaker Cura 5.11
- Intended use: Creality-compatible G-code workflows

## Tags

- Cura
- Creality
- Thumbnail
- G-code
- Ender-3 S1 Pro
- Preview

## Support Text

If the printer does not update the preview, rename the exported G-code file and try again because some printer firmwares cache previews.

If Cura fails to load the plugin, remove the plugin folder from the Cura plugins directory and restart Cura.
