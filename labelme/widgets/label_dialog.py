import re
from typing import cast

from loguru import logger
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

import labelme.utils

# TODO(unknown):
# - Calculate optimal position so as not to go out of screen area.


class LabelQLineEdit(QtWidgets.QLineEdit):
    def setListWidget(self, list_widget):
        self.list_widget = list_widget

    def keyPressEvent(self, e):
        if e.key() in [QtCore.Qt.Key_Up, QtCore.Qt.Key_Down]:  # type: ignore[attr-defined]
            self.list_widget.keyPressEvent(e)
        else:
            super(LabelQLineEdit, self).keyPressEvent(e)


class LabelDialog(QtWidgets.QDialog):
    def __init__(
        self,
        text="Enter object label",
        parent=None,
        labels=None,
        sort_labels=True,
        show_text_field=True,
        completion="startswith",
        fit_to_content=None,
        flags=None,
    ):
        if fit_to_content is None:
            fit_to_content = {"row": False, "column": True}
        self._fit_to_content = fit_to_content

        # 设置固定的标签选项(TODO 这个地方没有用到配置文件的内容，待解决)
        if labels is None:
            labels = ["Text", "Connection", "Anchor", "Inflection"]
        self._labels = labels

        super(LabelDialog, self).__init__(parent)
        self.editList = QtWidgets.QComboBox()
        self.editList.setEditable(False)
        if self._fit_to_content["row"]:
            self.editList.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        if self._fit_to_content["column"]:
            self.editList.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        for label in labels:
            self.editList.addItem(label)
        self.editList.setFixedHeight(30)
        self.edit = LabelQLineEdit()

        if flags:
            self.editList.currentIndexChanged.connect(self.updateFlags)
        self.editList.currentIndexChanged.connect(self.labelSelected)
        # 新增两个输入框 分别输入中文和英文
        self.edit_cn = LabelQLineEdit()
        self.edit_cn.setPlaceholderText("Annotation chinese")
        self.edit_cn.setValidator(labelme.utils.labelValidator())
        self.edit_en = LabelQLineEdit()
        self.edit_en.setPlaceholderText("Annotation English")
        self.edit_en.setValidator(labelme.utils.labelValidator())

        self.edit_group_id = QtWidgets.QLineEdit()
        self.edit_group_id.setPlaceholderText("Group ID")
        self.edit_group_id.setValidator(
            QtGui.QRegExpValidator(QtCore.QRegExp(r"\d*"), None)
        )
        layout = QtWidgets.QVBoxLayout()
        if show_text_field:
            layout_edit = QtWidgets.QHBoxLayout()
            layout_edit.addWidget(self.editList, 6)
            layout_edit.addWidget(self.edit_cn, 6)
            layout_edit.addWidget(self.edit_en, 6)
            layout_edit.addWidget(self.edit_group_id, 2)
            layout.addLayout(layout_edit)
        # buttons
        self.buttonBox = bb = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal,  # type: ignore[attr-defined]
            self,
        )
        bb.button(bb.Ok).setIcon(labelme.utils.newIcon("done"))  # type: ignore[union-attr]
        bb.button(bb.Cancel).setIcon(labelme.utils.newIcon("undo"))  # type: ignore[union-attr]
        bb.accepted.connect(self.validate)
        bb.rejected.connect(self.reject)
        layout.addWidget(bb)
        # label_flags
        if flags is None:
            flags = {}
        self._flags = flags
        self.flagsLayout = QtWidgets.QVBoxLayout()
        self.resetFlags()
        layout.addItem(self.flagsLayout)
        # text edit
        # self.editDescription = QtWidgets.QTextEdit()
        # self.editDescription.setPlaceholderText("Label description")
        # self.editDescription.setFixedHeight(50)
        # layout.addWidget(self.editDescription)
        self.setLayout(layout)

    def addLabelHistory(self, label):
        if self.labelList.findItems(label, QtCore.Qt.MatchExactly):  # type: ignore[attr-defined]
            return
        self.labelList.addItem(label)
        if self._sort_labels:
            self.labelList.sortItems()

    def labelSelected(self, index):
        text = self.editList.itemText(index)
        self.edit.setText(text)

    def validate(self):
        if not self.edit.isEnabled():
            self.accept()
            return

        text = self.edit.text()
        if hasattr(text, "strip"):
            text = text.strip()
        else:
            text = text.trimmed()  # type: ignore[attr-defined]
        if text:
            self.accept()

    def labelDoubleClicked(self, item):
        self.validate()

    def postProcess(self):
        text = self.edit.text()
        if hasattr(text, "strip"):
            text = text.strip()
        else:
            text = text.trimmed()  # type: ignore[attr-defined]
        self.edit.setText(text)

    def updateFlags(self, label_new):
        # keep state of shared flags
        flags_old = self.getFlags()
        self.edit.setText(self.editList.currentText())

        flags_new = {}
        for pattern, keys in self._flags.items():
            if re.match(pattern, label_new):
                for key in keys:
                    flags_new[key] = flags_old.get(key, False)
        self.setFlags(flags_new)

    def deleteFlags(self):
        for i in reversed(range(self.flagsLayout.count())):
            item = self.flagsLayout.itemAt(i).widget()  # type: ignore[union-attr]
            self.flagsLayout.removeWidget(item)
            item.setParent(QtWidgets.QWidget())

    def resetFlags(self, label=""):
        flags = {}
        for pattern, keys in self._flags.items():
            if re.match(pattern, label):
                for key in keys:
                    flags[key] = False
        self.setFlags(flags)

    def setFlags(self, flags):
        self.deleteFlags()
        for key in flags:
            item = QtWidgets.QCheckBox(key, self)
            item.setChecked(flags[key])
            self.flagsLayout.addWidget(item)
            item.show()

    def getFlags(self):
        flags = {}
        for i in range(self.flagsLayout.count()):
            item = self.flagsLayout.itemAt(i).widget()  # type: ignore[union-attr]
            item = cast(QtWidgets.QCheckBox, item)
            flags[item.text()] = item.isChecked()  # type: ignore[union-attr]
        return flags

    def getGroupId(self):
        group_id = self.edit_group_id.text()
        if group_id:
            return int(group_id)
        return None


    def getAnnotation(self):
        annotation = self.edit_cn.text()
        if annotation:
            return annotation
        return None

    def getAnnotationEng(self):
        annotation_eng = self.edit_en.text()
        if annotation_eng:
            return annotation_eng
        return None


    def show_edited_text(self):
        print(self.edit.text())


    def popUp(
        self,
        text=None,
        annotation=None,
        annotation_eng=None,
        move=True,
        flags=None,
        group_id=None,
        description=None,
        flags_disabled: bool = False,
    ):
        # if text is None, the previous label in self.edit is kept
        if text is None:
            text = self.editList.currentText()
        #如果未传入annotation，则清空显示内容，否则显示传入的值进行显示
        if annotation is None:
            self.edit_cn.clear()
        else:
            self.edit_cn.setText(annotation)
        # 如果未传入annotation_eng，则清空显示内容，否则显示传入的值进行显示
        if annotation_eng is None:
            self.edit_en.clear()
        else:
            self.edit_en.setText(annotation_eng)
        if flags:
            self.setFlags(flags)
        else:
            self.resetFlags(text)
        if flags_disabled:
            for i in range(self.flagsLayout.count()):
                self.flagsLayout.itemAt(i).widget().setDisabled(True)
        self.edit.setText(text)
        self.edit.setSelection(0, len(text))
        if group_id is None:
            self.edit_group_id.clear()
        else:
            self.edit_group_id.setText(str(group_id))
        # items = self.labelList.findItems(text, QtCore.Qt.MatchFixedString)  # type: ignore[attr-defined]
        # if items:
        #     if len(items) != 1:
        #         logger.warning("Label list has duplicate '{}'".format(text))
        #     self.labelList.setCurrentItem(items[0])
        #     row = self.labelList.row(items[0])
        #     self.edit.completer().setCurrentRow(row)  # type: ignore[union-attr]
        # self.edit.setFocus(QtCore.Qt.PopupFocusReason)  # type: ignore[attr-defined]
        # index = self.labelList.findText(text, QtCore.Qt.MatchFixedString)  # type: ignore[attr-defined]
        # if index >= 0:
        #     self.labelList.setCurrentIndex(index)
        #     self.edit.completer().setCurrentRow(index)  # type: ignore[union-attr]
        # self.edit.setFocus(QtCore.Qt.PopupFocusReason)  # type: ignore[attr-defined]
        if move:
            self.move(QtGui.QCursor.pos())
        if self.exec_():
            return (
                self.edit.text(),
                self.getAnnotation(),
                self.getAnnotationEng(),
                self.getFlags(),
                self.getGroupId(),
                # self.editDescription.toPlainText(),
            )
        else:
            return None, None, None, None, None
