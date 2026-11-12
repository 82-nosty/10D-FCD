# -*- coding: utf-8 -*-
"""
10D FCD - Hardware HUD Overlay & Performance Tuning Card Component (i18n + Live Sync)
"""
from PyQt6.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout, QLabel,
                             QCheckBox, QSlider, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from core.i18n import I18nManager


class OverlayCard(QGroupBox):
    settings_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("", parent)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        self.cb_cpu = QCheckBox()
        self.cb_cpu.setChecked(True)
        self.cb_cpu.toggled.connect(lambda: self.settings_changed.emit())
        layout.addWidget(self.cb_cpu)

        self.cb_ram = QCheckBox()
        self.cb_ram.setChecked(True)
        self.cb_ram.toggled.connect(lambda: self.settings_changed.emit())
        layout.addWidget(self.cb_ram)

        self.cb_time = QCheckBox()
        self.cb_time.setChecked(True)
        self.cb_time.toggled.connect(lambda: self.settings_changed.emit())
        layout.addWidget(self.cb_time)

        self.cb_fps = QCheckBox()
        self.cb_fps.setChecked(True)
        self.cb_fps.toggled.connect(lambda: self.settings_changed.emit())
        layout.addWidget(self.cb_fps)

        # 1. FPS 슬라이더
        f_row = QHBoxLayout()
        self.lbl_fps = QLabel()
        self.lbl_fps.setFixedWidth(185)
        self.slider_fps = QSlider(Qt.Orientation.Horizontal)
        self.slider_fps.setRange(10, 30)
        self.slider_fps.setValue(20)
        self.slider_fps.valueChanged.connect(self.on_fps_change)
        f_row.addWidget(self.lbl_fps)
        f_row.addWidget(self.slider_fps, 1)
        layout.addLayout(f_row)

        # 2. 품질 슬라이더
        q_row = QHBoxLayout()
        self.lbl_q = QLabel()
        self.lbl_q.setFixedWidth(185)
        self.slider_q = QSlider(Qt.Orientation.Horizontal)
        self.slider_q.setRange(50, 98)
        self.slider_q.setValue(90)
        self.slider_q.valueChanged.connect(self.on_q_change)
        q_row.addWidget(self.lbl_q)
        q_row.addWidget(self.slider_q, 1)
        layout.addLayout(q_row)

        # 3. HUD 반투명(불투명도) 감도 조절 슬라이더 (0% ~ 100%)
        a_row = QHBoxLayout()
        self.lbl_alpha = QLabel()
        self.lbl_alpha.setFixedWidth(185)
        self.slider_alpha = QSlider(Qt.Orientation.Horizontal)
        self.slider_alpha.setRange(0, 100)
        self.slider_alpha.setValue(75) # 기본 75%
        self.slider_alpha.valueChanged.connect(self.on_alpha_change)
        a_row.addWidget(self.lbl_alpha)
        a_row.addWidget(self.slider_alpha, 1)
        layout.addLayout(a_row)

        self.retranslate()

    def retranslate(self):
        t = I18nManager.t
        self.setTitle(f" {t('card_tuning_title')} ")
        self.cb_cpu.setText(t("hud_cpu"))
        self.cb_ram.setText(t("hud_ram"))
        self.cb_time.setText(t("hud_time"))
        self.cb_fps.setText(t("hud_fps"))
        self.lbl_fps.setText(f"{t('target_fps')}: {self.slider_fps.value()} FPS")
        self.lbl_q.setText(f"{t('jpeg_quality')}: {self.slider_q.value()}")
        alpha_pct = self.slider_alpha.value()
        self.lbl_alpha.setText(f"HUD 불투명도: {alpha_pct}%" if I18nManager.get_lang() == "KO" else f"HUD Opacity: {alpha_pct}%")

    def on_fps_change(self, val):
        t = I18nManager.t
        self.lbl_fps.setText(f"{t('target_fps')}: {val} FPS")
        self.settings_changed.emit()

    def on_q_change(self, val):
        t = I18nManager.t
        self.lbl_q.setText(f"{t('jpeg_quality')}: {val}")
        self.settings_changed.emit()

    def on_alpha_change(self, val):
        self.lbl_alpha.setText(f"HUD 불투명도: {val}%" if I18nManager.get_lang() == "KO" else f"HUD Opacity: {val}%")
        self.settings_changed.emit()

    def get_settings(self):
        alpha_val = int(round((self.slider_alpha.value() / 100.0) * 255))
        return {
            "show_cpu": self.cb_cpu.isChecked(),
            "show_ram": self.cb_ram.isChecked(),
            "show_time": self.cb_time.isChecked(),
            "show_fps": self.cb_fps.isChecked(),
            "fps": self.slider_fps.value(),
            "quality": self.slider_q.value(),
            "hud_alpha": alpha_val
        }

    def apply_settings(self, settings: dict):
        self.cb_cpu.setChecked(bool(settings.get("show_cpu", True)))
        self.cb_ram.setChecked(bool(settings.get("show_ram", True)))
        self.cb_time.setChecked(bool(settings.get("show_time", True)))
        self.cb_fps.setChecked(bool(settings.get("show_fps", True)))
        self.slider_fps.setValue(int(settings.get("fps", 20)))
        self.slider_q.setValue(int(settings.get("quality", 90)))
        raw_alpha = int(settings.get("hud_alpha", 190))
        self.slider_alpha.setValue(int(round((raw_alpha / 255.0) * 100)))
