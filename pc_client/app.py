# -*- coding: utf-8 -*-
"""
10D FCD - Application Entry Point (PyQt6)
Onedir + Inno Setup 배포 최적화 (단일 인스턴스 락, DPI 인식, 사용자 데이터 관리)
"""
import sys
import os
import ctypes
import multiprocessing
from pathlib import Path

# 소스코드 실행 시 현재 디렉터리를 sys.path에 추가하여 내부 모듈 임포트 보장
_CURRENT_DIR = str(Path(__file__).resolve().parent)
if _CURRENT_DIR not in sys.path:
    sys.path.insert(0, _CURRENT_DIR)

from PyQt6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon
from PyQt6.QtCore import QSharedMemory
from PyQt6.QtGui import QFont, QIcon

from config import APP_NAME, APP_VERSION, APP_ID, USER_DATA_DIR, get_resource_path
from core.i18n import I18nManager, LANG_KO
from ui.main_window import MainWindow
from ui.styles import MODERN_STYLE_SHEET


def main():
    multiprocessing.freeze_support()

    # 윈도우 작업 표시줄 아이콘 분리 방지 (고유 AppUserModelID 등록)
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
    except Exception:
        pass

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setStyleSheet(MODERN_STYLE_SHEET)

    # 앱 아이콘 설정 (assets 폴더 내 아이콘 존재 시)
    icon_path = get_resource_path("assets/icon.png")
    if not icon_path.exists():
        icon_path = get_resource_path("assets/icon.ico")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # 1. 단일 인스턴스 보호 (중복 실행 방지)
    shared_memory = QSharedMemory(APP_ID)
    if not shared_memory.create(1):
        QMessageBox.warning(
            None,
            APP_NAME,
            f"{APP_NAME} 프로그램이 이미 실행 중입니다.\n작업 표시줄 또는 시스템 트레이를 확인해 주세요."
        )
        sys.exit(0)

    # 2. 고해상도 가독성을 위한 시스템 폰트 설정 (넉넉한 가독성 유지)
    font = QFont("Segoe UI", 11)
    app.setFont(font)

    # 3. 메인 윈도우 생성
    window = MainWindow()

    # 시작 시 최소화 옵션 확인
    st = window.card_settings.get_settings()
    if st.get("start_minimized", False):
        window.hide()
        if hasattr(window, "tray_icon") and window.tray_icon and window.tray_icon.isVisible():
            is_ko = I18nManager.get_lang() == LANG_KO
            window.tray_icon.showMessage(
                APP_NAME,
                "10D FCD가 시스템 트레이(백그라운드)에서 시작되었습니다.\n아이콘을 클릭하면 제어 창이 열립니다."
                if is_ko else f"{APP_NAME} started minimized in system tray.\nClick icon to open.",
                QSystemTrayIcon.MessageIcon.Information,
                3000
            )
    else:
        window.show()

    exit_code = app.exec()

    # 종료 시 공유 메모리 정리
    shared_memory.detach()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
