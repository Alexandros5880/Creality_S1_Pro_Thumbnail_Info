import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.3

import UM 1.6 as UM
import Cura 1.6 as Cura

UM.Dialog {
    id: root

    title: "Creality S1 Pro Auto Thumbnail"
    width: 760 * screenScaleFactor
    height: 620 * screenScaleFactor
    minimumWidth: 620 * screenScaleFactor
    minimumHeight: 520 * screenScaleFactor
    backgroundColor: UM.Theme.getColor("main_background")

    property var backend
    property int cardRadius: Math.round(UM.Theme.getSize("default_radius").width / 2)
    property int sectionGap: UM.Theme.getSize("default_margin").height

    function safe(v, fallback) { return (v === undefined || v === null) ? fallback : v }
    function indexForLevelingMode(modeKey) {
        var mode = safe(modeKey, "use_saved_mesh")
        for (var i = 0; i < modeModel.length; i++) {
            if (modeModel[i].key === mode) {
                return i
            }
        }
        return 0
    }
    function syncLevelingModeFromBackend() {
        if (!backend || !mode) {
            return
        }
        var idx = indexForLevelingMode(backend.levelingMode)
        if (mode.currentIndex !== idx) {
            mode.currentIndex = idx
        }
    }
    function syncAllFromBackend() {
        if (!backend) {
            return
        }
        if (enableThumb.checked !== backend.enabled) enableThumb.checked = backend.enabled
        if (sizeSpin.value !== backend.size) sizeSpin.value = backend.size
        if (qualitySpin.value !== backend.jpegQuality) qualitySpin.value = backend.jpegQuality
        if (lineLengthSpin.value !== backend.lineLength) lineLengthSpin.value = backend.lineLength
        if (linePrefixField.text !== backend.linePrefix) linePrefixField.text = backend.linePrefix
        if (crealityTailField.text !== backend.crealityTail) crealityTailField.text = backend.crealityTail
        if (enableLeveling.checked !== backend.levelingEnabled) enableLeveling.checked = backend.levelingEnabled
        syncLevelingModeFromBackend()
    }
    property var modeModel: [
        { key: "use_saved_mesh", text: "Use saved mesh (M420 S1)" },
        { key: "probe_now", text: "Probe now (G29)" }
    ]

    headerComponent: Rectangle {
        width: parent.width
        height: 118 * screenScaleFactor
        color: UM.Theme.getColor("main_window_header_background")

        Rectangle {
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.margins: 18 * screenScaleFactor
            radius: 999
            color: enableThumb.checked ? UM.Theme.getColor("action_button") : UM.Theme.getColor("setting_control_disabled_border")
            width: statusLabel.implicitWidth + 18 * screenScaleFactor
            height: 30 * screenScaleFactor

            UM.Label {
                id: statusLabel
                anchors.centerIn: parent
                text: enableThumb.checked ? "Enabled" : "Disabled"
                color: UM.Theme.getColor(enableThumb.checked ? "text_default" : "button_text")
                font: UM.Theme.getFont("default_bold")
            }
        }

        Column {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.verticalCenter: parent.verticalCenter
            anchors.leftMargin: 22 * screenScaleFactor
            anchors.rightMargin: 120 * screenScaleFactor
            spacing: 6

            UM.Label {
                text: root.title
                font: UM.Theme.getFont("large_bold")
                color: UM.Theme.getColor("button_text")
            }

            UM.Label {
                width: parent.width
                text: "Injects a Creality-compatible JPG thumbnail into exported G-code and can optionally add bed leveling after the first G28."
                wrapMode: Text.WordWrap
                color: UM.Theme.getColor("button_text")
                opacity: 0.88
            }
        }
    }

    Item {
        anchors.fill: parent

        Flickable {
            id: scroll
            anchors.fill: parent
            anchors.margins: 18 * screenScaleFactor
            anchors.bottomMargin: footerRow.height + 24 * screenScaleFactor
            clip: true
            contentWidth: width
            contentHeight: content.implicitHeight
            ScrollBar.vertical: UM.ScrollBar {
                visible: scroll.contentHeight > scroll.height
            }

            Column {
                id: content
                width: scroll.width - (scroll.contentHeight > scroll.height ? 10 : 0)
                spacing: root.sectionGap

                Rectangle {
                    width: parent.width
                    radius: root.cardRadius
                    color: UM.Theme.getColor("background_2")
                    border.width: 1
                    border.color: UM.Theme.getColor("lining")
                    implicitHeight: enableSection.implicitHeight + 28 * screenScaleFactor

                    ColumnLayout {
                        id: enableSection
                        anchors.fill: parent
                        anchors.margins: 14 * screenScaleFactor
                        spacing: 10 * screenScaleFactor

                        RowLayout {
                            Layout.fillWidth: true

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 4

                                UM.Label {
                                    text: "Plugin status"
                                    font: UM.Theme.getFont("default_bold")
                                }

                                UM.Label {
                                    Layout.fillWidth: true
                                    text: "Turn automatic thumbnail injection on or off for file exports."
                                    wrapMode: Text.WordWrap
                                    opacity: 0.7
                                }
                            }

                            RowLayout {
                                spacing: 8 * screenScaleFactor

                                CheckBox {
                                    id: enableThumb
                                    text: ""
                                    checked: safe(backend ? backend.enabled : undefined, true)
                                    onToggled: if (backend) backend.enabled = checked
                                }

                                UM.Label {
                                    text: "Enabled"
                                    font: UM.Theme.getFont("default_bold")
                                    color: UM.Theme.getColor(enableThumb.enabled ? "text_default" : "text_disabled")
                                    verticalAlignment: Text.AlignVCenter
                                }
                            }
                        }
                    }
                }

                Rectangle {
                    width: parent.width
                    radius: root.cardRadius
                    color: UM.Theme.getColor("background_2")
                    border.width: 1
                    border.color: UM.Theme.getColor("lining")
                    enabled: enableThumb.checked
                    opacity: enabled ? 1.0 : 0.45
                    implicitHeight: thumbSection.implicitHeight + 32 * screenScaleFactor

                    ColumnLayout {
                        id: thumbSection
                        anchors.fill: parent
                        anchors.margins: 16 * screenScaleFactor
                        spacing: 12 * screenScaleFactor

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 4

                            UM.Label {
                                text: "Thumbnail output"
                                font: UM.Theme.getFont("default_bold")
                            }

                            UM.Label {
                                Layout.fillWidth: true
                                text: "Choose the rendered preview size, JPG compression and Base64 line wrapping."
                                wrapMode: Text.WordWrap
                                opacity: 0.7
                            }
                        }

                        GridLayout {
                            Layout.fillWidth: true
                            columns: 2
                            columnSpacing: 18 * screenScaleFactor
                            rowSpacing: 12 * screenScaleFactor

                            UM.Label {
                                text: "Size (px)"
                                Layout.alignment: Qt.AlignVCenter
                            }

                            SpinBox {
                                id: sizeSpin
                                Layout.fillWidth: true
                                from: 64
                                to: 512
                                stepSize: 1
                                editable: true
                                value: safe(backend ? backend.size : undefined, 300)
                                onValueChanged: if (backend && backend.size !== value) backend.size = value
                            }

                            UM.Label {
                                text: "JPEG quality"
                                Layout.alignment: Qt.AlignVCenter
                            }

                            SpinBox {
                                id: qualitySpin
                                Layout.fillWidth: true
                                from: 40
                                to: 95
                                stepSize: 1
                                editable: true
                                value: safe(backend ? backend.jpegQuality : undefined, 85)
                                onValueChanged: if (backend && backend.jpegQuality !== value) backend.jpegQuality = value
                            }

                            UM.Label {
                                text: "Base64 line length"
                                Layout.alignment: Qt.AlignVCenter
                            }

                            SpinBox {
                                id: lineLengthSpin
                                Layout.fillWidth: true
                                from: 40
                                to: 120
                                stepSize: 1
                                editable: true
                                value: safe(backend ? backend.lineLength : undefined, 76)
                                onValueChanged: if (backend && backend.lineLength !== value) backend.lineLength = value
                            }
                        }
                    }
                }

                Rectangle {
                    width: parent.width
                    radius: root.cardRadius
                    color: UM.Theme.getColor("background_2")
                    border.width: 1
                    border.color: UM.Theme.getColor("lining")
                    enabled: enableThumb.checked
                    opacity: enabled ? 1.0 : 0.45
                    implicitHeight: advancedSection.implicitHeight + 32 * screenScaleFactor

                    ColumnLayout {
                        id: advancedSection
                        anchors.fill: parent
                        anchors.margins: 16 * screenScaleFactor
                        spacing: 12 * screenScaleFactor

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 4

                            UM.Label {
                                text: "Firmware formatting"
                                font: UM.Theme.getFont("default_bold")
                            }

                            UM.Label {
                                Layout.fillWidth: true
                                text: "Control the exact formatting used for the encoded thumbnail block."
                                wrapMode: Text.WordWrap
                                opacity: 0.7
                            }
                        }

                        GridLayout {
                            Layout.fillWidth: true
                            columns: 2
                            columnSpacing: 18 * screenScaleFactor
                            rowSpacing: 12 * screenScaleFactor

                            UM.Label {
                                text: "Line prefix"
                                Layout.alignment: Qt.AlignVCenter
                            }

                            Cura.TextField {
                                id: linePrefixField
                                Layout.fillWidth: true
                                text: safe(backend ? backend.linePrefix : undefined, "; ")
                                placeholderText: "e.g. ; "
                                selectByMouse: true
                                onTextChanged: if (backend && backend.linePrefix !== text) backend.linePrefix = text
                            }

                            UM.Label {
                                text: "Creality tail numbers"
                                Layout.alignment: Qt.AlignVCenter
                            }

                            Cura.TextField {
                                id: crealityTailField
                                Layout.fillWidth: true
                                text: safe(backend ? backend.crealityTail : undefined, " 1 197 500")
                                placeholderText: "e.g. 1 197 500"
                                selectByMouse: true
                                onTextChanged: if (backend && backend.crealityTail !== text) backend.crealityTail = text
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            radius: root.cardRadius
                            color: UM.Theme.getColor("main_background")
                            border.width: 1
                            border.color: UM.Theme.getColor("lining")
                            implicitHeight: tipText.implicitHeight + 20 * screenScaleFactor

                            UM.Label {
                                id: tipText
                                anchors.fill: parent
                                anchors.margins: 10 * screenScaleFactor
                                text: "Tip: some Creality firmwares reject thumbnails unless the expected tail numbers are present."
                                wrapMode: Text.WordWrap
                                opacity: 0.72
                            }
                        }
                    }
                }

                Rectangle {
                    width: parent.width
                    radius: root.cardRadius
                    color: UM.Theme.getColor("background_2")
                    border.width: 1
                    border.color: UM.Theme.getColor("lining")
                    enabled: enableThumb.checked
                    opacity: enabled ? 1.0 : 0.45
                    implicitHeight: levelingSection.implicitHeight + 32 * screenScaleFactor

                    ColumnLayout {
                        id: levelingSection
                        anchors.fill: parent
                        anchors.margins: 16 * screenScaleFactor
                        spacing: 12 * screenScaleFactor

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 4

                            UM.Label {
                                text: "Bed leveling"
                                font: UM.Theme.getFont("default_bold")
                            }

                            UM.Label {
                                Layout.fillWidth: true
                                text: "Optionally insert one leveling command after the first homing move."
                                wrapMode: Text.WordWrap
                                opacity: 0.7
                            }
                        }

                        RowLayout {
                            spacing: 8 * screenScaleFactor

                            CheckBox {
                                id: enableLeveling
                                text: ""
                                checked: safe(backend ? backend.levelingEnabled : undefined, false)
                                onToggled: if (backend) backend.levelingEnabled = checked
                            }

                            UM.Label {
                                text: "Inject leveling after first G28"
                                font: UM.Theme.getFont("default_bold")
                                color: UM.Theme.getColor(enableLeveling.enabled ? "text_default" : "text_disabled")
                                verticalAlignment: Text.AlignVCenter
                            }
                        }

                        GridLayout {
                            Layout.fillWidth: true
                            columns: 2
                            columnSpacing: 18 * screenScaleFactor
                            rowSpacing: 12 * screenScaleFactor
                            enabled: enableLeveling.checked
                            opacity: enabled ? 1.0 : 0.45

                            UM.Label {
                                text: "Leveling mode"
                                Layout.alignment: Qt.AlignVCenter
                            }

                            Cura.ComboBox {
                                id: mode
                                Layout.fillWidth: true
                                textRole: "text"
                                model: modeModel
                                onCurrentIndexChanged: {
                                    if (backend && currentIndex >= 0 && model[currentIndex].key !== backend.levelingMode) {
                                        backend.levelingMode = model[currentIndex].key
                                    }
                                }
                            }
                        }

                        UM.Label {
                            Layout.fillWidth: true
                            text: "The plugin skips duplicate insertion if your start G-code already includes G29 or M420 S1."
                            wrapMode: Text.WordWrap
                            opacity: 0.7
                        }
                    }
                }
            }
        }

        Row {
            id: footerRow
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.margins: 18 * screenScaleFactor
            layoutDirection: Qt.RightToLeft
            spacing: 10 * screenScaleFactor

            Cura.PrimaryButton {
                text: "Reset defaults"
                onClicked: if (backend) backend.resetToDefaults()
            }

            Cura.PrimaryButton {
                text: "Save now"
                onClicked: if (backend) backend.saveNow()
            }

            Cura.PrimaryButton {
                text: "Close"
                onClicked: root.hide()
            }
        }

        Connections {
            target: backend
            ignoreUnknownSignals: true
            function onPreferencesChanged() {
                syncAllFromBackend()
            }
        }
    }

    onBackendChanged: syncAllFromBackend()
    onVisibleChanged: if (visible) syncAllFromBackend()
}
