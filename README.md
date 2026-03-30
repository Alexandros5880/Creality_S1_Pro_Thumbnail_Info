# Creality S1 Pro -- Thumbnail & Auto Tools for Ultimaker Cura

Enhance **Ultimaker Cura** with automatic Creality-compatible thumbnails
and optional printer commands for the **Creality Ender 3 S1 Pro**.

This repository contains:

-   Cura Extension (UI Plugin)
-   Cura Post-Processing Script (G-code modification)

------------------------------------------------------------------------

# PART 1 -- Install the Cura Extension (UI Plugin)

This makes the plugin appear in:

Extensions → Creality S1 Pro Auto Thumbnail

Step 1 -- Locate Cura plugins folder (Windows):

C:`\Users`\<YOUR_USERNAME\>`\AppData\Roaming\cura`\<CURA_VERSION\>`\plugins`\

Example:

C:`\Users\Alex\AppData\Roaming\cura`\\5.6`\plugins`\

Step 2 -- Copy this folder:

CuraPlugin/CrealityS1ProAutoThumbnail

Into:

.../cura/`<version>`/plugins/

Final structure must be:

plugins/CrealityS1ProAutoThumbnail

IMPORTANT: Do NOT create nested folders like:
plugins/CrealityS1ProAutoThumbnail/CrealityS1ProAutoThumbnail/

Step 3 -- Restart Cura completely.

------------------------------------------------------------------------

# PART 2 -- Install the Post-Processing Script

This enables the thumbnail injection in G-code.

It will appear in:

Extensions → Post Processing → Modify G-code

Step 1 -- Locate scripts folder (Windows):

C:`\Users`\<YOUR_USERNAME\>`\AppData\Roaming\cura`\<CURA_VERSION\>`\scripts`\

If the folder does not exist, create it.

Step 2 -- Copy:

CuraExtention/Creality_S1_Pro_Thumbnail_Info.py

Into:

.../cura/`<version>`/scripts/

Step 3 -- Restart Cura.

Then:

1.  Slice a model
2.  Go to Extensions → Post Processing → Modify G-code
3.  Click Add Script
4.  Select: S1 Pro: 300x300 Thumbnail (Creality JPG block)

------------------------------------------------------------------------

# What This Tool Does

-   Injects Creality-compatible JPG thumbnail block
-   Supports configurable thumbnail size
-   Optional Auto Bed Level command
-   Optional custom printer start commands
-   Compatible with Cura 5.x

------------------------------------------------------------------------

# Troubleshooting

If plugin does not appear:

-   Check folder nesting
-   Ensure plugin.json exists
-   Restart Cura
-   Check log file:

C:`\Users`\<USER\>`\AppData\Roaming\cura`\<version\>`\cura`.log

If script does not appear:

-   Ensure .py file is inside /scripts/
-   Restart Cura

------------------------------------------------------------------------

# License

MIT License
