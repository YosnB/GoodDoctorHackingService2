import sys
import importlib
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout,
    QWidget, QHBoxLayout, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("GoodDoctorHackingService")
        self.setFixedSize(500, 600)

        # サブウィンドウの参照管理
        self.windows = {}

        # === レイアウト ===
        main_layout = QVBoxLayout()

        # --- ロゴ ---
        logo_label = QLabel()
        pixmap = QPixmap("logo.png")
        logo_label.setPixmap(pixmap.scaledToWidth(200, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(logo_label)

        # --- ボタン群 ---
        self.buttons = {
            "decode": QPushButton("デコード エンコード"),
            "moji": QPushButton("文字起こし"),
            "image": QPushButton("画像解析")
        }

        # ボタンの説明テキスト
        self.descriptions = {
            "decode": "文字列を様々な形式でエンコード／デコードします。",
            "moji": "画像の文字を文字に起こします。",
            "image": "画像ファイルの情報を解析します。"
        }

        # 下部の説明ラベル
        self.status_label = QLabel("ボタンにカーソルを合わせると説明が表示されます。")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: gray; margin-top: 10px;")

        # ボタンの配置
        for key, button in self.buttons.items():
            button.setFixedHeight(50)
            button.setFont(QFont("Meiryo", 10))
            button.setCursor(Qt.PointingHandCursor)
            button.enterEvent = lambda e, k=key: self.on_hover(k)
            button.leaveEvent = lambda e: self.on_leave()
            button.clicked.connect(lambda _, k=key: self.open_window(k))
            main_layout.addWidget(button)

        main_layout.addSpacerItem(QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        main_layout.addWidget(self.status_label)

        # セントラルウィジェットに設定
        central = QWidget()
        central.setLayout(main_layout)
        self.setCentralWidget(central)

    # --- ボタンにカーソルを合わせた時の処理 ---
    def on_hover(self, key):
        self.status_label.setText(self.descriptions.get(key, ""))

    def on_leave(self):
        self.status_label.setText("ボタンにカーソルを合わせると説明が表示されます。")

    # --- ウィンドウを開く処理 ---
    def open_window(self, name):
        # すでにウィンドウが存在し、まだ閉じていない場合 → 再利用
        if name in self.windows and self.windows[name] and self.windows[name].isVisible():
            self.windows[name].raise_()
            self.windows[name].activateWindow()
            return

        # 該当モジュールをロード
        try:
            module = importlib.import_module(f"windows.{name}_window")
            window_class = getattr(module, "Window")
            self.windows[name] = window_class()
            self.windows[name].show()
        except ModuleNotFoundError:
            self.status_label.setText("この機能はまだないね")

    # --- メインウィンドウ終了時 ---
    def closeEvent(self, event):
        for w in self.windows.values():
            if w and w.isVisible():
                w.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
