# -*- coding: utf-8 -*-
"""
10D FCD - Global Configuration (Portrait 240x320)
Onedir + Inno Setup 상용 윈도우 인스톨러 배포 최적화 구조
"""
import sys
import os
from pathlib import Path

APP_NAME = "10D FCD"
APP_VERSION = "2.1.8"
APP_ID = "com.10dfcd.coolerdisplay"

# =========================================================================
# 1. 경로 관리: Onedir 배포 & 소스코드 실행 완벽 호환
# =========================================================================
def get_base_path() -> Path:
    """실행 파일(PyInstaller Onedir) 또는 소스코드 루트 디렉터리 반환"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 번들 환경
        return Path(sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.dirname(sys.executable))
    return Path(__file__).resolve().parent

BASE_DIR = get_base_path()

def get_resource_path(relative_path: str) -> Path:
    """에셋/아이콘/폰트 등 읽기 전용 번들 리소스의 절대 경로 반환"""
    return BASE_DIR / relative_path

# =========================================================================
# 2. 사용자 데이터 디렉터리 (%APPDATA%/10D_FCD)
# Program Files에 설치되어도 권한 에러 없이 설정/로그/캐시 영구 보존
# =========================================================================
def get_user_data_dir() -> Path:
    if sys.platform == "win32":
        appdata = os.getenv('APPDATA')
        if appdata:
            data_path = Path(appdata) / "10D_FCD"
        else:
            data_path = Path.home() / ".10D_FCD"
    elif sys.platform == "darwin":
        data_path = Path.home() / "Library" / "Application Support" / "10D_FCD"
    else:
        data_path = Path.home() / ".config" / "10D_FCD"
    data_path.mkdir(parents=True, exist_ok=True)
    return data_path

USER_DATA_DIR = get_user_data_dir()
SETTINGS_FILE = USER_DATA_DIR / "settings.json"
LOG_DIR = USER_DATA_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# =========================================================================
# 3. 하드웨어 스펙 (240x320 Portrait 세로 모드)
# =========================================================================
TARGET_WIDTH = 240
TARGET_HEIGHT = 320
DEFAULT_TCP_PORT = 8888
DEFAULT_SERIAL_BAUD = 921600
MAGIC_HEADER = b'VLIF'

# 스트리밍 기본 파라미터
DEFAULT_TARGET_FPS = 20
DEFAULT_JPEG_QUALITY = 75

# 모던 미니멀 스튜디오 다크 테마 (리얼 블랙 대비 최적화)
COLOR_BG_DARK = "#121316"
COLOR_BG_CARD = "#1A1D24"
COLOR_BG_INPUT = "#222630"
COLOR_ACCENT_BLUE = "#3B82F6"
COLOR_ACCENT_GREEN = "#10B981"
COLOR_ACCENT_RED = "#EF4444"
COLOR_TEXT_PRIMARY = "#FFFFFF"
COLOR_TEXT_SECONDARY = "#94A3B8"
COLOR_BORDER = "#2B303C"
