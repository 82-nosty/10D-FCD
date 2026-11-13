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
from pathlib import Path

if sys.platform == "win32":
    try:
        import winreg
    except ImportError:
        winreg = None
else:
    winreg = None

from PyQt6.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout, QLabel,
                             QCheckBox, QPushButton, QMessageBox, QFrame,
                             QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt, pyqtSignal
from config import APP_NAME, APP_VERSION, USER_DATA_DIR, LOG_DIR, SETTINGS_FILE
from core.i18n import I18nManager, LANG_KO


REG_KEY_RUN = r"Software\Microsoft\Windows\CurrentVersion\Run"
REG_APP_NAME = "10D_FCD"
MAC_LAUNCH_PLIST = Path.home() / "Library" / "LaunchAgents" / "com.nosty.10dfcd.plist"


def open_path_native(path: Path):
    """OS별 기본 탐색기/파인더로 경로 열기"""
    str_path = str(path)
    try:
        if sys.platform == "win32":
            os.startfile(str_path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str_path])
        else:
            subprocess.Popen(["xdg-open", str_path])
    except Exception:
        if sys.platform == "win32":
            subprocess.Popen(["explorer", str_path])


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
        # 3. ESP32 저장 Wi-Fi 네트워크 관리 (다중 장소 자동 연결 목록)
        # =====================================================================
        self.lbl_sec_wifi = QLabel()
        self.lbl_sec_wifi.setStyleSheet("color: #00E5FF; font-weight: 700; font-size: 14px;")
        layout.addWidget(self.lbl_sec_wifi)

        self.list_wifi = QListWidget()
        self.list_wifi.setFixedHeight(120)
        self.list_wifi.setStyleSheet(
            "QListWidget { background-color: #12151D; border: 1px solid #232836; border-radius: 6px; padding: 4px; }"
            "QListWidget::item { padding: 6px 10px; color: #E2E8F0; border-radius: 4px; }"
            "QListWidget::item:selected { background-color: #1E293B; color: #00E5FF; }"
        )
        layout.addWidget(self.list_wifi)

        row_wifi_btn = QHBoxLayout()
        row_wifi_btn.setSpacing(10)
        self.btn_refresh_wifi = QPushButton()
        self.btn_refresh_wifi.setFixedHeight(36)
        self.btn_del_wifi = QPushButton()
        self.btn_del_wifi.setObjectName("StopButton")
        self.btn_del_wifi.setFixedHeight(36)
        row_wifi_btn.addWidget(self.btn_refresh_wifi)
        row_wifi_btn.addWidget(self.btn_del_wifi)
        layout.addLayout(row_wifi_btn)

        line_wifi = QFrame()
        line_wifi.setFrameShape(QFrame.Shape.HLine)
        line_wifi.setStyleSheet("background-color: #232836; max-height: 1px;")
        layout.addWidget(line_wifi)

        # =====================================================================
        # 4. 데이터 관리 및 유지보수
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

        self.lbl_sec_wifi.setText("기기 저장 Wi-Fi 네트워크 관리 (자동 연결 목록)" if is_ko else "Saved Wi-Fi Profiles on ESP32 (Auto-Connect)")
        self.btn_refresh_wifi.setText("저장 목록 불러오기" if is_ko else "Fetch Saved Wi-Fi")
        self.btn_del_wifi.setText("선택한 Wi-Fi 삭제" if is_ko else "Delete Selected Wi-Fi")

        self.lbl_sec_data.setText("데이터 관리 및 유지보수" if is_ko else "Data Management & Maintenance")
        self.btn_open_logs.setText("로그 폴더 열기" if is_ko else "Open Log Folder")
        self.btn_open_settings.setText("설정 파일 열기" if is_ko else "Open Settings File")
        self.btn_reset_all.setText("모든 설정 초기화" if is_ko else "Reset All Settings")

        self.lbl_sec_about.setText("소프트웨어 및 펌웨어 정보" if is_ko else "About Software & Device")

    def _check_autostart_reg(self) -> bool:
        """OS별 자동 실행 등록 여부 확인"""
        if sys.platform == "win32" and winreg:
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY_RUN, 0, winreg.KEY_READ)
                val, _ = winreg.QueryValueEx(key, REG_APP_NAME)
                winreg.CloseKey(key)
                return bool(val)
            except Exception:
                return False
        elif sys.platform == "darwin":
            return MAC_LAUNCH_PLIST.exists()
        return False

    def _on_autostart_toggled(self, checked: bool):
        """OS별 시작 프로그램 등록 / 해제 (Windows 레지스트리 / macOS LaunchAgent)"""
        is_ko = I18nManager.get_lang() == LANG_KO
        try:
            if sys.platform == "win32" and winreg:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY_RUN, 0, winreg.KEY_SET_VALUE)
                if checked:
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
            elif sys.platform == "darwin":
                if checked:
                    MAC_LAUNCH_PLIST.parent.mkdir(parents=True, exist_ok=True)
                    target_exec = sys.executable if getattr(sys, 'frozen', False) else f"{sys.executable} {Path(__file__).resolve().parent.parent.parent / 'app.py'}"
                    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.nosty.10dfcd</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>"""
                    MAC_LAUNCH_PLIST.write_text(plist_content, encoding="utf-8")
                else:
                    if MAC_LAUNCH_PLIST.exists():
                        MAC_LAUNCH_PLIST.unlink(missing_ok=True)
        except Exception as e:
            QMessageBox.warning(
                self,
                "시작 프로그램 설정 실패" if is_ko else "Startup Setting Failed",
                f"등록 오류: {e}"
            )
        self.settings_changed.emit()

    def _open_log_folder(self):
        open_path_native(LOG_DIR)

    def _open_settings_file(self):
        if SETTINGS_FILE.exists():
            open_path_native(SETTINGS_FILE)
        else:
            open_path_native(USER_DATA_DIR)

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

    def update_wifi_profiles(self, profiles: list):
        self.list_wifi.clear()
        is_ko = I18nManager.get_lang() == LANG_KO
        if not profiles:
            item = QListWidgetItem("저장된 Wi-Fi 없음" if is_ko else "No saved Wi-Fi profiles")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.list_wifi.addItem(item)
            return

        for p in profiles:
            ssid = p.get("ssid", "")
            p_type = p.get("type", "PSK")
            p_id = p.get("id", "")
            if p_type == "EAP":
                desc = f"{ssid}  (교내/기업용 EAP, ID: {p_id})" if is_ko else f"{ssid}  (Enterprise EAP, ID: {p_id})"
            else:
                desc = f"{ssid}  (일반 WPA-PSK)" if is_ko else f"{ssid}  (WPA-PSK)"
            item = QListWidgetItem(desc)
            item.setData(Qt.ItemDataRole.UserRole, ssid)
            self.list_wifi.addItem(item)

    def get_selected_wifi_ssid(self) -> str:
        item = self.list_wifi.currentItem()
        if item:
            return item.data(Qt.ItemDataRole.UserRole) or ""
        return ""

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
