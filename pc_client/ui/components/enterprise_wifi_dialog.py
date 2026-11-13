# -*- coding: utf-8 -*-
"""
10D FCD - Enterprise Wi-Fi Modal Dialog
Appears when connecting to an Enterprise (802.1X EAP) network to configure ID and Certificate.
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QCheckBox, QFileDialog,
                             QMessageBox)
from PyQt6.QtCore import Qt
from core.i18n import I18nManager, LANG_KO


class EnterpriseWifiDialog(QDialog):
    def __init__(self, ssid: str, parent=None):
        super().__init__(parent)
        self.ssid = ssid
        self.ca_cert_path = ""

        is_ko = I18nManager.get_lang() == LANG_KO
        self.setWindowTitle("교내 와이파이 인증 정보 입력" if is_ko else "Enterprise Wi-Fi Authentication")
        self.setFixedWidth(460)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        info_label = QLabel(
            f"<b>네트워크: {ssid}</b><br>"
            + ("교내 보안 와이파이(802.1X EAP)가 감지되었습니다.<br>접속을 위해 아이디와 인증서 설정을 입력해 주세요."
               if is_ko else "Enterprise (802.1X EAP) Wi-Fi detected.<br>Please enter your Identity and Certificate options.")
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # 1. 아이디 (ID / Username)
        r_id = QHBoxLayout()
        lbl_id = QLabel("아이디 (ID):" if is_ko else "Identity (ID):")
        lbl_id.setFixedWidth(110)
        self.edit_id = QLineEdit()
        self.edit_id.setPlaceholderText("사용자 ID 또는 계정명" if is_ko else "Username or ID")
        r_id.addWidget(lbl_id)
        r_id.addWidget(self.edit_id, 1)
        layout.addLayout(r_id)

        # 2. CA 인증서 선택
        r_cert = QHBoxLayout()
        lbl_cert = QLabel("CA 인증서:" if is_ko else "CA Certificate:")
        lbl_cert.setFixedWidth(110)
        self.edit_cert = QLineEdit()
        self.edit_cert.setReadOnly(True)
        self.edit_cert.setPlaceholderText("인증서 파일 (.pem, .crt)" if is_ko else "Certificate (.pem, .crt)")
        self.btn_browse_cert = QPushButton("찾아보기..." if is_ko else "Browse...")
        self.btn_browse_cert.clicked.connect(self.browse_cert)

        r_cert.addWidget(lbl_cert)
        r_cert.addWidget(self.edit_cert, 1)
        r_cert.addWidget(self.btn_browse_cert)
        layout.addLayout(r_cert)

        # 인증서 미검증 옵션 (일반적인 기업/기관망 기본 설정)
        self.chk_no_cert = QCheckBox("인증서 검증 안 함 (권장)" if is_ko else "Do not validate CA certificate (Recommended)")
        self.chk_no_cert.setChecked(True)
        self.chk_no_cert.toggled.connect(self.toggle_cert_mode)
        layout.addWidget(self.chk_no_cert)
        self.toggle_cert_mode(True)

        # 하단 확인/취소 버튼
        r_btns = QHBoxLayout()
        r_btns.addStretch()
        self.btn_cancel = QPushButton("취소" if is_ko else "Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_connect = QPushButton("연결 확인" if is_ko else "Confirm Connect")
        self.btn_connect.setStyleSheet("background-color: #007ACC; color: white; font-weight: bold; padding: 6px 14px;")
        self.btn_connect.clicked.connect(self.on_confirm_clicked)

        r_btns.addWidget(self.btn_cancel)
        r_btns.addWidget(self.btn_connect)
        layout.addLayout(r_btns)

    def toggle_cert_mode(self, checked: bool):
        self.edit_cert.setEnabled(not checked)
        self.btn_browse_cert.setEnabled(not checked)
        if checked:
            self.edit_cert.clear()
            self.ca_cert_path = ""

    def browse_cert(self):
        is_ko = I18nManager.get_lang() == LANG_KO
        path, _ = QFileDialog.getOpenFileName(
            self,
            "CA 인증서 파일 선택" if is_ko else "Select CA Certificate File",
            "",
            "인증서 파일 (*.pem *.crt *.cer);;모든 파일 (*.*)"
        )
        if path:
            self.ca_cert_path = path
            self.edit_cert.setText(path)

    def on_confirm_clicked(self):
        is_ko = I18nManager.get_lang() == LANG_KO
        ident = self.edit_id.text().strip()

        if not ident:
            QMessageBox.warning(
                self,
                "아이디 필요" if is_ko else "ID Required",
                "엔터프라이즈 와이파이 접속을 위한 아이디(계정명)를 입력해 주세요." if is_ko else "Please enter your identity/username."
            )
            return

        if not self.chk_no_cert.isChecked() and not self.ca_cert_path:
            QMessageBox.warning(
                self,
                "인증서 선택 필요" if is_ko else "Certificate Required",
                "인증서 파일을 선택하거나 '인증서 검증 안 함'에 체크해 주세요." if is_ko else "Select a CA certificate or check 'Do not validate'."
            )
            return

        self.accept()

    def get_identity(self):
        return self.edit_id.text().strip()

    def get_cert_options(self):
        ca_content = ""
        if not self.chk_no_cert.isChecked() and self.ca_cert_path:
            try:
                with open(self.ca_cert_path, "r", encoding="utf-8") as f:
                    ca_content = f.read()
            except Exception:
                pass
        return {
            "no_validate": self.chk_no_cert.isChecked(),
            "ca_cert": ca_content
        }
