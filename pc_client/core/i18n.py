# -*- coding: utf-8 -*-
"""
10D FCD - Internationalization (i18n) Module
Supports Korean (KO, default) and Global English (EN)
"""

LANG_KO = "KO"
LANG_EN = "EN"

STRINGS = {
    LANG_KO: {
        "app_title": "10D FCD",
        "app_subtitle": "Fan Cooler Display",
        "lang_name": "한국어",
        "lang_switch_btn": "🌐  English",

        # 사이드바 네비게이션 탭
        "nav_media": "디스플레이 & 미디어",
        "nav_hud": "HUD & 성능 튜닝",
        "nav_community": "테마 커뮤니티",
        "nav_editor": "테마 에디터",
        "nav_conn": "장치 연결 & Wi-Fi",
        "nav_console": "시스템 콘솔",
        "nav_settings": "시스템 설정",

        # 페이지 헤더 타이틀 & 서브설명
        "page_media_title": "디스플레이 & 미디어",
        "page_media_desc": "쿨러 상단 LCD에 출력할 애니메이션(GIF), 이미지 또는 인포그래픽 테마를 선택하세요.",
        "page_hud_title": "하드웨어 HUD & 성능 튜닝",
        "page_hud_desc": "화면 위에 띄울 시스템 센서 정보(CPU/RAM/시계)와 무선 전송 화질을 조절합니다.",
        "page_community_title": "테마 커뮤니티 & 프리셋",
        "page_community_desc": "공식 디자인 프리셋 중 원하는 쿨러 레이아웃을 골라 원클릭으로 즉시 적용하세요.",
        "page_editor_title": "테마 에디터 & 스튜디오",
        "page_editor_desc": "변수 토큰과 JSON 엘리먼트를 조합하여 나만의 커스텀 LCD 테마를 개발하세요.",
        "page_conn_title": "장치 연결 & 네트워크 설정",
        "page_conn_desc": "USB 시리얼(COM)로 기기를 연동하고 무선 스트리밍용 와이파이(AP)를 설정합니다.",
        "page_console_title": "시스템 콘솔 & 진단",
        "page_console_desc": "10D FCD 쿨러와 PC 간의 실시간 시리얼/TCP 통신 상태를 확인합니다.",
        "page_settings_title": "시스템 및 설정",
        "page_settings_desc": "윈도우 시작 시 자동 실행, 쿨러 화면 회전, 트레이 아이콘 및 데이터 관리 설정입니다.",
        "settings_flip_sec": "화면 회전",
        "settings_flip_cb": "화면 180도 회전",
        "settings_flip_desc": "",

        # 상태 배지
        "badge_serial_on": "● USB 기기 연결됨",
        "badge_serial_off": "○ USB 연결 안 됨",

        # 1. 포트 & 네트워크 카드
        "card_conn_title": "USB 시리얼 및 무선 네트워크",
        "card_ip_title": "스트리밍 타겟 주소",
        "com_port": "시리얼 포트",
        "refresh_btn": "새로고침",
        "connect_btn": "연결",
        "disconnect_btn": "연결 해제",
        "wifi_ap": "와이파이 AP",
        "scan_btn": "주변 스캔",
        "password": "비밀번호",
        "send_wifi_btn": "공유기 연결",
        "target_ip": "쿨러 기기 IP",

        # 2. 미디어 소스 카드
        "card_media_title": "화면 출력 소스 선택",
        "mode_demo": "10D FCD 모던 인포그래픽 (기본 테마)",
        "mode_file": "고화질 이미지 / GIF / MP4 동영상 파일",
        "mode_screen": "가상 디스플레이 / PC 모니터 미러링 (3:4)",
        "select_file_btn": "파일 찾아보기...",
        "no_file_selected": "선택된 파일 없음 (MP4, GIF, PNG, JPG 지원)",
        "screen_target": "대상 모니터",
        "screen_fit": "비율 맞춤",
        "fit_cover": "3:4 화면 꽉 채우기 (중앙 크롭)",
        "fit_contain": "전체 화면 비율 유지 (레터박스)",
        "vdd_guide_btn": "(?) 가상 모니터 설정 방법",

        # 3. 하드웨어 HUD 및 튜닝
        "card_overlay_title": "실시간 하드웨어 HUD 오버레이",
        "card_tuning_title": "무선 스트리밍 성능 튜닝",
        "hud_on_media": "이미지 / 영상 / 가상 화면 위에도 HUD 위젯 표시",
        "hud_cpu": "CPU 점유율 오버레이 표시",
        "hud_ram": "RAM 점유율 오버레이 표시",
        "hud_time": "디지털 시계 및 날짜 표시",
        "hud_fps": "실시간 전송 FPS 표시",
        "target_fps": "목표 프레임 (FPS)",
        "jpeg_quality": "JPEG 압축 품질",

        # 컨트롤 버튼 및 프리뷰
        "start_stream": "▶  무선 스트리밍 시작",
        "stop_stream": "⏹  스트리밍 중지",
        "preview_title": "LIVE COOLER LCD",
        "stat_standby": "대기 중  |  0.0 FPS  |  0.0 KB/s",
        "stat_streaming": "송출 중",

        # 콘솔 로그 헤더
        "card_log_title": "실시간 통신 로그",

        # 연결 실패 팝업 안내
        "conn_err_title": "쿨러 기기 연결 실패",
        "conn_err_no_ip": "쿨러 기기의 IP 주소가 입력되지 않았거나 유효하지 않습니다.\n\n[장치 연결 & Wi-Fi] 탭에서 USB 케이블을 연결하고 와이파이 설정을 진행하거나, 쿨러 화면에 표시된 IP 주소를 입력해 주세요.",
        "conn_err_unreachable": "쿨러 기기({ip}:{port})에 연결할 수 없습니다.\n\n• 쿨러 전원이 켜져 있고 PC와 같은 와이파이에 연결되어 있는지 확인하세요.\n• 아직 와이파이 설정 전이라면 [장치 연결 & Wi-Fi] 탭에서 USB 연결 후 공유기를 설정해 주세요.\n\n오류 상세: {err}",
    },
    LANG_EN: {
        "app_title": "10D FCD",
        "app_subtitle": "Fan Cooler Display",
        "lang_name": "English",
        "lang_switch_btn": "🌐  한국어 (KO)",

        # Sidebar Navigation Tabs
        "nav_media": "Display & Media",
        "nav_hud": "HUD & Tuning",
        "nav_community": "Theme Community",
        "nav_editor": "Theme Editor",
        "nav_conn": "Device & Wi-Fi",
        "nav_console": "System Console",
        "nav_settings": "Preferences",

        # Page Headers
        "page_media_title": "Display & Media Source",
        "page_media_desc": "Choose GIF animations, custom images, or the modern infographic theme for your cooler LCD.",
        "page_hud_title": "Hardware HUD & Performance",
        "page_hud_desc": "Configure real-time CPU/RAM/Clock overlays and wireless streaming quality.",
        "page_community_title": "Theme Community & Presets",
        "page_community_desc": "Browse and apply distinctive official and community-made cooler LCD themes.",
        "page_editor_title": "Theme Editor & Studio",
        "page_editor_desc": "Design custom cooler themes with dynamic tokens and declarative JSON elements.",
        "page_conn_title": "Device Connection & Network",
        "page_conn_desc": "Connect via USB Serial to scan and configure Wi-Fi credentials on your 10D FCD.",
        "page_console_title": "System Console & Diagnostics",
        "page_console_desc": "Inspect real-time serial and TCP streaming logs between PC and cooler.",
        "page_settings_title": "Preferences",
        "page_settings_desc": "Configure Windows startup, screen rotation, system tray, and data maintenance.",
        "settings_flip_sec": "Display Orientation",
        "settings_flip_cb": "Flip 180°",
        "settings_flip_desc": "",

        # Status Badge
        "badge_serial_on": "● USB Connected",
        "badge_serial_off": "○ USB Offline",

        # 1. Port & Network
        "card_conn_title": "USB Serial & Wi-Fi Provisioning",
        "card_ip_title": "Streaming Target Endpoint",
        "com_port": "Serial Port",
        "refresh_btn": "Refresh",
        "connect_btn": "Connect",
        "disconnect_btn": "Disconnect",
        "wifi_ap": "Wi-Fi AP",
        "scan_btn": "Scan APs",
        "password": "Password",
        "send_wifi_btn": "Apply Wi-Fi",
        "target_ip": "Cooler IP",

        # 2. Media Source
        "card_media_title": "Output Source Mode",
        "mode_demo": "10D FCD Infographic (Built-in)",
        "mode_file": "HD Image / GIF / MP4 Video File",
        "mode_screen": "Virtual Display / Monitor Mirror (3:4)",
        "select_file_btn": "Browse File...",
        "no_file_selected": "No file selected (MP4, GIF, PNG, JPG)",
        "screen_target": "Target Monitor",
        "screen_fit": "Aspect Fit",
        "fit_cover": "Fill 3:4 Screen (Center Crop)",
        "fit_contain": "Fit Entire Screen (Letterbox)",
        "vdd_guide_btn": "(?) How to setup virtual display",

        # 3. Hardware HUD & Tuning
        "card_overlay_title": "Real-Time Hardware HUD Overlays",
        "card_tuning_title": "Wireless Streaming Performance",
        "hud_on_media": "Show HUD Widgets over Media / Virtual Screen",
        "hud_cpu": "Show CPU Load Overlay",
        "hud_ram": "Show RAM Load Overlay",
        "hud_time": "Show Digital Clock & Date",
        "hud_fps": "Show Real-Time FPS",
        "target_fps": "Target Frame Rate",
        "jpeg_quality": "JPEG Quality",

        # Controls & Preview
        "start_stream": "▶  START STREAMING",
        "stop_stream": "⏹  STOP STREAMING",
        "preview_title": "LIVE COOLER LCD",
        "stat_standby": "Standby  |  0.0 FPS  |  0.0 KB/s",
        "stat_streaming": "Streaming",

        # Console Log
        "card_log_title": "Real-Time Communication Log",

        # Connection Error Popup
        "conn_err_title": "Cooler Connection Failed",
        "conn_err_no_ip": "Target cooler IP address is missing or invalid.\n\nPlease connect via USB in the [Device & Wi-Fi] tab to configure Wi-Fi, or enter the IP shown on the cooler LCD.",
        "conn_err_unreachable": "Cannot reach cooler device ({ip}:{port}).\n\n• Ensure the cooler is powered on and connected to the same Wi-Fi network as your PC.\n• If Wi-Fi is not configured yet, connect USB in [Device & Wi-Fi] tab to set up your router.\n\nDetails: {err}",
    }
}

class I18nManager:
    _current_lang = LANG_KO

    @classmethod
    def get_lang(cls):
        return cls._current_lang

    @classmethod
    def set_lang(cls, lang):
        if lang in STRINGS:
            cls._current_lang = lang

    @classmethod
    def t(cls, key):
        return STRINGS.get(cls._current_lang, {}).get(key, key)
