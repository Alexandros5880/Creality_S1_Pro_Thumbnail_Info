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


class S1Pro_Thumbnail_300_Info(Script):

    def getSettingDataString(self):
        return """{
            "name": "S1 Pro: 300x300 Thumbnail (Creality JPG block)",
            "key": "S1Pro_Thumbnail_300_Info",
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
                    "minimum_value": 64,
                    "maximum_value": 512
                },
                "jpeg_quality":
                {
                    "label": "JPEG quality",
                    "description": "JPEG compression quality (higher = larger file).",
                    "type": "int",
                    "default_value": 85,
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

            gcode = "\n".join(data)

            # Avoid duplicates
            if re.search(r"(?im)^\s*;\s*jpg\s+begin\s+\d+\*\d+\s+\d+", gcode):
                Logger.log("i", "S1Pro thumbnail: jpg block already exists, skipping.")
                return data

            # Render snapshot
            img = None
            try:
                img = Snapshot.snapshot(size, size)
            except Exception:
                try:
                    img = Snapshot().snapshot(size, size)
                except Exception as ex:
                    Logger.log("w", f"S1Pro thumbnail: Snapshot failed: {ex}")
                    return data

            if img is None:
                Logger.log("w", "S1Pro thumbnail: Snapshot returned None.")
                return data

            # QImage -> JPEG bytes
            ba = QByteArray()
            buff = QBuffer(ba)
            buff.open(QIODevice.OpenModeFlag.WriteOnly)
            ok = img.save(buff, "JPG", quality)
            buff.close()

            if not ok or ba.size() <= 0:
                Logger.log("w", "S1Pro thumbnail: Failed to encode JPG.")
                return data

            jpg_bytes = bytes(ba)
            byte_count = len(jpg_bytes)

            import base64, textwrap
            b64 = base64.b64encode(jpg_bytes).decode("ascii")
            b64_lines = textwrap.wrap(b64, line_len)
            b64_block = "\n".join([f"{line_prefix}{ln}" for ln in b64_lines])

            header = f"; jpg begin {size}*{size} {byte_count}{tail}".rstrip()
            footer = "; jpg end"
            block = "\n".join([header, b64_block, footer])

            # Insert before ;FLAVOR if present (Creality style)
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