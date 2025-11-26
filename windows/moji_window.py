import sys
import os
import cv2
import numpy as np
import easyocr
from pathlib import Path
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QTextEdit, QComboBox, QMessageBox, QFrame, QDialog
)
from PyQt5.QtGui import QPixmap, QImage, QFont, QColor
from PyQt5.QtCore import Qt, QRect, pyqtSignal, QPoint, QSize
from PyQt5.QtCore import QThread
import importlib.util


class RangeSelector(QWidget):
    """スニッピングツール風の範囲選択ウィジェット"""
    range_selected = pyqtSignal(tuple)  # (x1, y1, x2, y2)

    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
        self.image = cv2.imread(image_path)
        self.image_rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.h, self.w = self.image_rgb.shape[:2]

        # ウィンドウサイズを画像サイズに制限（大きすぎる場合はスケール）
        max_size = 800
        if max(self.h, self.w) > max_size:
            scale = max_size / max(self.h, self.w)
            self.display_w = int(self.w * scale)
            self.display_h = int(self.h * scale)
        else:
            self.display_w = self.w
            self.display_h = self.h

        self.setWindowTitle("範囲選択")
        self.setGeometry(100, 100, self.display_w, self.display_h)

        # ウィンドウ全体をペイント用に使用
        self.start_pos = None
        self.end_pos = None
        self.selecting = False

        # ウィンドウ背景に画像を表示
        self.pixmap = QPixmap(self.image_path)
        self.pixmap = self.pixmap.scaledToWidth(self.display_w, Qt.SmoothTransformation)
        self.setStyleSheet("background-color: black;")

    def mousePressEvent(self, event):
        self.start_pos = event.pos()
        self.selecting = True

    def mouseMoveEvent(self, event):
        if self.selecting:
            self.end_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        self.end_pos = event.pos()
        self.selecting = False

        if self.start_pos and self.end_pos:
            # 画像座標に変換
            scale_x = self.w / self.display_w
            scale_y = self.h / self.display_h

            x1 = int(min(self.start_pos.x(), self.end_pos.x()) * scale_x)
            y1 = int(min(self.start_pos.y(), self.end_pos.y()) * scale_y)
            x2 = int(max(self.start_pos.x(), self.end_pos.x()) * scale_x)
            y2 = int(max(self.start_pos.y(), self.end_pos.y()) * scale_y)

            # 範囲が有効か確認
            if x2 - x1 > 10 and y2 - y1 > 10:
                self.range_selected.emit((x1, y1, x2, y2))
                self.close()
            else:
                QMessageBox.warning(self, "警告", "選択範囲が小さすぎます")

    def paintEvent(self, event):
        from PyQt5.QtGui import QPainter, QPen, QBrush
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.pixmap)

        if self.start_pos and self.end_pos:
            rect = QRect(self.start_pos, self.end_pos)
            pen = QPen(QColor(255, 0, 0), 2)
            painter.setPen(pen)
            painter.drawRect(rect)


