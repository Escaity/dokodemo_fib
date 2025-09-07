# main.py

import sys
import json
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt, QPoint
from pynput import mouse, keyboard

from config import Config
from ui_components import OverlayWidget, SettingsDialog


class FibonacciOverlay:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        self.widget = OverlayWidget(self)
        self.setup_window()

        self.settings = {}
        self.load_settings()

        self._is_hotkey_pressed = False
        self._drawing_is_committed = False
        self._start_point = QPoint()
        self._end_point = QPoint()

        self.exit_hotkey = keyboard.HotKey(
            keyboard.HotKey.parse(Config.EXIT_HOTKEY), self._on_exit
        )

    def setup_window(self):
        screen_geometry = self.app.primaryScreen().geometry()
        self.widget.setGeometry(screen_geometry)
        self.widget.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool
        )
        self.widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.widget.setMouseTracking(True)

    def load_settings(self):
        try:
            with open(Config.SETTINGS_FILENAME, "r") as f:
                self.settings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.settings = Config.DEFAULT_SETTINGS.copy()

    def save_settings(self, new_hotkey, new_levels_data):
        self.settings["hotkey"] = new_hotkey
        self.settings["levels"] = new_levels_data
        with open(Config.SETTINGS_FILENAME, "w") as f:
            json.dump(self.settings, f, indent=2)

    def open_settings_dialog(self):
        dialog = SettingsDialog(self.settings["hotkey"], self.settings["levels"])
        if dialog.exec():
            new_hotkey, new_levels = dialog.get_settings()
            self.save_settings(new_hotkey, new_levels)

    def get_start_point(self):
        return self._start_point

    def get_end_point(self):
        return self._end_point

    def _on_move(self, x, y):
        if self._is_hotkey_pressed:
            self._end_point = QPoint(x, y)
            self.widget.update()

    def _on_click(self, x, y, button, pressed):
        if pressed and self._drawing_is_committed:
            self._start_point = QPoint()
            self._end_point = QPoint()
            self.widget.update()
            self._drawing_is_committed = False

    def _on_press(self, key):
        self.exit_hotkey.press(key)
        try:
            hotkey = self.settings.get("hotkey", Config.DEFAULT_DRAW_KEY)
            if key.char == hotkey and not self._is_hotkey_pressed:
                self._is_hotkey_pressed = True
                self._drawing_is_committed = False
                with mouse.Controller() as m:
                    pos = m.position
                self._start_point = QPoint(pos[0], pos[1])
                self._end_point = self._start_point
                self.widget.update()
        except AttributeError:
            pass

    def _on_release(self, key):
        self.exit_hotkey.release(key)
        try:
            hotkey = self.settings.get("hotkey", Config.DEFAULT_DRAW_KEY)
            if key.char == hotkey:
                self._is_hotkey_pressed = False
                self._drawing_is_committed = True
        except AttributeError:
            pass

    def _on_exit(self):
        print("Exiting application...")
        if hasattr(self, 'keyboard_listener') and self.keyboard_listener.is_alive():
            self.keyboard_listener.stop()
        if hasattr(self, 'mouse_listener') and self.mouse_listener.is_alive():
            self.mouse_listener.stop()
        self.app.quit()

    def run(self):
        tray_icon = QSystemTrayIcon(QIcon(Config.ICON_FILENAME), parent=self.app)
        tray_icon.setToolTip(Config.APP_TOOLTIP)
        menu = QMenu()
        settings_action = QAction(Config.MENU_SETTINGS)
        settings_action.triggered.connect(self.open_settings_dialog)
        menu.addAction(settings_action)
        quit_action = QAction(Config.MENU_QUIT)
        quit_action.triggered.connect(self._on_exit)
        menu.addAction(quit_action)
        tray_icon.setContextMenu(menu)
        tray_icon.show()

        self.mouse_listener = mouse.Listener(on_move=self._on_move, on_click=self._on_click)
        self.keyboard_listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
        self.mouse_listener.start()
        self.keyboard_listener.start()

        self.widget.show()
        sys.exit(self.app.exec())


if __name__ == '__main__':
    overlay_app = FibonacciOverlay()
    overlay_app.run()
