import sys
import os
import cv2
import numpy as np
from pathlib import Path
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QTextEdit, QComboBox, QMessageBox, QFrame, QDialog
)
from PyQt5.QtGui import QPixmap, QImage, QFont, QColor
from PyQt5.QtCore import Qt, QRect, pyqtSignal, QPoint, QSize
from PyQt5.QtCore import QThread
import importlib.util


# グローバル変数：EasyOCRの遅延ロード用
_ocr_reader = None


def get_ocr_reader():
    """EasyOCRリーダーをシングルトンで取得（遅延ロード）"""
    global _ocr_reader
    if _ocr_reader is None:
        import easyocr
        _ocr_reader = easyocr.Reader(['ja', 'en'])
    return _ocr_reader


class InteractiveImageLabel(QLabel):
    """マウスドラッグで範囲選択ができるラベル"""
    range_selected = pyqtSignal(tuple)  # (x1, y1, x2, y2)

    def __init__(self):
        super().__init__()
        self.image_path = None
        self.original_pixmap = None
        self.start_pos = None
        self.end_pos = None
        self.selecting = False
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.displayed_pixmap = None  # 表示用のピクスマップ
        self.setStyleSheet("border: 1px solid gray; background-color: #f0f0f0;")
        self.setMinimumSize(400, 400)
        self.setAlignment(Qt.AlignCenter)

    def set_image(self, image_path):
        """画像を設定"""
        try:
            self.image_path = image_path
            self.original_pixmap = QPixmap(image_path)
            self.start_pos = None
            self.end_pos = None
            self.selecting = False

            # 画像が正しく読み込まれたか確認
            if self.original_pixmap.isNull():
                raise ValueError("画像ファイルが読み込めません")

            # スケール計算
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("OpenCVで画像が読み込めません")

            self.image_h, self.image_w = image.shape[:2]

            # 表示用のピクスマップを作成（スケーリング）
            self.displayed_pixmap = self.original_pixmap.scaledToWidth(400, Qt.SmoothTransformation)
            if self.displayed_pixmap.width() <= 0 or self.displayed_pixmap.height() <= 0:
                raise ValueError("画像のスケーリングに失敗しました")

            # スケール比率を計算
            self.scale_x = self.image_w / self.displayed_pixmap.width()
            self.scale_y = self.image_h / self.displayed_pixmap.height()
            
            self.setPixmap(self.displayed_pixmap)
        except Exception as e:
            QMessageBox.critical(None, "画像読み込みエラー", f"画像を読み込めません:\n{str(e)}")
            self.setPixmap(QPixmap())
            self.image_path = None

    def mousePressEvent(self, event):
        # 新しい選択を開始する時点で、前の選択を消す
        self.start_pos = event.pos()
        self.end_pos = None
        self.selecting = True
        self.update()

    def mouseMoveEvent(self, event):
        if self.selecting:
            self.end_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        self.end_pos = event.pos()
        self.selecting = False

        if self.start_pos and self.end_pos and self.image_path and self.displayed_pixmap:
            # ピクスマップの実際の描画矩形を取得
            pixmap_rect = self.pixmap().rect() if self.pixmap() else None
            if not pixmap_rect:
                return
            
            # ラベル内での実際の描画位置を計算
            label_rect = self.rect()
            pixmap_x = (label_rect.width() - pixmap_rect.width()) / 2
            pixmap_y = (label_rect.height() - pixmap_rect.height()) / 2
            
            # 座標をピクスマップ内のローカル座標に変換
            start_x = self.start_pos.x() - pixmap_x
            start_y = self.start_pos.y() - pixmap_y
            end_x = self.end_pos.x() - pixmap_x
            end_y = self.end_pos.y() - pixmap_y
            
            # 範囲チェック
            if (start_x < 0 or start_y < 0 or start_x >= pixmap_rect.width() or start_y >= pixmap_rect.height() or
                end_x < 0 or end_y < 0 or end_x >= pixmap_rect.width() or end_y >= pixmap_rect.height()):
                QMessageBox.warning(None, "警告", "画像の範囲内で選択してください")
                self.start_pos = None
                self.end_pos = None
                self.update()
                return

            # 画像座標に変換
            x1 = int(min(start_x, end_x) * self.scale_x)
            y1 = int(min(start_y, end_y) * self.scale_y)
            x2 = int(max(start_x, end_x) * self.scale_x)
            y2 = int(max(start_y, end_y) * self.scale_y)

            # 範囲が有効か確認
            if x2 - x1 > 10 and y2 - y1 > 10:
                self.range_selected.emit((x1, y1, x2, y2))
                self.update()
            else:
                QMessageBox.warning(None, "警告", "選択範囲が小さすぎます")
                self.start_pos = None
                self.end_pos = None
                self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        # 選択範囲の赤い線を描画（選択中または選択済み）
        if self.start_pos and self.end_pos:
            from PyQt5.QtGui import QPainter, QPen
            painter = QPainter(self)
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
            # 画像の読み込みを確認
            image = cv2.imread(self.image_path)
            if image is None:
                raise ValueError("画像ファイルが読み込めません")

            # 領域の妥当性を確認
            x1, y1, x2, y2 = self.region
            h, w = image.shape[:2]
            if x1 < 0 or y1 < 0 or x2 > w or y2 > h or x1 >= x2 or y1 >= y2:
                raise ValueError("指定された領域が画像の範囲外です")

            cropped = image[y1:y2, x1:x2]
            if cropped.size == 0:
                raise ValueError("抽出された領域が空です")

            # EasyOCRの遅延ロード（初回のみ重い）
            reader = get_ocr_reader()
            result = reader.readtext(cropped, detail=0)
            
            if not result:
                text = "テキストが検出されませんでした"
            else:
                text = '\n'.join(str(line) for line in result)

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

        # 画像プレビュー（範囲選択機能付き）
        self.preview_label = InteractiveImageLabel()
        self.preview_label.range_selected.connect(self.on_range_selected)
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
            self, "画像を選択", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp)"
        )
        if file_path:
            try:
                self.image_path = file_path
                self.current_region = None
                self.ocr_text.clear()
                self.result_text.clear()

                # プレビュー表示
                self.preview_label.set_image(file_path)
                self.reocr_btn.setEnabled(False)
            except Exception as e:
                QMessageBox.critical(self, "エラー", f"画像の読み込みに失敗しました:\n{str(e)}")
                self.image_path = None

    def on_range_selected(self, region):
        """範囲が選択された時の処理"""
        self.current_region = region
        # OCR処理が完了したら、次の選択の準備をする
        self.start_ocr(region)

    def start_ocr(self, region):
        """OCR処理を開始"""
        if not self.image_path:
            QMessageBox.warning(self, "警告", "画像が選択されていません")
            return

        if self.ocr_worker and self.ocr_worker.isRunning():
            QMessageBox.warning(self, "警告", "OCR処理中です。お待ちください")
            return

        self.preview_label.setEnabled(False)
        self.reocr_btn.setEnabled(False)
        self.ocr_text.setText("OCR処理中...")

        self.ocr_worker = OCRWorker(self.image_path, region)
        self.ocr_worker.ocr_finished.connect(self.on_ocr_finished)
        self.ocr_worker.ocr_error.connect(self.on_ocr_error)
        self.ocr_worker.start()

    def on_ocr_finished(self, text):
        """OCR完了時の処理"""
        self.ocr_text.setText(text)
        self.preview_label.setEnabled(True)
        self.reocr_btn.setEnabled(True)

    def on_ocr_error(self, error):
        """OCRエラー時の処理"""
        QMessageBox.critical(self, "OCRエラー", error)
        self.ocr_text.clear()
        self.preview_label.setEnabled(True)

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
