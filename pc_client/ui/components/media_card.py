# -*- coding: utf-8 -*-
"""
10D FCD - Media, MP4 Video & Virtual Display Selector Card (i18n supported)
"""
import os
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout, QLabel,
                             QRadioButton, QPushButton, QFileDialog,
                             QComboBox, QMessageBox, QCheckBox, QFrame)
from core.media_manager import MediaManager
from core.i18n import I18nManager, LANG_KO


class MediaCard(QGroupBox):
    def __init__(self, media_manager: MediaManager, parent=None):
        super().__init__("", parent)
        self.mm = media_manager
        self.last_path = ""
        self._monitors = []

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # 1. 기본 인포그래픽 모드
        self.rb_demo = QRadioButton()
        self.rb_demo.setChecked(True)
        self.rb_demo.toggled.connect(self.on_mode_change)
        layout.addWidget(self.rb_demo)

        # 2. 고화질 이미지 / GIF / MP4 동영상 모드
        self.rb_file = QRadioButton()
        self.rb_file.toggled.connect(self.on_mode_change)
        layout.addWidget(self.rb_file)

        row_f = QHBoxLayout()
        row_f.setContentsMargins(24, 0, 0, 0)
        self.btn_select = QPushButton()
        self.btn_select.setEnabled(False)
        self.btn_select.clicked.connect(self.select_file)

        self.lbl_file_name = QLabel()
        self.lbl_file_name.setStyleSheet("color: #94A3B8;")

        row_f.addWidget(self.btn_select)
        row_f.addWidget(self.lbl_file_name, 1)
        layout.addLayout(row_f)

        # 3. 가상 디스플레이 / PC 모니터 미러링 모드 (3:4)
        self.rb_screen = QRadioButton()
        self.rb_screen.toggled.connect(self.on_mode_change)
        layout.addWidget(self.rb_screen)

        # 모니터 선택 행
        row_m = QHBoxLayout()
        row_m.setContentsMargins(24, 0, 0, 0)
        self.lbl_mon = QLabel()
        self.lbl_mon.setFixedWidth(100)
        self.combo_monitor = QComboBox()
        self.combo_monitor.setEnabled(False)
        self.combo_monitor.currentIndexChanged.connect(self.on_monitor_changed)

        self.btn_refresh_mon = QPushButton()
        self.btn_refresh_mon.setEnabled(False)
        self.btn_refresh_mon.clicked.connect(self.refresh_monitors)

        row_m.addWidget(self.lbl_mon)
        row_m.addWidget(self.combo_monitor, 1)
        row_m.addWidget(self.btn_refresh_mon)
        layout.addLayout(row_m)

        # 비율 맞춤 행
        row_fit = QHBoxLayout()
        row_fit.setContentsMargins(24, 0, 0, 0)
        self.lbl_fit = QLabel()
        self.lbl_fit.setFixedWidth(100)
        self.combo_fit = QComboBox()
        self.combo_fit.setEnabled(False)
        self.combo_fit.currentIndexChanged.connect(self.on_fit_changed)

        row_fit.addWidget(self.lbl_fit)
        row_fit.addWidget(self.combo_fit, 1)
        layout.addLayout(row_fit)

        # 가상 디스플레이 가이드 줄바꿈 링크 버튼
        row_guide = QHBoxLayout()
        row_guide.setContentsMargins(24, 2, 0, 0)
        self.btn_vdd_guide = QPushButton()
        self.btn_vdd_guide.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_vdd_guide.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #38BDF8;
                font-size: 12px;
                font-weight: 600;
                text-align: left;
                padding: 4px 0;
            }
            QPushButton:hover {
                color: #00E5FF;
                text-decoration: underline;
            }
        """)
        self.btn_vdd_guide.clicked.connect(self.show_vdd_guide)
        row_guide.addWidget(self.btn_vdd_guide)
        row_guide.addStretch()
        layout.addLayout(row_guide)

        # 4. HUD 오버레이 마스터 스위치 (이미지/영상/가상화면 재생 시에도 HUD 표시)
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #232836; max-height: 1px; margin-top: 6px;")
        layout.addWidget(line)

        self.cb_hud_on_media = QCheckBox()
        self.cb_hud_on_media.setChecked(False)
        self.cb_hud_on_media.setStyleSheet("color: #00E5FF; font-weight: 700; font-size: 13px; padding: 4px 0;")
        layout.addWidget(self.cb_hud_on_media)

        self.refresh_monitors()
        self.retranslate()

    def retranslate(self):
        t = I18nManager.t
        self.setTitle(f" {t('card_media_title')} ")
        self.rb_demo.setText(t("mode_demo"))
        self.rb_file.setText(t("mode_file"))
        self.rb_screen.setText(t("mode_screen"))
        self.btn_select.setText(t("select_file_btn"))
        if self.mm.file_name == "None":
            self.lbl_file_name.setText(t("no_file_selected"))

        self.lbl_mon.setText(t("screen_target"))
        self.btn_refresh_mon.setText(t("refresh_btn"))
        self.lbl_fit.setText(t("screen_fit"))
        self.btn_vdd_guide.setText(t("vdd_guide_btn"))
        self.cb_hud_on_media.setText(t("hud_on_media"))

        cur_fit = self.combo_fit.currentIndex()
        self.combo_fit.blockSignals(True)
        self.combo_fit.clear()
        self.combo_fit.addItems([t("fit_cover"), t("fit_contain")])
        self.combo_fit.setCurrentIndex(cur_fit if cur_fit >= 0 else 0)
        self.combo_fit.blockSignals(False)

    def refresh_monitors(self):
        self._monitors = self.mm.list_monitors()
        self.combo_monitor.blockSignals(True)
        self.combo_monitor.clear()
        for m in self._monitors:
            self.combo_monitor.addItem(m["label"], m["index"])
        # 가상 디스플레이(Display 2 등)가 있으면 기본적으로 보조 모니터 선택 편의 제공
        if len(self._monitors) > 1:
            self.combo_monitor.setCurrentIndex(1)
            self.mm.selected_monitor_idx = self._monitors[1]["index"]
        elif self._monitors:
            self.mm.selected_monitor_idx = self._monitors[0]["index"]
        self.combo_monitor.blockSignals(False)

    def on_monitor_changed(self, idx):
        mon_id = self.combo_monitor.itemData(idx)
        if mon_id is not None:
            self.mm.selected_monitor_idx = int(mon_id)

    def on_fit_changed(self, idx):
        self.mm.fit_mode = "CONTAIN" if idx == 1 else "COVER"

    def on_mode_change(self):
        is_file = self.rb_file.isChecked()
        is_screen = self.rb_screen.isChecked()
        self.btn_select.setEnabled(is_file)
        self.combo_monitor.setEnabled(is_screen)
        self.btn_refresh_mon.setEnabled(is_screen)
        self.combo_fit.setEnabled(is_screen)

    def select_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Media File",
            "",
            "Media (*.mp4 *.gif *.png *.jpg *.jpeg *.avi *.mov *.mkv *.webm);;All Files (*.*)"
        )
        if path:
            ok, msg = self.mm.load_file(path)
            if ok:
                self.last_path = path
                self.lbl_file_name.setText(f"{self.mm.file_name} ({msg})")
            else:
                self.lbl_file_name.setText(f"Load Error: {msg}")

    def show_vdd_guide(self):
        is_ko = I18nManager.get_lang() == LANG_KO
        if is_ko:
            QMessageBox.information(
                self,
                "윈도우 3:4 가상 디스플레이 설정 방법",
                "10D FCD 쿨러를 윈도우의 '진짜 확장 모니터'로 인식시키려면:\n\n"
                "1. 오픈소스 가상 디스플레이 드라이버(Virtual Display Driver / IddSampleDriver)를 설치하면 윈도우 디스플레이 설정에 가상 모니터가 추가됩니다.\n"
                "2. 권장 해상도: 너무 낮으면 UI가 깨지므로 [720 × 960] 또는 [600 × 800] (3:4 세로 비율)로 설정하세요.\n"
                "3. 위 [대상 모니터] 목록에서 해당 가상 모니터를 선택하고 스트리밍을 시작하면, 유튜브/월페이퍼 엔진/하드웨어 모니터 창을 그 모니터로 끌어다 놓는 대로 240×320 쿨러 LCD에 꽉 차게 출력됩니다!"
            )
        else:
            QMessageBox.information(
                self,
                "Windows 3:4 Virtual Display Setup",
                "To add 10D FCD as a real extended Windows monitor:\n\n"
                "1. Install an open-source Virtual Display Driver (e.g., IddSampleDriver / MikeTheTech VDD).\n"
                "2. Recommended Resolution: Set it to [720 × 960] or [600 × 800] (3:4 Portrait).\n"
                "3. Select that virtual display in [Target Monitor] above and start streaming. Anything dragged onto that monitor (YouTube, Wallpaper Engine, hardware monitor) will display crisply on the cooler LCD!"
            )

    def get_mode(self):
        if self.rb_screen.isChecked():
            return "SCREEN"
        if self.rb_file.isChecked():
            return "FILE"
        return "DEMO"

    def get_media_path(self):
        return self.last_path

    def get_hud_on_media(self) -> bool:
        return self.cb_hud_on_media.isChecked()

    def apply_settings(self, settings: dict):
        mode = settings.get("media_mode", "DEMO")
        path = settings.get("media_path", "")
        self.cb_hud_on_media.setChecked(bool(settings.get("hud_on_media", False)))
        if path and os.path.exists(path):
            ok, msg = self.mm.load_file(path)
            if ok:
                self.last_path = path
                self.lbl_file_name.setText(f"{self.mm.file_name} ({msg})")
        if mode == "SCREEN":
            self.rb_screen.setChecked(True)
        elif mode == "FILE":
            self.rb_file.setChecked(True)
        else:
            self.rb_demo.setChecked(True)
