""" アプリケーションの設定値や定数を一元管理するクラス """


class Config:
    # ファイル設定
    SETTINGS_FILENAME = "settings.json"
    ICON_FILENAME = "icon.png"

    # ホットキー設定
    EXIT_HOTKEY = "<ctrl>+<alt>+x"
    DEFAULT_DRAW_KEY = "f"

    # 描画設定
    PEN_WIDTH = 1.5
    DEFAULT_NEW_LEVEL_COLOR = "#FFFFFF"

    # UIテキスト
    APP_TOOLTIP = "Dokodemo Fib"
    MENU_SETTINGS = "設定"
    MENU_QUIT = "終了"
    DIALOG_TITLE = "詳細設定"
    DIALOG_DRAW_KEY_LABEL = "描画キー:"
    DIALOG_LEVELS_LABEL = "フィボナッチレベル:"
    DIALOG_ADD_LEVEL = "レベルを追加"
    DIALOG_COLOR_PICKER_TITLE = "色の選択"
    DIALOG_DELETE_BTN = "削除"

    # デフォルト設定データ
    DEFAULT_SETTINGS = {
        "hotkey": DEFAULT_DRAW_KEY,
        "levels": [
            {"level": 0, "enabled": True, "color": "#808080"},
            {"level": 0.214, "enabled": True, "color": "#ff0000"},
            {"level": 0.256, "enabled": True, "color": "#adff2f"},
            {"level": 0.382, "enabled": True, "color": "#00ff00"},
            {"level": 0.5, "enabled": True, "color": "#20b2aa"},
            {"level": 0.786, "enabled": False, "color": "#00008b"},
            {"level": 1, "enabled": True, "color": "#808080"},
            {"level": 1.618, "enabled": False, "color": "#4b0082"}
        ]
    }