class OCRWorker(QThread):
    """OCR処理を別スレッドで実行"""
    ocr_finished = pyqtSignal(str)
    ocr_error = pyqtSignal(str)

    def __init__(self, image_path, region):
        super().__init__()
        self.image_path = image_path
        self.region = region

    def run(self):
        try:
            # EasyOCRの初期化と処理
            reader = easyocr.Reader(['ja', 'en'])
            image = cv2.imread(self.image_path)

            x1, y1, x2, y2 = self.region
            cropped = image[y1:y2, x1:x2]

            result = reader.readtext(cropped, detail=0)
            text = '\n'.join(result)

            self.ocr_finished.emit(text)
        except Exception as e:
            self.ocr_error.emit(f"OCR処理エラー: {str(e)}")


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("文字起こし - OCRツール")
        self.setGeometry(100, 100, 900, 700)

        # アルゴリズム管理
        self.algorithms = self.load_algorithms()

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout
        main_layout = QHBoxLayout()

        # === 左側パネル ===
        left_layout = QVBoxLayout()

        # 画像選択ボタン
        self.select_btn = QPushButton("画像を選択")
        self.select_btn.clicked.connect(self.select_image)
        left_layout.addWidget(self.select_btn)

        # 範囲選択ボタン
        self.range_btn = QPushButton("範囲を選択（選択後に表示）")
        self.range_btn.clicked.connect(self.select_range)
        self.range_btn.setEnabled(False)
        left_layout.addWidget(self.range_btn)

        # 画像プレビュー
        self.preview_label = QLabel("画像がここに表示されます")
        self.preview_label.setStyleSheet("border: 1px solid gray; background-color: #f0f0f0;")
        self.preview_label.setMinimumSize(400, 400)
        self.preview_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.preview_label)

        left_frame = QFrame()
        left_frame.setLayout(left_layout)
        main_layout.addWidget(left_frame, 1)

        # === 右側パネル ===
        right_layout = QVBoxLayout()

        # OCRテキスト表示
        right_layout.addWidget(QLabel("認識された文字:"))
        self.ocr_text = QTextEdit()
        self.ocr_text.setReadOnly(False)
        self.ocr_text.setMinimumHeight(150)
        right_layout.addWidget(self.ocr_text)

        # 再認識ボタン
        self.reocr_btn = QPushButton("再認識")
        self.reocr_btn.clicked.connect(self.re_ocr)
        self.reocr_btn.setEnabled(False)
        right_layout.addWidget(self.reocr_btn)

        # 区切り線
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        right_layout.addWidget(separator)

        # アルゴリズム選択
        right_layout.addWidget(QLabel("エンコード/デコード方式:"))
        self.algo_combo = QComboBox()
        self.algo_combo.addItems(list(self.algorithms.keys()))
        right_layout.addWidget(self.algo_combo)

        # エンコード/デコードボタン
        button_layout = QHBoxLayout()
        self.encode_btn = QPushButton("実行")
        self.encode_btn.clicked.connect(self.execute_algorithm)
        button_layout.addWidget(self.encode_btn)

        self.copy_btn = QPushButton("コピー")
        self.copy_btn.clicked.connect(self.copy_result)
        button_layout.addWidget(self.copy_btn)

        right_layout.addLayout(button_layout)

        # 結果テキスト
        right_layout.addWidget(QLabel("結果:"))
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(False)
        self.result_text.setMinimumHeight(150)
        right_layout.addWidget(self.result_text)

        right_frame = QFrame()
        right_frame.setLayout(right_layout)
        main_layout.addWidget(right_frame, 1)

        central_widget.setLayout(main_layout)

        # 状態管理
        self.image_path = None
        self.current_region = None
        self.ocr_worker = None

    def load_algorithms(self):
        """algorithmsフォルダからアルゴリズムを動的に読み込む"""
        algorithms = {}
        algo_dir = Path(__file__).parent / "algorithms"

        if not algo_dir.exists():
            return algorithms

        for file in sorted(algo_dir.glob("*.py")):
            if file.name.startswith("__"):
                continue

            try:
                spec = importlib.util.spec_from_file_location(file.stem, file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                if hasattr(module, 'ALGO_NAME') and hasattr(module, 'run'):
                    algorithms[module.ALGO_NAME] = module.run
            except Exception as e:
                print(f"アルゴリズム読み込みエラー ({file.name}): {e}")

        return algorithms

    def select_image(self):
        """画像ファイルを選択"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "画像を選択", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            self.image_path = file_path
            self.current_region = None
            self.ocr_text.clear()
            self.result_text.clear()

            # プレビュー表示
            pixmap = QPixmap(file_path)
            pixmap = pixmap.scaledToWidth(400, Qt.SmoothTransformation)
            self.preview_label.setPixmap(pixmap)

            self.range_btn.setEnabled(True)
            self.reocr_btn.setEnabled(False)

    def select_range(self):
        """範囲選択ウィンドウを開く"""
        if not self.image_path:
            QMessageBox.warning(self, "エラー", "先に画像を選択してください")
            return

        self.selector = RangeSelector(self.image_path)
        self.selector.range_selected.connect(self.on_range_selected)
        self.selector.show()

    def on_range_selected(self, region):
        """範囲が選択された時の処理"""
        self.current_region = region
        self.start_ocr(region)

    def start_ocr(self, region):
        """OCR処理を開始"""
        if self.ocr_worker and self.ocr_worker.isRunning():
            QMessageBox.warning(self, "警告", "OCR処理中です。お待ちください")
            return

        self.range_btn.setEnabled(False)
        self.reocr_btn.setEnabled(False)
        self.ocr_text.setText("OCR処理中...")

        self.ocr_worker = OCRWorker(self.image_path, region)
        self.ocr_worker.ocr_finished.connect(self.on_ocr_finished)
        self.ocr_worker.ocr_error.connect(self.on_ocr_error)
        self.ocr_worker.start()

    def on_ocr_finished(self, text):
        """OCR完了時の処理"""
        self.ocr_text.setText(text)
        self.range_btn.setEnabled(True)
        self.reocr_btn.setEnabled(True)

    def on_ocr_error(self, error):
        """OCRエラー時の処理"""
        QMessageBox.critical(self, "OCRエラー", error)
        self.ocr_text.clear()
        self.range_btn.setEnabled(True)

    def re_ocr(self):
        """再認識"""
        if self.current_region and self.image_path:
            self.start_ocr(self.current_region)

    def execute_algorithm(self):
        """選択したアルゴリズムを実行"""
        algo_name = self.algo_combo.currentText()
        if algo_name not in self.algorithms:
            QMessageBox.warning(self, "エラー", "アルゴリズムが見つかりません")
            return

        input_text = self.ocr_text.toPlainText()
        if not input_text.strip():
            QMessageBox.warning(self, "警告", "入力テキストが空です")
            return

        try:
            result = self.algorithms[algo_name](input_text)
            self.result_text.setText(result)
        except Exception as e:
            QMessageBox.critical(self, "実行エラー", f"{algo_name}の実行に失敗しました:\n{str(e)}")

    def copy_result(self):
        """結果をクリップボードにコピー"""
        from PyQt5.QtWidgets import QApplication
        result_text = self.result_text.toPlainText()
        if result_text:
            QApplication.clipboard().setText(result_text)
            QMessageBox.information(self, "成功", "クリップボードにコピーしました")
        else:
            QMessageBox.warning(self, "警告", "コピーする内容がありません")


def main():
    app = None
    if QApplication.instance() is None:
        from PyQt5.QtWidgets import QApplication
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

    window = Window()
    window.show()

    if app:
        sys.exit(app.exec_())


if __name__ == "__main__":
    main()
