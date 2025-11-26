import os
import importlib
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QScrollArea, QFrame, QApplication, QGridLayout, QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import sys

ALGO_PATH = os.path.join(os.path.dirname(__file__), "algorithms")


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("デコード／エンコードツール")
        self.resize(1200, 800)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(6)  # カード間を詰める

        # --- 検索バー ---
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍 検索:")
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("出力を検索...")
        self.search_bar.textChanged.connect(self.update_results)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_bar)
        main_layout.addLayout(search_layout)

        # --- 入力欄 ---
        input_label = QLabel("入力テキスト:")
        self.input_box = QTextEdit()
        self.input_box.setFixedHeight(80)
        self.input_box.textChanged.connect(self.update_results)
        main_layout.addWidget(input_label)
        main_layout.addWidget(self.input_box)

        # --- スクロール領域（カード表示） ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.results_container = QWidget()
        self.results_layout = QGridLayout(self.results_container)
        self.results_layout.setSpacing(6)
        self.scroll_area.setWidget(self.results_container)
        main_layout.addWidget(self.scroll_area, stretch=1)

        # --- ステータス（説明表示） ---
        self.status_label = QLabel("アルゴリズムにカーソルを合わせると説明が表示されます。")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: gray;")
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)

        # アルゴリズムモジュールを自動読み込み
        self.algorithms = self.load_algorithms()

        # 初回描画
        self.update_results()

    def load_algorithms(self):
        algorithms = []
        for file in sorted(os.listdir(ALGO_PATH)):
            if not file.endswith(".py") or file.startswith("__"):
                continue
            module_name = file[:-3]
            module = importlib.import_module(f"windows.algorithms.{module_name}")
            algorithms.append(module)
        return algorithms

    def update_results(self):
        text = self.input_box.toPlainText()
        # 既存のカードを削除
        for i in reversed(range(self.results_layout.count())):
            widget = self.results_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # 1行2列に並べる
        row, col = 0, 0
        query = self.search_bar.text().strip().lower()
        for module in self.algorithms:
            result_text = module.run(text)
            if query and query not in result_text.lower():
                continue
            self.add_result_card(module, result_text, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1

    def add_result_card(self, module, result_text, row, col):
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet("""
            QFrame {
                background-color: #f7f9fa;
                border: 1px solid #d0d7de;
                border-radius: 6px;
                padding: 4px;  /* 縦幅縮小 */
            }
            QFrame:hover {
                background-color: #eef2f3;
            }
        """)
        layout = QVBoxLayout(card)
        layout.setSpacing(2)  # 内部余白を詰める

        # --- 名前＋コピー ---
        top_layout = QHBoxLayout()
        algo_label = QLabel(module.ALGO_NAME)
        algo_label.setFont(QFont("Meiryo", 10, QFont.Bold))
        algo_label.enterEvent = lambda e, d=module.DESCRIPTION: self.status_label.setText(d)
        algo_label.leaveEvent = lambda e: self.status_label.setText("アルゴリズムにカーソルを合わせると説明が表示されます。")
        top_layout.addWidget(algo_label)

        copy_btn = QPushButton("📋")
        copy_btn.setFixedSize(32, 32)
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #1d9bf0;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0d8ae5;
            }
        """)
        copy_btn.clicked.connect(lambda _, t=result_text: QApplication.clipboard().setText(t))
        top_layout.addWidget(copy_btn)
        layout.addLayout(top_layout)

        # --- シーザー暗号パラメータ専用 ---
        if hasattr(module, "VARIABLES") and "shift" in module.VARIABLES:
            param_layout = QHBoxLayout()
            label = QLabel(f"shift: {module.VARIABLES['shift']}")
            param_layout.addWidget(label)

            combo = QComboBox()
            for i in range(-13, 14):  # 固定リスト
                combo.addItem(str(i))
            combo.setCurrentText(str(module.VARIABLES["shift"]))

            def make_handler(m, lbl):
                return lambda value: self.update_variable(m, "shift", int(value), lbl)

            combo.currentTextChanged.connect(make_handler(module, label))
            param_layout.addWidget(combo)
            layout.addLayout(param_layout)

        # --- 結果テキスト ---
        result_box = QTextEdit(result_text)
        result_box.setReadOnly(True)
        result_box.setFixedHeight(30)  # 縦幅縮小
        result_box.setStyleSheet("""
            QTextEdit {
                background: #f7f9fa;
                color: #1d9bf0;
                border: none;
                font-family: Meiryo;
                font-size: 10pt;
            }
        """)
        layout.addWidget(result_box)

        self.results_layout.addWidget(card, row, col)

    def update_variable(self, module, var_name, value, label):
        module.VARIABLES[var_name] = value
        label.setText(f"{var_name}: {value}")
        self.update_results()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())
