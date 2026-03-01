import os
from typing import Any

from UM.Logger import Logger

# Qt compatibility: Cura 5.11 uses PyQt6, but keep fallback.
try:
    from PyQt6.QtCore import QObject, QMetaObject, Qt, pyqtProperty, pyqtSignal
except Exception:
    from PyQt5.QtCore import QObject, QMetaObject, Qt, pyqtProperty, pyqtSignal

# Extension import compatibility
try:
    from UM.Extension.Extension import Extension
except Exception:
    from UM.Extension import Extension

try:
    from cura.CuraApplication import CuraApplication
except Exception:
    CuraApplication = None


class CrealityS1ProAutoThumbnailPlugin(QObject, Extension):
    """Cura Extension: shows Settings UI and stores settings in-memory.
    (G-code injection hook can be added on top of these settings.)
    """

    preferencesChanged = pyqtSignal()

    def __init__(self, parent: Any = None) -> None:
        QObject.__init__(self, parent)
        Extension.__init__(self)

        self._application = CuraApplication.getInstance() if CuraApplication else None
        self._settings_dialog = None

        # Default settings (in-memory)
        self._enabled = True
        self._size = 300
        self._jpeg_quality = 85
        self._line_length = 76
        self._line_prefix = "; "
        self._creality_tail = " 1 197 500"
        self._leveling_enabled = False
        self._leveling_mode = "use_saved_mesh"

        self.addMenuItem("Settings", self.showSettings)
        Logger.log("i", "CrealityS1ProAutoThumbnail: loaded")

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
        self.preferencesChanged.emit()

    @pyqtProperty(int, notify=preferencesChanged)
    def size(self) -> int:
        return self._size

    @size.setter
    def size(self, value: int) -> None:
        self._size = int(value)
        self.preferencesChanged.emit()

    @pyqtProperty(int, notify=preferencesChanged)
    def jpegQuality(self) -> int:
        return self._jpeg_quality

    @jpegQuality.setter
    def jpegQuality(self, value: int) -> None:
        self._jpeg_quality = int(value)
        self.preferencesChanged.emit()

    @pyqtProperty(int, notify=preferencesChanged)
    def lineLength(self) -> int:
        return self._line_length

    @lineLength.setter
    def lineLength(self, value: int) -> None:
        self._line_length = int(value)
        self.preferencesChanged.emit()

    @pyqtProperty(str, notify=preferencesChanged)
    def linePrefix(self) -> str:
        return self._line_prefix

    @linePrefix.setter
    def linePrefix(self, value: str) -> None:
        self._line_prefix = str(value)
        self.preferencesChanged.emit()

    @pyqtProperty(str, notify=preferencesChanged)
    def crealityTail(self) -> str:
        return self._creality_tail

    @pyqtProperty(str, notify=preferencesChanged)
    def version(self) -> str:
        return "1.0.0"


    @crealityTail.setter
    def crealityTail(self, value: str) -> None:
        self._creality_tail = str(value)
        self.preferencesChanged.emit()

    @pyqtProperty(bool, notify=preferencesChanged)
    def levelingEnabled(self) -> bool:
        return self._leveling_enabled

    @levelingEnabled.setter
    def levelingEnabled(self, value: bool) -> None:
        self._leveling_enabled = bool(value)
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
        self.preferencesChanged.emit()
