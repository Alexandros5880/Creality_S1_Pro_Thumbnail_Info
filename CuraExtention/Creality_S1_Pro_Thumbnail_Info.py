from ..Script import Script
from UM.Logger import Logger
import re

try:
    from cura.Snapshot import Snapshot
except Exception:
    Snapshot = None

try:
    from PyQt6.QtCore import QByteArray, QBuffer, QIODevice
except Exception:
    try:
        from PyQt5.QtCore import QByteArray, QBuffer, QIODevice
    except Exception:
        QByteArray = None
        QBuffer = None
        QIODevice = None


class Creality_S1_Pro_Thumbnail_Info(Script):

    def getSettingDataString(self):
        return """{
            "name": "S1 Pro: 300x300 Thumbnail (Creality JPG block)",
            "key": "Creality_S1_Pro_Thumbnail_Info",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "size":
                {
                    "label": "Thumbnail size",
                    "description": "Thumbnail width/height in pixels (square).",
                    "type": "int",
                    "default_value": 300,
                    "minimum_value": 32,
                    "maximum_value": 128
                },
                "jpeg_quality":
                {
                    "label": "JPEG quality",
                    "description": "JPEG compression quality (higher = larger file).",
                    "type": "int",
                    "default_value": 60,
                    "minimum_value": 40,
                    "maximum_value": 95
                },
                "creality_tail":
                {
                    "label": "Creality tail numbers",
                    "description": "Extra numbers appended to 'jpg begin' line for compatibility with some Creality firmwares.",
                    "type": "str",
                    "default_value": " 1 197 500"
                },
                "line_prefix":
                {
                    "label": "Line prefix",
                    "description": "Prefix for each base64 line (usually '; ').",
                    "type": "str",
                    "default_value": "; "
                },
                "line_len":
                {
                    "label": "Base64 line length",
                    "description": "Characters per base64 line.",
                    "type": "int",
                    "default_value": 76,
                    "minimum_value": 40,
                    "maximum_value": 120
                },

                "enable_leveling":
                {
                    "label": "Enable bed leveling",
                    "description": "Inject leveling commands into the Start G-code area.",
                    "type": "bool",
                    "default_value": false
                },
                "leveling_mode":
                {
                    "label": "Leveling mode",
                    "description": "Use saved mesh (M420 S1) or probe now (G29).",
                    "type": "enum",
                    "options": {
                        "use_saved_mesh": "Use saved mesh (M420 S1)",
                        "probe_now": "Probe now (G29)"
                    },
                    "default_value": "use_saved_mesh",
                    "enabled": "enable_leveling"
                }
            }
        }"""

    def execute(self, data):
        try:
            if Snapshot is None:
                Logger.log("w", "S1Pro thumbnail: Snapshot API not available.")
                return data

            if QByteArray is None or QBuffer is None or QIODevice is None:
                Logger.log("w", "S1Pro thumbnail: Qt buffer API not available.")
                return data

            size = int(self.getSettingValueByKey("size"))
            quality = int(self.getSettingValueByKey("jpeg_quality"))
            tail = self.getSettingValueByKey("creality_tail") or ""
            line_prefix = self.getSettingValueByKey("line_prefix") or "; "
            line_len = int(self.getSettingValueByKey("line_len"))

            enable_leveling = bool(self.getSettingValueByKey("enable_leveling"))
            leveling_mode = self.getSettingValueByKey("leveling_mode") or "use_saved_mesh"

            gcode = "\n".join(data)

            # 1) Inject leveling into the start gcode (only if enabled)
            if enable_leveling:
                gcode = self._inject_leveling(gcode, leveling_mode)

            # 2) Avoid duplicate thumbnail blocks
            if re.search(r"(?im)^\s*;\s*jpg\s+begin\s+\d+\*\d+\s+\d+", gcode):
                Logger.log("i", "S1Pro thumbnail: jpg block already exists, skipping.")
                return [gcode]

            # 3) Render snapshot
            img = None
            try:
                img = Snapshot.snapshot(size, size)
            except Exception:
                try:
                    img = Snapshot().snapshot(size, size)
                except Exception as ex:
                    Logger.log("w", f"S1Pro thumbnail: Snapshot failed: {ex}")
                    return [gcode]

            if img is None:
                Logger.log("w", "S1Pro thumbnail: Snapshot returned None.")
                return [gcode]

            # 4) QImage -> JPEG bytes
            ba = QByteArray()
            buff = QBuffer(ba)
            buff.open(QIODevice.OpenModeFlag.WriteOnly)
            ok = img.save(buff, "JPG", quality)
            buff.close()

            if not ok or ba.size() <= 0:
                Logger.log("w", "S1Pro thumbnail: Failed to encode JPG.")
                return [gcode]

            jpg_bytes = bytes(ba)
            byte_count = len(jpg_bytes)
            
            # if byte_count > 20000:
            #     Logger.log("w", f"S1Pro thumbnail: Thumbnail too large ({byte_count} bytes), skipping.")
            #     return [gcode]

            import base64, textwrap
            b64 = base64.b64encode(jpg_bytes).decode("ascii")
            b64_lines = textwrap.wrap(b64, line_len)
            b64_block = "\n".join([f"{line_prefix}{ln}" for ln in b64_lines])

            header = f"; jpg begin {size}*{size} {byte_count}{tail}".rstrip()
            footer = "; jpg end"
            block = "\n".join([header, b64_block, footer])

            # 5) Insert before ;FLAVOR if present (Creality style)
            m = re.search(r"(?im)^\s*;FLAVOR:", gcode)
            if m:
                insert_at = m.start()
                gcode2 = gcode[:insert_at] + block + "\n" + gcode[insert_at:]
            else:
                gcode2 = block + "\n" + gcode

            return [gcode2]

        except Exception as ex:
            Logger.logException("e", f"S1Pro thumbnail script failed: {ex}")
            return data

    def _inject_leveling(self, gcode: str, leveling_mode: str) -> str:
        # If user already has G29/M420 in start gcode, don't spam duplicates
        if re.search(r"(?im)^\s*G29\b", gcode) or re.search(r"(?im)^\s*M420\s+S1\b", gcode):
            Logger.log("i", "S1Pro leveling: leveling command already present, skipping inject.")
            return gcode

        # Insert right after the first G28 (home), which is the safest place.
        # If no G28 exists, do nothing (we won't guess).
        m = re.search(r"(?im)^\s*G28\b.*$", gcode)
        if not m:
            Logger.log("w", "S1Pro leveling: No G28 found. Not injecting leveling.")
            return gcode

        insert_pos = m.end()

        if leveling_mode == "probe_now":
            leveling_lines = "\nG29 ; Auto Bed Leveling (probe mesh now)\n"
        else:
            leveling_lines = "\nM420 S1 ; Enable saved mesh leveling\n"

        gcode2 = gcode[:insert_pos] + leveling_lines + gcode[insert_pos:]
        Logger.log("i", f"S1Pro leveling: injected mode={leveling_mode}")
        return gcode2