# -*- coding: utf-8 -*-
"""
10D FCD - Modern Commercial Dark Theme QSS Stylesheet (PyQt6)
"""
from config import get_resource_path

_ARROW_PATH = get_resource_path("assets/arrow_down.png").as_posix()

MODERN_STYLE_SHEET = """
QMainWindow {
    background-color: #111318;
}

QWidget {
    color: #E2E8F0;
    font-family: 'Segoe UI', 'Pretendard', 'Malgun Gothic', sans-serif;
    font-size: 15px;
}

/* ======================== 좌측 사이드바 ======================== */
QFrame#Sidebar {
    background-color: #0B0D11;
    border-right: 1px solid #1E232E;
}

QLabel#BrandTitle {
    font-size: 26px;
    font-weight: 800;
    color: #00E5FF;
    letter-spacing: 1px;
}

QLabel#BrandSubtitle {
    font-size: 13px;
    color: #64748B;
    font-weight: 600;
}

QPushButton#NavButton {
    background-color: transparent;
    border: none;
    border-left: 3px solid transparent;
    border-radius: 0px;
    text-align: left;
    padding: 14px 16px;
    color: #94A3B8;
    font-size: 15px;
    font-weight: 600;
}

QPushButton#NavButton:hover {
    background-color: #151922;
    color: #F8FAFC;
}

QPushButton#NavButton:checked {
    background-color: #161C28;
    border-left: 3px solid #00E5FF;
    color: #00E5FF;
}

QPushButton#LangButton {
    background-color: #151922;
    border: 1px solid #262C3A;
    border-radius: 8px;
    padding: 9px 12px;
    color: #E2E8F0;
    font-weight: 600;
}

QPushButton#LangButton:hover {
    background-color: #1E2432;
    border-color: #00E5FF;
}

/* ======================== 우측 프리뷰 스테이지 ======================== */
QFrame#PreviewStage {
    background-color: #0E1015;
    border-left: 1px solid #1E232E;
}

QFrame#CoolerBezel {
    background-color: #050608;
    border: 2px solid #252B38;
    border-radius: 18px;
}

/* ======================== 메인 컨텐츠 페이지 ======================== */
QLabel#PageTitle {
    font-size: 24px;
    font-weight: 700;
    color: #F8FAFC;
}

QLabel#PageDesc {
    font-size: 14px;
    color: #94A3B8;
}

QGroupBox {
    background-color: #161922;
    border: 1px solid #232836;
    border-radius: 10px;
    margin-top: 16px;
    padding: 20px 16px 16px 16px;
    font-weight: 700;
    font-size: 15px;
    color: #38BDF8;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    padding: 0 6px;
    background-color: #161922;
}

/* ======================== 공통 위젯 ======================== */
QPushButton {
    background-color: #1E2330;
    border: 1px solid #2C3344;
    border-radius: 7px;
    padding: 8px 14px;
    min-height: 24px;
    color: #F1F5F9;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #272E3F;
    border-color: #38BDF8;
}

QPushButton:pressed {
    background-color: #171B24;
}

QPushButton:disabled {
    background-color: #141720;
    color: #475569;
    border-color: #1E232E;
}

QPushButton#PrimaryButton {
    background-color: #0284C7;
    border: none;
    border-radius: 9px;
    font-weight: 700;
    padding: 12px 16px;
    min-height: 24px;
    font-size: 16px;
    color: #FFFFFF;
}

QPushButton#PrimaryButton:hover {
    background-color: #0369A1;
}

QPushButton#StopButton {
    background-color: #DC2626;
    border: none;
    border-radius: 9px;
    font-weight: 700;
    padding: 10px 16px;
    min-height: 24px;
    font-size: 15px;
    color: #FFFFFF;
}

QPushButton#StopButton:hover {
    background-color: #B91C1C;
}

QLineEdit, QComboBox {
    background-color: #0F1218;
    border: 1px solid #2A303E;
    border-radius: 7px;
    padding: 7px 10px;
    color: #F8FAFC;
    selection-background-color: #0284C7;
}

QLineEdit:focus, QComboBox:focus {
    border-color: #00E5FF;
}

QLineEdit:read-only {
    background-color: #0B0D12;
    color: #94A3B8;
    border-color: #1E2430;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 32px;
    border-left: 1px solid #2A303E;
    background-color: #1A1F2B;
    border-top-right-radius: 7px;
    border-bottom-right-radius: 7px;
}

QComboBox::down-arrow {
    image: url("__ARROW_PATH__");
    width: 12px;
    height: 12px;
}

QComboBox QAbstractItemView {
    background-color: #161922;
    border: 1px solid #00E5FF;
    border-radius: 6px;
    color: #F8FAFC;
    selection-background-color: #0284C7;
    selection-color: #FFFFFF;
    padding: 4px;
    outline: 0px;
}

QCheckBox, QRadioButton {
    spacing: 10px;
    color: #E2E8F0;
    padding: 4px 0px;
}

QCheckBox::indicator, QRadioButton::indicator {
    width: 17px;
    height: 17px;
    border: 1px solid #3B4457;
    border-radius: 5px;
    background-color: #0F1218;
}

QCheckBox::indicator:checked {
    background-color: #00E5FF;
    border-color: #00E5FF;
}

QRadioButton::indicator {
    border-radius: 9px;
}

QRadioButton::indicator:checked {
    background-color: #00E5FF;
    border-color: #00E5FF;
}

QSlider::groove:horizontal {
    height: 6px;
    background: #1E2430;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: #00E5FF;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #F8FAFC;
    border: 2px solid #00E5FF;
    width: 16px;
    height: 16px;
    margin-top: -6px;
    margin-bottom: -6px;
    border-radius: 9px;
}

QTextEdit {
    background-color: #090B0E;
    border: 1px solid #1E232E;
    border-radius: 8px;
    color: #10B981;
    font-family: 'Consolas', 'D2Coding', monospace;
    font-size: 14px;
    padding: 10px;
}

QScrollBar:vertical {
    background: #111318;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #2C3344;
    border-radius: 4px;
}
""".replace("__ARROW_PATH__", _ARROW_PATH)
