# -*- coding: utf-8 -*-
"""
Portrait 240x320 Cooler LCD Bezel Mockup & Real-Time Preview Widget
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt
from config import TARGET_WIDTH, TARGET_HEIGHT
from core.i18n import I18nManager, LANG_KO


class PreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 쿨러 상단 LCD 하우징 베젤 목업
        self.bezel = QFrame()
        self.bezel.setObjectName("CoolerBezel")
        bezel_layout = QVBoxLayout(self.bezel)
        bezel_layout.setContentsMargins(12, 14, 12, 12)
        bezel_layout.setSpacing(8)
        bezel_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 상단 미세 LED/센서 바
        top_dot = QLabel("●")
        top_dot.setStyleSheet("color: #00E5FF; font-size: 8px;")
        top_dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bezel_layout.addWidget(top_dot)

        # 240 x 320 실제 LCD 화면 캔버스
        self.lbl_canvas = QLabel()
        self.lbl_canvas.setFixedSize(TARGET_WIDTH, TARGET_HEIGHT)
        self.lbl_canvas.setStyleSheet("""
            background-color: #000000;
            border: 1px solid #1E2430;
            border-radius: 4px;
            color: #64748B;
            font-weight: 700;
            font-size: 14px;
            line-height: 1.5;
        """)
        self.lbl_canvas.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_canvas.setWordWrap(True)
        bezel_layout.addWidget(self.lbl_canvas)

        # 하단 베젤 10D FCD 로고 각인
        lbl_brand = QLabel("10D FCD")
        lbl_brand.setStyleSheet("color: #475569; font-size: 11px; font-weight: 800; letter-spacing: 2px;")
        lbl_brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bezel_layout.addWidget(lbl_brand)

        outer.addWidget(self.bezel)
        self.set_blank()

    def set_blank(self):
        self.lbl_canvas.clear()
        if I18nManager.get_lang() == LANG_KO:
            self.lbl_canvas.setText("기기 연결 안 됨\n\n스트리밍을 시작하면\n실시간 화면이 표시됩니다\n(240 × 320)")
        else:
            self.lbl_canvas.setText("COOLER OFFLINE\n\nStart streaming to\npreview live LCD\n(240 × 320)")

    def update_frame(self, pil_image):
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")
        data = pil_image.tobytes("raw", "RGB")
        q_img = QImage(data, pil_image.size[0], pil_image.size[1], QImage.Format.Format_RGB888)
        self.lbl_canvas.setPixmap(QPixmap.fromImage(q_img))
