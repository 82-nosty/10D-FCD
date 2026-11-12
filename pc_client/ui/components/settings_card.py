# -*- coding: utf-8 -*-
"""
10D FCD - Commercial Grade System Settings & Maintenance Card Component
- Windows Startup Registry Toggle
- Tray / Minimize Behavior
- Data & Log Directories
- Software & Firmware Info
"""
import os
import sys
import subprocess
import winreg
from pathlib import Path
from PyQt6.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout, QLabel,
                             QCheckBox, QPushButton, QMessageBox, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from config import APP_NAME, APP_VERSION, USER_DATA_DIR, LOG_DIR, SETTINGS_FILE
from core.i18n import I18nManager, LANG_KO


REG_KEY_RUN = r"Software\Microsoft\Windows\CurrentVersion\Run"
REG_APP_NAME = "10D_FCD"


class SettingsCard(QGroupBox):
    settings_changed = pyqtSignal()
    reset_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("", parent)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        # =====================================================================
        # 1. 시스템 동작 (시작 프로그램 / 트레이 최소화)
        # =====================================================================
        self.lbl_sec_sys = QLabel()
        self.lbl_sec_sys.setStyleSheet("color: #00E5FF; font-weight: 700; font-size: 14px;")
        layout.addWidget(self.lbl_sec_sys)

        self.cb_autostart = QCheckBox()
        self.cb_autostart.setChecked(self._check_autostart_reg())
        self.cb_autostart.toggled.connect(self._on_autostart_toggled)
        layout.addWidget(self.cb_autostart)

        self.cb_min_to_tray = QCheckBox()
        self.cb_min_to_tray.setChecked(True)
        self.cb_min_to_tray.toggled.connect(lambda: self.settings_changed.emit())
        layout.addWidget(self.cb_min_to_tray)

        self.cb_start_minimized = QCheckBox()
        self.cb_start_minimized.setChecked(False)
        self.cb_start_minimized.toggled.connect(lambda: self.settings_changed.emit())
        layout.addWidget(self.cb_start_minimized)

        line_sys = QFrame()
        line_sys.setFrameShape(QFrame.Shape.HLine)
        line_sys.setStyleSheet("background-color: #232836; max-height: 1px;")
        layout.addWidget(line_sys)

        # =====================================================================
        # 2. 쿨러 하드웨어 화면 회전
        # =====================================================================
        self.lbl_sec_flip = QLabel()
        self.lbl_sec_flip.setStyleSheet("color: #00E5FF; font-weight: 700; font-size: 14px;")
        layout.addWidget(self.lbl_sec_flip)

        self.cb_flip_180 = QCheckBox()
        self.cb_flip_180.setChecked(False)
        self.cb_flip_180.setStyleSheet("font-weight: 600; color: #F1F5F9;")
        self.cb_flip_180.toggled.connect(lambda: self.settings_changed.emit())
        layout.addWidget(self.cb_flip_180)

        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setStyleSheet("background-color: #232836; max-height: 1px;")
        layout.addWidget(line1)

        # =====================================================================
        # 3. 데이터 관리 및 유지보수
        # =====================================================================
        self.lbl_sec_data = QLabel()
        self.lbl_sec_data.setStyleSheet("color: #00E5FF; font-weight: 700; font-size: 14px;")
        layout.addWidget(self.lbl_sec_data)

        row_data = QHBoxLayout()
        row_data.setSpacing(10)
        self.btn_open_logs = QPushButton()
        self.btn_open_logs.setFixedHeight(42)
        self.btn_open_logs.clicked.connect(self._open_log_folder)

        self.btn_open_settings = QPushButton()
        self.btn_open_settings.setFixedHeight(42)
        self.btn_open_settings.clicked.connect(self._open_settings_file)

        self.btn_reset_all = QPushButton()
        self.btn_reset_all.setObjectName("StopButton")
        self.btn_reset_all.setFixedHeight(42)
        self.btn_reset_all.clicked.connect(self._confirm_reset)

        row_data.addWidget(self.btn_open_logs)
        row_data.addWidget(self.btn_open_settings)
        row_data.addWidget(self.btn_reset_all)
        layout.addLayout(row_data)

        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setStyleSheet("background-color: #232836; max-height: 1px;")
        layout.addWidget(line2)

        # =====================================================================
        # 3. 소프트웨어 & 하드웨어 정보
        # =====================================================================
        self.lbl_sec_about = QLabel()
        self.lbl_sec_about.setStyleSheet("color: #00E5FF; font-weight: 700; font-size: 14px;")
        layout.addWidget(self.lbl_sec_about)

        self.lbl_info_ver = QLabel(f"• Software Version: {APP_NAME} v{APP_VERSION} (Commercial Build)")
        self.lbl_info_ver.setStyleSheet("color: #E2E8F0; font-size: 13px;")
        layout.addWidget(self.lbl_info_ver)

        self.lbl_info_hw = QLabel("• Target Hardware: ESP32-2432S028 (2.8\" Portrait 240x320 LCD)")
        self.lbl_info_hw.setStyleSheet("color: #94A3B8; font-size: 13px;")
        layout.addWidget(self.lbl_info_hw)

        self.lbl_info_status = QLabel("• Burn-in Guard: 8-Way Pixel Orbiting + Smart PWM Dimming (Active)")
        self.lbl_info_status.setStyleSheet("color: #10B981; font-size: 13px; font-weight: 600;")
        layout.addWidget(self.lbl_info_status)

        layout.addStretch()
        self.retranslate()

    def retranslate(self):
        t = I18nManager.t
        is_ko = I18nManager.get_lang() == LANG_KO
        self.setTitle(f" {t('nav_settings')} ")
        self.lbl_sec_sys.setText("윈도우 연동 및 시스템 동작" if is_ko else "System & Window Behavior")
        self.cb_autostart.setText("윈도우 시작 시 10D FCD 자동 실행" if is_ko else "Start 10D FCD with Windows")
        self.cb_min_to_tray.setText("창 닫기(X) 시 시스템 트레이로 최소화 (백그라운드 스트리밍 유지)" if is_ko else "Minimize to System Tray on close (Keep Streaming)")
        self.cb_start_minimized.setText("프로그램 실행 시 트레이 아이콘으로 최소화 시작" if is_ko else "Start minimized in system tray")

        self.lbl_sec_flip.setText(t("settings_flip_sec"))
        self.cb_flip_180.setText(t("settings_flip_cb"))

        self.lbl_sec_data.setText("데이터 관리 및 유지보수" if is_ko else "Data Management & Maintenance")
        self.btn_open_logs.setText("로그 폴더 열기" if is_ko else "Open Log Folder")
        self.btn_open_settings.setText("설정 파일 열기" if is_ko else "Open Settings File")
        self.btn_reset_all.setText("모든 설정 초기화" if is_ko else "Reset All Settings")

        self.lbl_sec_about.setText("소프트웨어 및 펌웨어 정보" if is_ko else "About Software & Device")

    def _check_autostart_reg(self) -> bool:
        """Windows 레지스트리에 자동 실행 등록 여부 확인"""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY_RUN, 0, winreg.KEY_READ)
            val, _ = winreg.QueryValueEx(key, REG_APP_NAME)
            winreg.CloseKey(key)
            return bool(val)
        except Exception:
            return False

    def _on_autostart_toggled(self, checked: bool):
        """Windows 레지스트리에 시작 프로그램 등록 / 해제"""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY_RUN, 0, winreg.KEY_SET_VALUE)
            if checked:
                # EXE 실행 파일 경로 또는 현재 파이썬 스크립트 실행 경로
                if getattr(sys, 'frozen', False):
                    exe_path = f'"{sys.executable}"'
                else:
                    bat_path = Path(__file__).resolve().parent.parent.parent / "run_10D_FCD.bat"
                    if bat_path.exists():
                        exe_path = f'"{bat_path}"'
                    else:
                        exe_path = f'"{sys.executable}" "{Path(__file__).resolve().parent.parent.parent / "main.py"}"'
                winreg.SetValueEx(key, REG_APP_NAME, 0, winreg.REG_SZ, exe_path)
            else:
                try:
                    winreg.DeleteValue(key, REG_APP_NAME)
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception as e:
            is_ko = I18nManager.get_lang() == LANG_KO
            QMessageBox.warning(
                self,
                "시작 프로그램 설정 실패" if is_ko else "Startup Setting Failed",
                f"레지스트리 등록 오류: {e}"
            )
        self.settings_changed.emit()

    def _open_log_folder(self):
        try:
            os.startfile(str(LOG_DIR))
        except Exception as e:
            subprocess.Popen(["explorer", str(LOG_DIR)])

    def _open_settings_file(self):
        try:
            if SETTINGS_FILE.exists():
                os.startfile(str(SETTINGS_FILE))
            else:
                os.startfile(str(USER_DATA_DIR))
        except Exception:
            subprocess.Popen(["explorer", str(USER_DATA_DIR)])

    def _confirm_reset(self):
        is_ko = I18nManager.get_lang() == LANG_KO
        ret = QMessageBox.question(
            self,
            "설정 초기화 확인" if is_ko else "Confirm Settings Reset",
            "정말로 모든 설정을 초기 상태로 되돌리시겠습니까?\n이전 Wi-Fi 및 연결 기록이 삭제됩니다."
            if is_ko else "Are you sure you want to reset all settings to defaults?\nSaved Wi-Fi credentials will be cleared.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if ret == QMessageBox.StandardButton.Yes:
            self.reset_requested.emit()

    def get_settings(self) -> dict:
        return {
            "autostart": self.cb_autostart.isChecked(),
            "min_to_tray": self.cb_min_to_tray.isChecked(),
            "start_minimized": self.cb_start_minimized.isChecked(),
            "flip_180": self.cb_flip_180.isChecked()
        }

    def apply_settings(self, cfg: dict):
        self.cb_autostart.setChecked(bool(cfg.get("autostart", self._check_autostart_reg())))
        self.cb_min_to_tray.setChecked(bool(cfg.get("min_to_tray", True)))
        self.cb_start_minimized.setChecked(bool(cfg.get("start_minimized", False)))
        self.cb_flip_180.setChecked(bool(cfg.get("flip_180", False)))
