from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QFileDialog, QTextBrowser, QApplication
from PyQt5.QtGui import QPixmap, QImage
from PIL import Image, ExifTags
import numpy as np
import os
import sys

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("画像解析ツール")
        self.setFixedSize(600, 550)

        layout = QVBoxLayout()

        # ボタン
        self.open_btn = QPushButton("画像を開く")
        self.open_btn.clicked.connect(self.open_image)
        layout.addWidget(self.open_btn)

        # 画像表示
        self.image_label = QLabel("画像プレビュー")
        self.image_label.setFixedSize(400, 300)
        layout.addWidget(self.image_label)

        # 結果表示
        self.result_text = QTextBrowser()
        self.result_text.setOpenExternalLinks(True)
        layout.addWidget(self.result_text)

        self.setLayout(layout)

    # --- 画像を安全に開く（HEIC対応） ---
    def open_image_safely(self, path):
        ext = os.path.splitext(path)[1].lower()
        if ext in [".heic", ".heif"]:
            try:
                from pillow_heif import register_heif_opener
                register_heif_opener()
            except ImportError:
                raise ImportError("HEICを開くには pillow-heif をインストールしてください")
        return Image.open(path)

    # --- Pillow Image -> QPixmap ---
    def pil2pixmap(self, img):
        img = img.convert("RGBA")
        data = img.tobytes("raw", "RGBA")
        qimg = QImage(data, img.width, img.height, QImage.Format_RGBA8888)
        return QPixmap.fromImage(qimg)

    # --- GPSを10進数に変換 ---
    def gps_to_decimal(self, coord, ref):
        def to_float(r):
            try:
                return float(r)
            except TypeError:
                return r
        deg = to_float(coord[0])
        min_ = to_float(coord[1])
        sec = to_float(coord[2])
        dec = deg + (min_ / 60) + (sec / 3600)
        if ref in ['S', 'W']:
            dec = -dec
        return dec

    # --- 画像解析 ---
    def open_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "画像を選択", "", "Images (*.png *.jpg *.bmp *.jpeg *.heic *.heif)"
        )
        if not path:
            return

        try:
            img = self.open_image_safely(path)

            # プレビュー表示
            pixmap = self.pil2pixmap(img).scaled(self.image_label.width(), self.image_label.height())
            self.image_label.setPixmap(pixmap)

            # HTML形式で表示
            info = "<div style='font-size:150%'>"
            info += f"<p>形式: {img.format}</p>"
            info += f"<p>サイズ: {img.size}</p>"
            info += f"<p>モード: {img.mode}</p>"

            # --- EXIF情報取得 ---
            exif_data = None
            if hasattr(img, "_getexif"):  # JPEGなど
                exif_data = img._getexif()
            elif hasattr(img, "info") and "exif" in img.info:  # HEICの場合
                try:
                    from PIL.TiffImagePlugin import ImageFileDirectory_v2
                    import io
                    exif_bytes = img.info["exif"]
                    exif_ifd = ImageFileDirectory_v2()
                    exif_ifd.load(io.BytesIO(exif_bytes))
                    exif_data = dict(exif_ifd)
                except Exception:
                    exif_data = None

            # GPS情報
            if exif_data:
                exif = {ExifTags.TAGS.get(k, k): v for k, v in exif_data.items()}
                gps_info = exif.get("GPSInfo")
                if gps_info:
                    try:
                        gps_tags = {ExifTags.GPSTAGS.get(k, k): v for k, v in gps_info.items()}
                        lat = self.gps_to_decimal(gps_tags["GPSLatitude"], gps_tags["GPSLatitudeRef"])
                        lon = self.gps_to_decimal(gps_tags["GPSLongitude"], gps_tags["GPSLongitudeRef"])
                        link = f"https://www.google.com/maps?q={lat},{lon}"
                        info += f"<p>GPS情報あり: {lat:.6f}, {lon:.6f}</p>"
                        info += f"<p>Google Maps: <a href='{link}'>ここをクリック</a></p>"
                    except Exception:
                        info += "<p>GPSタグは存在しますが、情報が不完全です</p>"
                else:
                    info += "<p>EXIF情報はありますがGPSはありません</p>"
            else:
                info += "<p>EXIF情報は取得できません</p>"

            # RGB平均値
            img_np = np.array(img)
            if len(img_np.shape) == 3:
                mean_rgb = np.mean(img_np, axis=(0,1))
                info += f"<p>平均RGB: {mean_rgb}</p>"

            info += "</div>"
            self.result_text.setHtml(info)

        except Exception as e:
            self.result_text.setHtml(f"<div style='font-size:150%'>解析中にエラーが発生: {e}</div>")

# 単体起動用
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())
