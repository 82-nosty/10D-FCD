# -*- coding: utf-8 -*-
"""
10D FCD - Mobile Gallery Style Theme Community Component
- Compact thumbnail grid (No horizontal scrolling)
- Click-to-apply (Instant preview & selection)
- Hover overlay showing dimmed thumbnail with truncated title
- Active neon cyan border & badge
"""
from pathlib import Path
from PyQt6.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QScrollArea, QWidget, QGridLayout, QFrame)
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont
from PyQt6.QtCore import Qt, pyqtSignal
from core.i18n import I18nManager, LANG_KO
from core.theme_engine import ThemeEngine


class ThemeThumbnailTile(QFrame):
    clicked = pyqtSignal(str) # theme_id

    def __init__(self, theme_id: str, name: str, preview_path: str, is_active: bool, parent=None):
        super().__init__(parent)
        self.theme_id = theme_id
        self.theme_name = name
        self.preview_path = preview_path
        self.is_active = is_active
        self.is_hovered = False

        self.setFixedSize(148, 198)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._pixmap = None
        if preview_path and Path(preview_path).exists():
            self._pixmap = QPixmap(preview_path).scaled(
                144, 192,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

    def set_active(self, active: bool):
        self.is_active = active
        self.update()

    def enterEvent(self, event):
        self.is_hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.is_hovered = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.theme_id)
        super().mousePressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 1. 외곽 프레임 (활성: 시안 테두리, 비활성: 딥 슬레이트)
        bg_col = QColor(14, 18, 27)
        border_col = QColor(0, 229, 255) if self.is_active else (QColor(59, 130, 246) if self.is_hovered else QColor(35, 42, 56))
        border_width = 2 if (self.is_active or self.is_hovered) else 1

        painter.setBrush(bg_col)
        painter.setPen(border_col)
        rect = self.rect().adjusted(1, 1, -1, -1)
        painter.drawRoundedRect(rect, 8, 8)

        # 2. 썸네일 이미지 중앙 렌더링
        if self._pixmap and not self._pixmap.isNull():
            px = (self.width() - self._pixmap.width()) // 2
            py = (self.height() - self._pixmap.height()) // 2
            painter.drawPixmap(px, py, self._pixmap)

        # 3. 호버(Hover) 상태: 썸네일 딤(반투명 오버레이) + 타이틀 텍스트 오버레이
        if self.is_hovered:
            painter.setBrush(QColor(10, 15, 25, 210))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(rect, 8, 8)

            # 호버 시 제목 표시 (가로 폭 초과 시 자동 줄바꿈 및 ... 처리)
            painter.setPen(QColor(255, 255, 255))
            font = QFont("Segoe UI", 11)
            font.setBold(True)
            painter.setFont(font)
            text_rect = self.rect().adjusted(10, 14, -10, -14)
            painter.drawText(
                text_rect,
                Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap,
                self.theme_name
            )

        # 4. 활성화 상태 배지 (우상단 체크 마크)
        if self.is_active:
            painter.setBrush(QColor(0, 229, 255))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(self.width() - 24, 8, 16, 16)
            painter.setPen(QColor(10, 15, 25))
            font_b = QFont("Segoe UI", 10)
            font_b.setBold(True)
            painter.setFont(font_b)
            painter.drawText(self.width() - 24, 8, 16, 16, Qt.AlignmentFlag.AlignCenter, "✓")


class ThemeCommunityCard(QGroupBox):
    theme_selected = pyqtSignal(str) # theme_id

    def __init__(self, theme_engine: ThemeEngine, parent=None):
        super().__init__("", parent)
        self.te = theme_engine
        self.active_theme_id = "design1_classic"
        self._tiles = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # 상단 헤더: 미니멀 설명 + 새로고침
        top_bar = QHBoxLayout()
        self.lbl_desc = QLabel()
        self.lbl_desc.setStyleSheet("color: #94A3B8; font-size: 12px;")
        self.btn_refresh = QPushButton()
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.clicked.connect(self.populate_themes)
        top_bar.addWidget(self.lbl_desc, 1)
        top_bar.addWidget(self.btn_refresh)
        layout.addLayout(top_bar)

        # 스크롤 영역 (가로 스크롤 완전 차단)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #0F131D;
                width: 8px;
                margin: 0;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #252D3D;
                min-height: 24px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #00E5FF;
            }
        """)

        self.grid_container = QWidget()
        self.grid_container.setStyleSheet("background-color: transparent;")
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(6)
        self.grid_layout.setContentsMargins(2, 2, 2, 2)

        scroll.setWidget(self.grid_container)
        layout.addWidget(scroll, 1)

        self.retranslate()
        self.populate_themes()

    def retranslate(self):
        is_ko = I18nManager.get_lang() == LANG_KO
        self.setTitle(" 테마 프리셋 갤러리 " if is_ko else " Theme Preset Gallery ")
        self.lbl_desc.setText(
            "원하는 테마 썸네일을 클릭하면 즉시 쿨러 화면에 적용됩니다."
            if is_ko else "Click any thumbnail to instantly apply it to your cooler display."
        )
        self.btn_refresh.setText("새로고침" if is_ko else "Refresh")

    def populate_themes(self):
        # 기존 타일 정리
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._tiles.clear()

        themes = self.te.list_available_themes()
        is_ko = I18nManager.get_lang() == LANG_KO

        # 갤러리 그리드: 3열(가로 스크롤 없이 넉넉하게 세로 배열)
        cols = 3
        for idx, th in enumerate(themes):
            tid = th.get("id", "")
            name = th.get("name_ko" if is_ko else "name", th.get("name", tid))
            preview_path = th.get("preview", "")

            is_active = (tid == self.active_theme_id)
            tile = ThemeThumbnailTile(tid, name, preview_path, is_active)
            tile.clicked.connect(self._apply_theme)
            self._tiles[tid] = tile

            r, c = divmod(idx, cols)
            self.grid_layout.addWidget(tile, r, c)

        # 남은 빈 공간 스트레치
        self.grid_layout.setRowStretch(len(themes) // cols + 1, 1)

    def _apply_theme(self, tid: str):
        if self.active_theme_id == tid:
            return
        self.active_theme_id = tid
        for t_id, tile in self._tiles.items():
            tile.set_active(t_id == tid)
        self.te.load_theme(tid)
        self.theme_selected.emit(tid)
