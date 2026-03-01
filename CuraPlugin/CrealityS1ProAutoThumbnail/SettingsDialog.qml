import QtQuick 2.10
import QtQuick.Controls 2.3
import QtQuick.Layouts 1.3
import QtQuick.Window 2.2

Window {
    id: root
    title: "S1 Pro Auto Thumbnail"
    visible: false
    modality: Qt.ApplicationModal
    width: 560
    minimumWidth: 560
    minimumHeight: 560

    property var backend

    function safe(v, fallback) { return (v === undefined || v === null) ? fallback : v }

    Rectangle {
        anchors.fill: parent
        color: palette.window

        Column {
            anchors.fill: parent
            anchors.margins: 12
            spacing: 12

            Label {
                width: parent.width
                text: "Automatically injects a Creality-compatible JPG thumbnail into exported G-code."
                wrapMode: Text.WordWrap
                opacity: 0.85
            }

            ScrollView {
                width: parent.width
                height: parent.height - closeRow.height - 36
                clip: true

                Item {
                    width: Math.max(root.width - 48, 400)
                    implicitHeight: content.implicitHeight

                    ColumnLayout {
                        id: content
                        anchors.left: parent.left
                        anchors.right: parent.right
                        spacing: 14

                        Rectangle {
                            Layout.fillWidth: true
                            radius: 6
                            border.width: 1
                            border.color: "#3a3a3a"
                            color: "transparent"
                            implicitHeight: enableColumn.implicitHeight + 24

                            ColumnLayout {
                                id: enableColumn
                                anchors.fill: parent
                                anchors.margins: 12
                                spacing: 10

                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 10

                                    CheckBox {
                                        id: enableThumb
                                        text: "Enable auto thumbnail injection"
                                        checked: safe(backend ? backend.enabled : undefined, true)
                                        onToggled: if (backend) backend.enabled = checked
                                    }

                                    Item { Layout.fillWidth: true }

                                    Label {
                                        text: "v" + safe(backend ? backend.version : undefined, "1.0.0")
                                        opacity: 0.6
                                    }
                                }

                                Label {
                                    Layout.fillWidth: true
                                    text: "When enabled, the plugin updates the G-code right before saving to disk (Local file / Removable drive)."
                                    wrapMode: Text.WordWrap
                                    opacity: 0.75
                                }
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            radius: 6
                            border.width: 1
                            border.color: "#3a3a3a"
                            color: "transparent"
                            enabled: enableThumb.checked
                            opacity: enabled ? 1.0 : 0.5
                            implicitHeight: thumbColumn.implicitHeight + 24

                            ColumnLayout {
                                id: thumbColumn
                                anchors.fill: parent
                                anchors.margins: 12
                                spacing: 10

                                Label { text: "Thumbnail"; font.bold: true }

                                GridLayout {
                                    Layout.fillWidth: true
                                    columns: 2
                                    columnSpacing: 12
                                    rowSpacing: 10

                                    Label { text: "Size (px)"; opacity: 0.85 }
                                    SpinBox {
                                        from: 64; to: 512; stepSize: 1; editable: true
                                        value: safe(backend ? backend.size : undefined, 300)
                                        onValueModified: if (backend) backend.size = value
                                        Layout.fillWidth: true
                                    }

                                    Label { text: "JPEG quality"; opacity: 0.85 }
                                    SpinBox {
                                        from: 40; to: 95; stepSize: 1; editable: true
                                        value: safe(backend ? backend.jpegQuality : undefined, 85)
                                        onValueModified: if (backend) backend.jpegQuality = value
                                        Layout.fillWidth: true
                                    }

                                    Label { text: "Base64 line length"; opacity: 0.85 }
                                    SpinBox {
                                        from: 40; to: 120; stepSize: 1; editable: true
                                        value: safe(backend ? backend.lineLength : undefined, 76)
                                        onValueModified: if (backend) backend.lineLength = value
                                        Layout.fillWidth: true
                                    }
                                }
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            radius: 6
                            border.width: 1
                            border.color: "#3a3a3a"
                            color: "transparent"
                            enabled: enableThumb.checked
                            opacity: enabled ? 1.0 : 0.5
                            implicitHeight: advancedColumn.implicitHeight + 24

                            ColumnLayout {
                                id: advancedColumn
                                anchors.fill: parent
                                anchors.margins: 12
                                spacing: 10

                                Label { text: "Advanced"; font.bold: true }

                                GridLayout {
                                    Layout.fillWidth: true
                                    columns: 2
                                    columnSpacing: 12
                                    rowSpacing: 10

                                    Label { text: "Line prefix"; opacity: 0.85 }
                                    TextField {
                                        text: safe(backend ? backend.linePrefix : undefined, "; ")
                                        placeholderText: "e.g. ; "
                                        onEditingFinished: if (backend) backend.linePrefix = text
                                        Layout.fillWidth: true
                                    }

                                    Label { text: "Creality tail numbers"; opacity: 0.85 }
                                    TextField {
                                        text: safe(backend ? backend.crealityTail : undefined, " 1 197 500")
                                        placeholderText: "e.g. 1 197 500"
                                        onEditingFinished: if (backend) backend.crealityTail = text
                                        Layout.fillWidth: true
                                    }

                                    Label {
                                        Layout.columnSpan: 2
                                        text: "Tip: Tail numbers are required by some Creality firmwares for thumbnail compatibility."
                                        wrapMode: Text.WordWrap
                                        opacity: 0.65
                                    }
                                }
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            radius: 6
                            border.width: 1
                            border.color: "#3a3a3a"
                            color: "transparent"
                            enabled: enableThumb.checked
                            opacity: enabled ? 1.0 : 0.5
                            implicitHeight: levelingColumn.implicitHeight + 24

                            ColumnLayout {
                                id: levelingColumn
                                anchors.fill: parent
                                anchors.margins: 12
                                spacing: 10

                                Label { text: "Bed leveling (optional)"; font.bold: true }

                                CheckBox {
                                    id: enableLeveling
                                    text: "Inject leveling command after first G28"
                                    checked: safe(backend ? backend.levelingEnabled : undefined, false)
                                    onToggled: if (backend) backend.levelingEnabled = checked
                                }

                                RowLayout {
                                    Layout.fillWidth: true
                                    enabled: enableLeveling.checked
                                    opacity: enabled ? 1.0 : 0.5

                                    Label { text: "Mode"; opacity: 0.85 }
                                    ComboBox {
                                        id: mode
                                        Layout.fillWidth: true
                                        textRole: "text"
                                        model: [
                                            { key: "use_saved_mesh", text: "Use saved mesh (M420 S1)" },
                                            { key: "probe_now", text: "Probe now (G29)" }
                                        ]

                                        Component.onCompleted: {
                                            var v = safe(backend ? backend.levelingMode : undefined, "use_saved_mesh")
                                            for (var i = 0; i < model.length; i++) {
                                                if (model[i].key === v) {
                                                    currentIndex = i
                                                    break
                                                }
                                            }
                                        }

                                        onActivated: if (backend && currentIndex >= 0) backend.levelingMode = model[currentIndex].key
                                    }
                                }

                                Label {
                                    Layout.fillWidth: true
                                    text: "It will not add duplicates if your start G-code already contains G29 or M420 S1."
                                    wrapMode: Text.WordWrap
                                    opacity: 0.65
                                }
                            }
                        }
                    }
                }
            }

            Row {
                id: closeRow
                width: parent.width
                layoutDirection: Qt.RightToLeft

                Button {
                    text: "Close"
                    onClicked: root.hide()
                }
            }
        }
    }
}
