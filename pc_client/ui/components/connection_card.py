# -*- coding: utf-8 -*-
"""
10D FCD - Network & Port Connection Card Component (i18n + Full Error Handling)
"""
from PyQt6.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QPushButton, QLineEdit, QMessageBox)
from PyQt6.QtCore import pyqtSignal
from core.serial_manager import SerialManager
from core.i18n import I18nManager, LANG_KO


class ConnectionCard(QGroupBox):
    serial_status_changed = pyqtSignal(bool)
    ip_updated_signal = pyqtSignal(str)
    before_send_wifi_signal = pyqtSignal()

    def __init__(self, serial_manager: SerialManager, parent=None):
        super().__init__("", parent)
        self.sm = serial_manager
        self._current_ip = ""
        self._saved_ssid = ""
        self._saved_pw = ""

        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        # 1. COM 포트 행
        r1 = QHBoxLayout()
        self.lbl_p = QLabel()
        self.lbl_p.setFixedWidth(115)
        self.combo_port = QComboBox()
        self.btn_refresh = QPushButton()
        self.btn_refresh.clicked.connect(self.refresh_ports)
        self.btn_port_conn = QPushButton()
        self.btn_port_conn.clicked.connect(self.toggle_port)

        r1.addWidget(self.lbl_p)
        r1.addWidget(self.combo_port, 1)
        r1.addWidget(self.btn_refresh)
        r1.addWidget(self.btn_port_conn)
        layout.addLayout(r1)

        # 2. Wi-Fi AP 및 스캔 행
        r2 = QHBoxLayout()
        self.lbl_w = QLabel()
        self.lbl_w.setFixedWidth(115)
        self.combo_wifi = QComboBox()
        self.btn_scan = QPushButton()
        self.btn_scan.clicked.connect(self.on_scan_clicked)

        r2.addWidget(self.lbl_w)
        r2.addWidget(self.combo_wifi, 1)
        r2.addWidget(self.btn_scan)
        layout.addLayout(r2)

        # 3. 비밀번호 및 전송 행 (초기값 비움!)
        r3 = QHBoxLayout()
        self.lbl_pw = QLabel()
        self.lbl_pw.setFixedWidth(115)
        self.edit_pw = QLineEdit()
        self.edit_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.btn_send_wifi = QPushButton()
        self.btn_send_wifi.clicked.connect(self.send_wifi)

        r3.addWidget(self.lbl_pw)
        r3.addWidget(self.edit_pw, 1)
        r3.addWidget(self.btn_send_wifi)
        layout.addLayout(r3)

        # 4. 기기 IP 주소 행 (읽기 전용 자동 동기화 필드!)
        r4 = QHBoxLayout()
        self.lbl_ip = QLabel()
        self.lbl_ip.setFixedWidth(115)
        self.edit_ip = QLineEdit()
        self.edit_ip.setReadOnly(True)
        r4.addWidget(self.lbl_ip)
        r4.addWidget(self.edit_ip, 1)
        layout.addLayout(r4)

        self.sm.scan_result_signal.connect(self.on_scan_result)
        self.sm.wifi_connected_signal.connect(self.on_wifi_connected)
        self.sm.error_signal.connect(self.on_serial_error)
        self.sm.busy_signal.connect(self.on_busy_state_changed)

        self.refresh_ports()
        self.retranslate()

    def retranslate(self):
        t = I18nManager.t
        is_ko = I18nManager.get_lang() == LANG_KO
        self.setTitle(f" {t('card_conn_title')} ")
        self.lbl_p.setText(t("com_port"))
        self.btn_refresh.setText(t("refresh_btn"))
        self.btn_port_conn.setText(t("disconnect_btn") if self.sm.is_connected() else t("connect_btn"))
        self.lbl_w.setText(t("wifi_ap"))
        self.btn_scan.setText(t("scan_btn"))
        self.lbl_pw.setText(t("password"))
        self.btn_send_wifi.setText(t("send_wifi_btn"))
        self.lbl_ip.setText(t("target_ip"))

        self.combo_wifi.setPlaceholderText(
            "주변 스캔 버튼을 눌러 Wi-Fi를 선택하세요" if is_ko else "Click Scan APs to select Wi-Fi"
        )
        self.edit_pw.setPlaceholderText(
            "와이파이 비밀번호를 입력하세요" if is_ko else "Enter Wi-Fi password"
        )
        self.edit_ip.setPlaceholderText(
            "와이파이 연결 완료 시 IP가 자동 표시됩니다" if is_ko else "Auto-filled after Wi-Fi connection"
        )

    def refresh_ports(self):
        ports = self.sm.list_ports()
        self.combo_port.clear()
        self.combo_port.addItems(ports)

    def toggle_port(self):
        if self.sm.is_connected():
            self.sm.disconnect_port()
            self.btn_port_conn.setText(I18nManager.t("connect_btn"))
            self.serial_status_changed.emit(False)
        else:
            port = self.combo_port.currentText()
            if not port:
                is_ko = I18nManager.get_lang() == LANG_KO
                QMessageBox.warning(
                    self,
                    "포트 없음" if is_ko else "No Port",
                    "연결할 시리얼 포트(COM)가 없습니다. USB 케이블을 확인해 주세요." if is_ko else "No serial port available."
                )
                return
            if self.sm.connect_port(port):
                self.btn_port_conn.setText(I18nManager.t("disconnect_btn"))
                self.serial_status_changed.emit(True)
                self.sm.set_device_language(I18nManager.get_lang())
                self.sm.query_device_ip()

    def on_serial_error(self, title: str, detail: str):
        QMessageBox.warning(self, title, detail)

    def on_scan_clicked(self):
        self.sm.scan_wifi()

    def on_scan_result(self, aps):
        prev_ssid = self.combo_wifi.currentText().strip() or self._saved_ssid
        self.combo_wifi.clear()
        if aps:
            self.combo_wifi.addItems(aps)
            if prev_ssid:
                idx = self.combo_wifi.findText(prev_ssid)
                if idx >= 0:
                    self.combo_wifi.setCurrentIndex(idx)
            self.combo_wifi.showPopup()
        else:
            is_ko = I18nManager.get_lang() == LANG_KO
            QMessageBox.warning(
                self,
                "Wi-Fi 스캔" if is_ko else "Wi-Fi Scan",
                "주변에서 검색된 2.4GHz 와이파이가 없습니다." if is_ko else "No 2.4GHz Wi-Fi networks found nearby."
            )

    def on_busy_state_changed(self, is_busy: bool):
        self.btn_send_wifi.setEnabled(not is_busy)
        self.btn_scan.setEnabled(not is_busy)
        self.btn_refresh.setEnabled(not is_busy)
        if is_busy:
            self.btn_send_wifi.setText("진행 중..." if I18nManager.get_lang() == LANG_KO else "Processing...")
        else:
            self.btn_send_wifi.setText(I18nManager.t("send_wifi_btn"))

    def send_wifi(self):
        is_ko = I18nManager.get_lang() == LANG_KO
        if not self.sm.is_connected():
            QMessageBox.warning(
                self,
                "시리얼 연결 필요" if is_ko else "Serial Required",
                "먼저 상단의 [시리얼 포트]에서 COM 포트를 연결해 주세요." if is_ko else "Please connect the Serial Port (COM) first."
            )
            return

        ssid = self.combo_wifi.currentText().strip()
        if not ssid:
            QMessageBox.warning(
                self,
                "와이파이 선택 필요" if is_ko else "Wi-Fi Required",
                "먼저 [주변 스캔]을 눌러 연결할 와이파이를 선택해 주세요." if is_ko else "Please scan and select a Wi-Fi AP first."
            )
            return

        # Wi-Fi 설정 전 스트리밍 안전 정지 신호 방출
        self.before_send_wifi_signal.emit()

        pw = self.edit_pw.text().strip()
        self._pending_ssid = ssid
        self._pending_pw = pw
        self.sm.connect_wifi(ssid, pw)

    def on_wifi_connected(self, ip):
        self._current_ip = ip
        self.edit_ip.setText(ip)
        if getattr(self, "_pending_ssid", ""):
            self._saved_ssid = self._pending_ssid
            self._saved_pw = getattr(self, "_pending_pw", "")
        self.ip_updated_signal.emit(ip)

    def get_target_ip(self):
        return self._current_ip.strip() or self.edit_ip.text().strip()

    def get_selected_port(self):
        return self.combo_port.currentText().strip()

    def get_wifi_credentials(self):
        ssid = self._saved_ssid or self.combo_wifi.currentText().strip()
        pw = self._saved_pw or self.edit_pw.text().strip()
        return ssid, pw

    def apply_settings(self, settings: dict):
        saved_ip = settings.get("target_ip", "").strip()
        if saved_ip and saved_ip != "0.0.0.0":
            self._current_ip = saved_ip
            self.edit_ip.setText(saved_ip)

        saved_port = settings.get("com_port", "").strip()
        if saved_port:
            idx = self.combo_port.findText(saved_port)
            if idx >= 0:
                self.combo_port.setCurrentIndex(idx)

        saved_ssid = settings.get("wifi_ssid", "").strip()
        saved_pw = settings.get("wifi_pw", "").strip()
        if saved_ssid:
            self._saved_ssid = saved_ssid
            if self.combo_wifi.findText(saved_ssid) < 0:
                self.combo_wifi.addItem(saved_ssid)
            self.combo_wifi.setCurrentText(saved_ssid)
        if saved_pw:
            self._saved_pw = saved_pw
            self.edit_pw.setText(saved_pw)
