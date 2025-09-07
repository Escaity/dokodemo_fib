from PySide6.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QColorDialog, QDialogButtonBox,
    QCheckBox, QDoubleSpinBox, QScrollArea, QFormLayout
)
from PySide6.QtGui import QPainter, QColor, QPen, QValidator
from PySide6.QtCore import Qt, QPoint, Signal
from config import Config


class AlphaNumericValidator(QValidator):
    def validate(self, input_str, pos):
        if len(input_str) > 1 or (len(input_str) == 1 and not input_str.isalnum()):
            return QValidator.State.Invalid, input_str, pos
        return QValidator.State.Acceptable, input_str, pos


class LevelSettingRow(QWidget):
    delete_requested = Signal(QWidget)

    def __init__(self, level_data, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.enabled_check = QCheckBox()
        self.enabled_check.setChecked(level_data.get("enabled", True))
        self.layout.addWidget(self.enabled_check)
        self.level_spinbox = QDoubleSpinBox()
        self.level_spinbox.setDecimals(4)
        self.level_spinbox.setSingleStep(0.001)
        self.level_spinbox.setRange(-100, 100)
        self.level_spinbox.setValue(level_data.get("level", 0.0))
        self.layout.addWidget(self.level_spinbox)
        self.color_button = QPushButton("■")
        self.color = QColor(level_data.get("color", Config.DEFAULT_NEW_LEVEL_COLOR))
        self.update_color_button()
        self.color_button.clicked.connect(self.choose_color)
        self.layout.addWidget(self.color_button)
        delete_button = QPushButton(Config.DIALOG_DELETE_BTN)
        delete_button.clicked.connect(lambda: self.delete_requested.emit(self))
        self.layout.addWidget(delete_button)

    def choose_color(self):
        new_color = QColorDialog.getColor(self.color, self, Config.DIALOG_COLOR_PICKER_TITLE)
        if new_color.isValid():
            self.color = new_color
            self.update_color_button()

    def update_color_button(self):
        self.color_button.setStyleSheet(f"background-color: {self.color.name()}; color: white;")

    def get_data(self):
        return {"enabled": self.enabled_check.isChecked(), "level": self.level_spinbox.value(),
                "color": self.color.name()}


class SettingsDialog(QDialog):
    def __init__(self, current_hotkey, current_levels, parent=None):
        super().__init__(parent)
        self.setWindowTitle(Config.DIALOG_TITLE)
        self.setMinimumWidth(350)
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        self.hotkey_edit = QLineEdit(current_hotkey)
        self.hotkey_edit.setMaxLength(1)
        self.hotkey_edit.setValidator(AlphaNumericValidator())
        form_layout.addRow(Config.DIALOG_DRAW_KEY_LABEL, self.hotkey_edit)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(QLabel("-" * 40))
        main_layout.addWidget(QLabel(Config.DIALOG_LEVELS_LABEL))
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)
        container = QWidget()
        self.levels_layout = QVBoxLayout(container)
        scroll_area.setWidget(container)
        for level_data in current_levels:
            self.add_level_row(level_data)
        add_button = QPushButton(Config.DIALOG_ADD_LEVEL)
        add_button.clicked.connect(lambda: self.add_level_row())
        main_layout.addWidget(add_button)
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

    def add_level_row(self, level_data=None):
        if level_data is None:
            level_data = {"enabled": True, "level": 0.0, "color": Config.DEFAULT_NEW_LEVEL_COLOR}
        row = LevelSettingRow(level_data)
        row.delete_requested.connect(self.remove_level_row)
        self.levels_layout.addWidget(row)
        return row

    def remove_level_row(self, row_widget):
        row_widget.deleteLater()

    def get_settings(self):
        levels_data = []
        for i in range(self.levels_layout.count()):
            row_widget = self.levels_layout.itemAt(i).widget()
            if row_widget:
                levels_data.append(row_widget.get_data())
        hotkey = self.hotkey_edit.text().lower()
        if not hotkey:
            hotkey = Config.DEFAULT_DRAW_KEY
        return hotkey, levels_data


class OverlayWidget(QWidget):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller

    def paintEvent(self, event):
        start_point = self.controller.get_start_point()
        if start_point.isNull(): return
        end_point = self.controller.get_end_point()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        start_x, end_x = start_point.x(), end_point.x()
        diff_y = end_point.y() - start_point.y()
        for level_data in self.controller.settings.get("levels", []):
            if level_data.get("enabled", False):
                pen = QPen(QColor(level_data["color"]), Config.PEN_WIDTH, Qt.PenStyle.SolidLine)
                painter.setPen(pen)
                level = level_data["level"]
                y = start_point.y() + diff_y * level
                painter.drawLine(start_x, int(y), end_x, int(y))
                text_x = min(start_x, end_x) + 5
                painter.drawText(QPoint(text_x, int(y) - 8), f"{level:.3f}")
