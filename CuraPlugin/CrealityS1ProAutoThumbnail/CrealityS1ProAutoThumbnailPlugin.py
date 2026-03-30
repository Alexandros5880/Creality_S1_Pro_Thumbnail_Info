import os
import re
import base64
import textwrap
import json
from typing import Any

from UM.Logger import Logger
from UM.Application import Application

# Qt compatibility: Cura 5.11 uses PyQt6, but keep fallback.
try:
    from PyQt6.QtCore import QObject, QMetaObject, Qt, QByteArray, QBuffer, QIODevice, pyqtProperty, pyqtSignal, pyqtSlot
except Exception:
    from PyQt5.QtCore import QObject, QMetaObject, Qt, QByteArray, QBuffer, QIODevice, pyqtProperty, pyqtSignal, pyqtSlot

# Extension import compatibility
try:
    from UM.Extension.Extension import Extension
except Exception:
    from UM.Extension import Extension

try:
    from cura.CuraApplication import CuraApplication
except Exception:
    CuraApplication = None

try:
    from cura.Snapshot import Snapshot
except Exception:
    Snapshot = None


class CrealityS1ProAutoThumbnailPlugin(QObject, Extension):
    """Cura Extension: shows Settings UI and stores settings in-memory.
    (G-code injection hook can be added on top of these settings.)
    """

    preferencesChanged = pyqtSignal()
    _plugin_version = "1.1.0"
    _pref_prefix = "creality_s1_pro_auto_thumbnail/"
    _thumbnail_start_marker = ";CREALITY_S1_PRO_AUTO_THUMBNAIL_BLOCK_START"
    _thumbnail_end_marker = ";CREALITY_S1_PRO_AUTO_THUMBNAIL_BLOCK_END"
    _leveling_marker = "[CrealityS1ProAutoThumbnail]"
    _default_enabled = True
    _default_size = 64
    _default_jpeg_quality = 60
    _default_line_length = 76
    _default_line_prefix = "; "
    _default_creality_tail = " 1 197 500"
    _default_leveling_enabled = False
    _default_leveling_mode = "use_saved_mesh"
    _thumbnail_start_marker = ";CREALITY_S1_PRO_AUTO_THUMBNAIL_BLOCK_START"
    _thumbnail_end_marker = ";CREALITY_S1_PRO_AUTO_THUMBNAIL_BLOCK_END"

    def __init__(self, parent: Any = None) -> None:
        QObject.__init__(self, parent)
        Extension.__init__(self)

        self._application = CuraApplication.getInstance() if CuraApplication else None
        self._settings_dialog = None

        self._enabled = self._default_enabled
        self._size = self._default_size
        self._jpeg_quality = self._default_jpeg_quality
        self._line_length = self._default_line_length
        self._line_prefix = self._default_line_prefix
        self._creality_tail = self._default_creality_tail
        self._leveling_enabled = self._default_leveling_enabled
        self._leveling_mode = self._default_leveling_mode
        self._plugin_version = self._loadPluginVersion()

        self._loadPreferences()

        if self._application is not None:
            self._application.getOutputDeviceManager().writeStarted.connect(self._onWriteStarted)

        self.addMenuItem("Settings", self.showSettings)
        Logger.log("i", "CrealityS1ProAutoThumbnail: loaded")

    def _loadPluginVersion(self) -> str:
        plugin_json_path = os.path.join(os.path.dirname(__file__), "plugin.json")
        try:
            with open(plugin_json_path, "r", encoding="utf-8") as plugin_file:
                plugin_data = json.load(plugin_file)
            version = str(plugin_data.get("version") or "").strip()
            if version:
                return version
        except Exception as ex:
            Logger.logException("w", f"CrealityS1ProAutoThumbnail: Failed to read plugin version: {ex}")
        return self._plugin_version

    def _prefKey(self, name: str) -> str:
        return self._pref_prefix + name

    def _loadPreferences(self) -> None:
        if self._application is None:
            return

        prefs = self._application.getPreferences()
        prefs.addPreference(self._prefKey("enabled"), self._default_enabled)
        prefs.addPreference(self._prefKey("size"), self._default_size)
        prefs.addPreference(self._prefKey("jpeg_quality"), self._default_jpeg_quality)
        prefs.addPreference(self._prefKey("line_length"), self._default_line_length)
        prefs.addPreference(self._prefKey("line_prefix"), self._default_line_prefix)
        prefs.addPreference(self._prefKey("creality_tail"), self._default_creality_tail)
        prefs.addPreference(self._prefKey("leveling_enabled"), self._default_leveling_enabled)
        prefs.addPreference(self._prefKey("leveling_mode"), self._default_leveling_mode)

        self._enabled = self._asBool(prefs.getValue(self._prefKey("enabled")))
        self._size = int(prefs.getValue(self._prefKey("size")))
        self._jpeg_quality = int(prefs.getValue(self._prefKey("jpeg_quality")))
        self._line_length = int(prefs.getValue(self._prefKey("line_length")))
        self._line_prefix = str(prefs.getValue(self._prefKey("line_prefix")))
        self._creality_tail = str(prefs.getValue(self._prefKey("creality_tail")))
        self._leveling_enabled = self._asBool(prefs.getValue(self._prefKey("leveling_enabled")))
        self._leveling_mode = str(prefs.getValue(self._prefKey("leveling_mode")) or "use_saved_mesh")
        if self._leveling_mode not in ("use_saved_mesh", "probe_now"):
            self._leveling_mode = self._default_leveling_mode

    def _saveAllPreferences(self) -> None:
        self._savePreference("enabled", self._enabled)
        self._savePreference("size", self._size)
        self._savePreference("jpeg_quality", self._jpeg_quality)
        self._savePreference("line_length", self._line_length)
        self._savePreference("line_prefix", self._line_prefix)
        self._savePreference("creality_tail", self._creality_tail)
        self._savePreference("leveling_enabled", self._leveling_enabled)
        self._savePreference("leveling_mode", self._leveling_mode)

    def _savePreference(self, name: str, value: Any) -> None:
        if self._application is None:
            return
        self._application.getPreferences().setValue(self._prefKey(name), value)

    def _asBool(self, value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in ("1", "true", "yes", "on")
        return bool(value)

    def _onWriteStarted(self, output_device: Any) -> None:
        scene = Application.getInstance().getController().getScene()
        if not hasattr(scene, "gcode_dict"):
            Logger.log("w", "CrealityS1ProAutoThumbnail: Scene has no gcode_dict.")
            return

        gcode_dict = getattr(scene, "gcode_dict")
        if not gcode_dict:
            return

        active_build_plate_id = self._application.getMultiBuildPlateModel().activeBuildPlate
        gcode_list = gcode_dict.get(active_build_plate_id)
        if not gcode_list:
            return

        try:
            transformed_gcode = self._transformGcode("\n".join(gcode_list))
        except Exception as ex:
            Logger.logException("e", f"CrealityS1ProAutoThumbnail: Failed to transform gcode: {ex}")
            return

        gcode_dict[active_build_plate_id] = [transformed_gcode]
        setattr(scene, "gcode_dict", gcode_dict)

    def _transformGcode(self, gcode: str) -> str:
        gcode = self._removeManagedThumbnailBlock(gcode)
        gcode = self._removeManagedLeveling(gcode)

        if not self._enabled:
            return gcode

        if self._leveling_enabled:
            gcode = self._injectLeveling(gcode)

        if re.search(r"(?im)^\s*;\s*jpg\s+begin\s+\d+\*\d+\s+\d+", gcode):
            Logger.log("i", "CrealityS1ProAutoThumbnail: Existing JPG thumbnail block detected, not replacing it.")
            return gcode

        thumbnail_block = self._buildThumbnailBlock()
        if not thumbnail_block:
            return gcode

        flavor_match = re.search(r"(?im)^\s*;FLAVOR:", gcode)
        if flavor_match:
            return gcode[:flavor_match.start()] + thumbnail_block + "\n" + gcode[flavor_match.start():]
        return thumbnail_block + "\n" + gcode

    def _removeManagedThumbnailBlock(self, gcode: str) -> str:
        legacy_pattern = (
            re.escape(self._thumbnail_start_marker)
            + r".*?"
            + r";\s*jpg\s+end"
            + r"(?:\n[ \t]*)?"
        )
        gcode = re.sub(legacy_pattern, "", gcode, flags=re.DOTALL)

        unmarked_pattern = r"(?is)\A\s*;\s*jpg\s+begin\s+\d+\*\d+\s+\d+[^\n]*\n.*?\n;\s*jpg\s+end(?:\n[ \t]*)?"
        return re.sub(unmarked_pattern, "", gcode, count=1)

    def _removeManagedLeveling(self, gcode: str) -> str:
        pattern = rf"(?im)^\s*(?:G29|M420\s+S1)\b.*{re.escape(self._leveling_marker)}.*\n?"
        return re.sub(pattern, "", gcode)

    def _injectLeveling(self, gcode: str) -> str:
        # Restrict duplicate detection and insertion point to start G-code only.
        # Some profiles/macros can contain G29/M420 later in the file, which should
        # not prevent start-leveling injection.
        layer0_markers = list(re.finditer(r"(?im)^\s*;\s*LAYER:0\b.*$", gcode))
        start_end = layer0_markers[0].start() if layer0_markers else len(gcode)
        start_gcode = gcode[:start_end]

        if re.search(r"(?im)^\s*G29\b", start_gcode) or re.search(r"(?im)^\s*M420\s+S1\b", start_gcode):
            return gcode

        g28_matches = list(re.finditer(r"(?im)^\s*G28\b.*$", start_gcode))
        if not g28_matches:
            Logger.log("w", "CrealityS1ProAutoThumbnail: No G28 found, skipping leveling injection.")
            return gcode
        match = g28_matches[-1]

        if self._leveling_mode == "probe_now":
            leveling_line = f"\nG29 ; Auto Bed Leveling (probe mesh now) {self._leveling_marker}\n"
        else:
            leveling_line = f"\nM420 S1 ; Enable saved mesh leveling {self._leveling_marker}\n"

        return gcode[:match.end()] + leveling_line + gcode[match.end():]

    def _buildThumbnailBlock(self) -> str:
        if Snapshot is None:
            Logger.log("w", "CrealityS1ProAutoThumbnail: Snapshot API not available.")
            return ""
        if byte_count > 20000:
            Logger.log("w", f"CrealityS1ProAutoThumbnail: Thumbnail too large ({byte_count} bytes), skipping.")
            return ""

        image = None
        try:
            image = Snapshot.snapshot(self._size, self._size)
        except Exception:
            try:
                image = Snapshot().snapshot(self._size, self._size)
            except Exception as ex:
                Logger.logException("w", f"CrealityS1ProAutoThumbnail: Snapshot failed: {ex}")
                return ""

        if image is None:
            Logger.log("w", "CrealityS1ProAutoThumbnail: Snapshot returned None.")
            return ""

        image_bytes = QByteArray()
        buffer = QBuffer(image_bytes)
        buffer.open(QIODevice.OpenModeFlag.WriteOnly if hasattr(QIODevice, "OpenModeFlag") else QIODevice.WriteOnly)
        save_ok = image.save(buffer, "JPG", self._jpeg_quality)
        buffer.close()

        if not save_ok or image_bytes.size() <= 0:
            Logger.log("w", "CrealityS1ProAutoThumbnail: Failed to encode JPG snapshot.")
            return ""

        raw_bytes = bytes(image_bytes)
        byte_count = len(raw_bytes)
        encoded = base64.b64encode(raw_bytes).decode("ascii")
        encoded_lines = textwrap.wrap(encoded, self._line_length)
        payload = "\n".join(f"{self._line_prefix}{line}" for line in encoded_lines)

        header = f"; jpg begin {self._size}*{self._size} {byte_count}{self._creality_tail}".rstrip()
        footer = "; jpg end"

        return "\n".join(
            [
                self._thumbnail_start_marker,
                header,
                payload,
                footer,
                self._thumbnail_end_marker,
                "",
            ]
        )

    # ---------------- QML Loader ----------------

    def _createSettingsDialog(self) -> None:
        if self._application is None:
            Logger.log("e", "CrealityS1ProAutoThumbnail: CuraApplication not available.")
            return

        base_dir = os.path.dirname(__file__)
        qml_path = os.path.join(base_dir, "SettingsDialog.qml")

        if not os.path.exists(qml_path):
            Logger.log("e", f"CrealityS1ProAutoThumbnail: SettingsDialog.qml not found at: {qml_path}")
            return

        # IMPORTANT: QML expects `property var backend`
        self._settings_dialog = self._application.createQmlComponent(qml_path, {"backend": self})

    def showSettings(self) -> None:
        if self._settings_dialog is None:
            self._createSettingsDialog()

        if self._settings_dialog is None:
            Logger.log("e", "CrealityS1ProAutoThumbnail: Failed to create Settings dialog (None). Check cura.log for QML errors.")
            return

        try:
            self._settings_dialog.setProperty("backend", self)
            self._settings_dialog.setProperty("focus", True)
            QMetaObject.invokeMethod(
                self._settings_dialog,
                "show",
                Qt.ConnectionType.DirectConnection if hasattr(Qt, "ConnectionType") else Qt.DirectConnection,
            )
        except Exception as ex:
            Logger.logException("w", f"CrealityS1ProAutoThumbnail: show() failed, falling back to open()/visible=true: {ex}")
            try:
                QMetaObject.invokeMethod(
                    self._settings_dialog,
                    "open",
                    Qt.ConnectionType.DirectConnection if hasattr(Qt, "ConnectionType") else Qt.DirectConnection,
                )
            except Exception:
                try:
                    self._settings_dialog.setProperty("visible", True)
                except Exception as fallback_ex:
                    Logger.logException("e", f"CrealityS1ProAutoThumbnail: Failed to show settings dialog: {fallback_ex}")

    # ---------------- Properties exposed to QML ----------------

    @pyqtProperty(bool, notify=preferencesChanged)
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = bool(value)
        self._savePreference("enabled", self._enabled)
        self.preferencesChanged.emit()

    @pyqtProperty(int, notify=preferencesChanged)
    def size(self) -> int:
        return self._size

    @size.setter
    def size(self, value: int) -> None:
        self._size = int(value)
        self._savePreference("size", self._size)
        self.preferencesChanged.emit()

    @pyqtProperty(int, notify=preferencesChanged)
    def jpegQuality(self) -> int:
        return self._jpeg_quality

    @jpegQuality.setter
    def jpegQuality(self, value: int) -> None:
        self._jpeg_quality = int(value)
        self._savePreference("jpeg_quality", self._jpeg_quality)
        self.preferencesChanged.emit()

    @pyqtProperty(int, notify=preferencesChanged)
    def lineLength(self) -> int:
        return self._line_length

    @lineLength.setter
    def lineLength(self, value: int) -> None:
        self._line_length = int(value)
        self._savePreference("line_length", self._line_length)
        self.preferencesChanged.emit()

    @pyqtProperty(str, notify=preferencesChanged)
    def linePrefix(self) -> str:
        return self._line_prefix

    @linePrefix.setter
    def linePrefix(self, value: str) -> None:
        self._line_prefix = str(value)
        self._savePreference("line_prefix", self._line_prefix)
        self.preferencesChanged.emit()

    @pyqtProperty(str, notify=preferencesChanged)
    def crealityTail(self) -> str:
        return self._creality_tail

    @pyqtProperty(str, notify=preferencesChanged)
    def version(self) -> str:
        return self._plugin_version

    @pyqtSlot()
    def saveNow(self) -> None:
        self._saveAllPreferences()
        self.preferencesChanged.emit()
        Logger.log("i", "CrealityS1ProAutoThumbnail: preferences saved.")

    @pyqtSlot()
    def resetToDefaults(self) -> None:
        self._enabled = self._default_enabled
        self._size = self._default_size
        self._jpeg_quality = self._default_jpeg_quality
        self._line_length = self._default_line_length
        self._line_prefix = self._default_line_prefix
        self._creality_tail = self._default_creality_tail
        self._leveling_enabled = self._default_leveling_enabled
        self._leveling_mode = self._default_leveling_mode
        self._saveAllPreferences()
        self.preferencesChanged.emit()
        Logger.log("i", "CrealityS1ProAutoThumbnail: preferences reset to defaults.")


    @crealityTail.setter
    def crealityTail(self, value: str) -> None:
        self._creality_tail = str(value)
        self._savePreference("creality_tail", self._creality_tail)
        self.preferencesChanged.emit()

    @pyqtProperty(bool, notify=preferencesChanged)
    def levelingEnabled(self) -> bool:
        return self._leveling_enabled

    @levelingEnabled.setter
    def levelingEnabled(self, value: bool) -> None:
        self._leveling_enabled = bool(value)
        self._savePreference("leveling_enabled", self._leveling_enabled)
        self.preferencesChanged.emit()

    @pyqtProperty(str, notify=preferencesChanged)
    def levelingMode(self) -> str:
        return self._leveling_mode

    @levelingMode.setter
    def levelingMode(self, value: str) -> None:
        v = str(value)
        if v not in ("use_saved_mesh", "probe_now"):
            v = "use_saved_mesh"
        self._leveling_mode = v
        self._savePreference("leveling_mode", self._leveling_mode)
        self.preferencesChanged.emit()
