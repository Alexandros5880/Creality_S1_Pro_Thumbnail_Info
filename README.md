# Creality Ender-3 S1 Pro — Cura Thumbnail + Info (300×300)

A Cura Post-Processing script that embeds a **Creality-compatible JPEG thumbnail block**
and keeps **print info** visible on the Ender-3 S1 Pro screen (time / filament / layers).

✅ Tested with **Cura 5.11** and **Ender-3 S1 Pro**.

---

## Features
- 300×300 JPEG thumbnail (Creality JPG block)
- Works from SD card (no extra tools)
- Keeps common “info” lines compatible with Creality UI

---

## Installation (Windows / Cura 5.x)

1) Copy the script file into Cura scripts folder:

`%APPDATA%\cura\5.xx\scripts\`

Example for Cura 5.11:
`%APPDATA%\cura\5.11\scripts\`

2) Restart Cura

3) In Cura:
**Extensions → Post Processing → Modify G-Code → Add a script**
Select:
**S1 Pro: 300x300 Thumbnail (Creality JPG block)**

---

## Recommended settings
- Thumbnail size: **300**
- JPEG quality: **85**
- Line prefix: `;`
- Base64 line length: **76**
- “Creality tail numbers”: `1 197 500`

---

## Troubleshooting
- If the printer shows no preview, try renaming the gcode file (printer can cache previews).
- If Cura crashes on startup, remove the script from the `scripts` folder and restart Cura.

---

## Contributing
PRs are welcome. If you can test on other S1 firmware versions, open an issue with:
- Firmware version
- Cura version
- A sample gcode (small)

---

## License
MIT