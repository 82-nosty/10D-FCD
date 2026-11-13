# -*- coding: utf-8 -*-
"""
Main Commercial Window - 10D FCD (Fan Cooler Display)
3-Column Layout: Left Sidebar Navigation | Center Tabbed Pages | Right Live Cooler LCD Stage
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                             QPushButton, QLabel, QFrame, QStackedWidget,
                             QButtonGroup, QSizePolicy, QMessageBox, QApplication,
                             QSystemTrayIcon, QMenu, QScrollArea)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, QTimer

from config import APP_NAME, APP_VERSION, DEFAULT_TCP_PORT, USER_DATA_DIR, BASE_DIR
from core.i18n import I18nManager, LANG_KO, LANG_EN
from core.serial_manager import SerialManager
from core.media_manager import MediaManager
from core.network_manager import StreamWorker
from core.settings_manager import SettingsManager
from core.theme_engine import ThemeEngine
from renderer.overlay_engine import OverlayEngine

from ui.components.preview_widget import PreviewWidget
from ui.components.connection_card import ConnectionCard
from ui.components.media_card import MediaCard
from ui.components.overlay_card import OverlayCard
from ui.components.log_widget import LogWidget
from ui.components.settings_card import SettingsCard
from ui.components.community_card import ThemeCommunityCard
from ui.components.theme_editor_card import ThemeEditorCard


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.resize(1120, 720)
        self.setMinimumSize(1020, 660)

        self.serial_manager = SerialManager()
        self.media_manager = MediaManager()
        self.overlay_engine = OverlayEngine()
        self.theme_engine = ThemeEngine(BASE_DIR / "themes")
        self.theme_engine.load_theme("design1_classic")
        self.worker = None

        self.setup_ui()
        self.connect_signals()
        self.load_saved_settings()
        self.retranslate_ui()
        self.setup_tray()

        # 이전 연결 기록이 있으면 프로그램 시작 0.8초 후 자동 연결 시도
        QTimer.singleShot(800, self.auto_connect_on_startup)

        # 외부(펌웨어 업로더 등)에서 종료 요청 시 안전하게 ESP 통신 해제 후 자동 종료하는 워처
        self._shutdown_flag = USER_DATA_DIR / "shutdown.flag"
        if self._shutdown_flag.exists():
            try:
                self._shutdown_flag.unlink()
            except Exception:
                pass
        self._shutdown_timer = QTimer(self)
        self._shutdown_timer.timeout.connect(self._check_shutdown_flag)
        self._shutdown_timer.start(500)

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # =====================================================================
        # 1. [좌측] 사이드바 네비게이션 (210px 고정)
        # =====================================================================
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(235)
        sb_layout = QVBoxLayout(self.sidebar)
        sb_layout.setContentsMargins(0, 22, 0, 18)
        sb_layout.setSpacing(4)

        # 브랜드 헤더
        brand_box = QWidget()
        brand_layout = QVBoxLayout(brand_box)
        brand_layout.setContentsMargins(20, 0, 16, 18)
        brand_layout.setSpacing(2)

        self.lbl_brand = QLabel(APP_NAME)
        self.lbl_brand.setObjectName("BrandTitle")
        self.lbl_sub = QLabel(f"Fan Cooler Display · v{APP_VERSION}")
        self.lbl_sub.setObjectName("BrandSubtitle")
        brand_layout.addWidget(self.lbl_brand)
        brand_layout.addWidget(self.lbl_sub)
        sb_layout.addWidget(brand_box)

        # 네비게이션 탭 버튼 그룹
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        self.btn_nav_media = self._create_nav_button(0)
        self.btn_nav_hud = self._create_nav_button(1)
        self.btn_nav_community = self._create_nav_button(2)
        self.btn_nav_editor = self._create_nav_button(3)
        self.btn_nav_conn = self._create_nav_button(4)
        self.btn_nav_console = self._create_nav_button(5)
        self.btn_nav_settings = self._create_nav_button(6)

        sb_layout.addWidget(self.btn_nav_media)
        sb_layout.addWidget(self.btn_nav_hud)
        sb_layout.addWidget(self.btn_nav_community)
        sb_layout.addWidget(self.btn_nav_editor)
        sb_layout.addWidget(self.btn_nav_conn)
        sb_layout.addWidget(self.btn_nav_console)
        sb_layout.addWidget(self.btn_nav_settings)
        sb_layout.addStretch()

        # 하단 상태 배지 & 언어 토글
        bottom_box = QWidget()
        bottom_layout = QVBoxLayout(bottom_box)
        bottom_layout.setContentsMargins(16, 0, 16, 0)
        bottom_layout.setSpacing(10)

        self.lbl_serial_badge = QLabel()
        self.lbl_serial_badge.setStyleSheet(
            "color: #64748B; font-size: 13px; font-weight: 600; padding: 7px 10px; "
            "background-color: #12151D; border-radius: 6px;"
        )
        bottom_layout.addWidget(self.lbl_serial_badge)

        self.btn_lang_toggle = QPushButton()
        self.btn_lang_toggle.setObjectName("LangButton")
        self.btn_lang_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_lang_toggle.clicked.connect(self.toggle_language)
        bottom_layout.addWidget(self.btn_lang_toggle)

        sb_layout.addWidget(bottom_box)
        root_layout.addWidget(self.sidebar)

        # =====================================================================
        # 2. [중앙] 탭별 페이지 워크스페이스 (QStackedWidget)
        # =====================================================================
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(28, 24, 28, 24)
        center_layout.setSpacing(16)

        # 페이지 상단 타이틀 + 설명 헤더
        self.lbl_page_title = QLabel()
        self.lbl_page_title.setObjectName("PageTitle")
        self.lbl_page_desc = QLabel()
        self.lbl_page_desc.setObjectName("PageDesc")
        self.lbl_page_desc.setWordWrap(True)

        center_layout.addWidget(self.lbl_page_title)
        center_layout.addWidget(self.lbl_page_desc)

        # 스택 위젯 (7개 탭 페이지)
        self.stack = QStackedWidget()

        # Page 0: 디스플레이 & 미디어
        self.card_media = MediaCard(self.media_manager)
        page_media = self._wrap_page(self.card_media)
        self.stack.addWidget(page_media)

        # Page 1: HUD & 성능 튜닝
        self.card_overlay = OverlayCard()
        page_hud = self._wrap_page(self.card_overlay)
        self.stack.addWidget(page_hud)

        # Page 2: 테마 커뮤니티 & 프리셋
        self.card_community = ThemeCommunityCard(self.theme_engine)
        self.card_community.theme_selected.connect(self.on_theme_changed)
        page_community = self._wrap_page(self.card_community)
        self.stack.addWidget(page_community)

        # Page 3: 테마 에디터 & 스튜디오 (Beta)
        self.card_editor = ThemeEditorCard()
        page_editor = self._wrap_page(self.card_editor)
        self.stack.addWidget(page_editor)

        # Page 4: 장치 연결 & Wi-Fi
        self.card_conn = ConnectionCard(self.serial_manager)
        page_conn = self._wrap_page(self.card_conn)
        self.stack.addWidget(page_conn)

        # Page 5: 시스템 콘솔
        self.log_widget = LogWidget()
        page_console = QWidget()
        pc_layout = QVBoxLayout(page_console)
        pc_layout.setContentsMargins(0, 4, 0, 0)
        pc_layout.addWidget(self.log_widget)
        self.stack.addWidget(page_console)

        # Page 6: 시스템 및 고급 설정 (상용 소프트웨어 급)
        self.card_settings = SettingsCard()
        self.card_settings.settings_changed.connect(self._on_settings_changed)
        self.card_settings.reset_requested.connect(self.reset_all_settings)
        page_settings = self._wrap_page(self.card_settings)
        self.stack.addWidget(page_settings)

        center_layout.addWidget(self.stack, 1)
        root_layout.addWidget(center_panel, 1)

        # =====================================================================
        # 3. [우측] 고정 쿨러 LCD 라이브 프리뷰 스테이지 (325px 고정)
        # =====================================================================
        self.preview_stage = QFrame()
        self.preview_stage.setObjectName("PreviewStage")
        self.preview_stage.setFixedWidth(325)
        pv_layout = QVBoxLayout(self.preview_stage)
        pv_layout.setContentsMargins(22, 24, 22, 24)
        pv_layout.setSpacing(14)

        self.lbl_pv_title = QLabel()
        self.lbl_pv_title.setStyleSheet(
            "font-size: 14px; font-weight: 800; color: #38BDF8; letter-spacing: 1.5px;"
        )
        self.lbl_pv_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pv_layout.addWidget(self.lbl_pv_title)

        pv_layout.addStretch()

        self.preview_widget = PreviewWidget()
        pv_layout.addWidget(self.preview_widget)

        # 텔레메트리 상태 배지
        self.lbl_stream_stat = QLabel()
        self.lbl_stream_stat.setStyleSheet(
            "color: #10B981; font-size: 13px; font-weight: 600; "
            "background-color: #141820; border: 1px solid #222936; "
            "border-radius: 6px; padding: 8px 10px;"
        )
        self.lbl_stream_stat.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pv_layout.addWidget(self.lbl_stream_stat)

        pv_layout.addStretch()

        # 마스터 스트리밍 컨트롤 버튼
        self.btn_toggle_stream = QPushButton()
        self.btn_toggle_stream.setObjectName("PrimaryButton")
        self.btn_toggle_stream.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_stream.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_toggle_stream.clicked.connect(self.toggle_stream)
        pv_layout.addWidget(self.btn_toggle_stream)

        root_layout.addWidget(self.preview_stage)

        # 기본 탭: 디스플레이 & 미디어 (0번) 선택
        self.btn_nav_media.setChecked(True)
        self.switch_page(0)

    def _create_nav_button(self, index: int) -> QPushButton:
        btn = QPushButton()
        btn.setObjectName("NavButton")
        btn.setCheckable(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(lambda: self.switch_page(index))
        self.nav_group.addButton(btn, index)
        return btn

    def _wrap_page(self, widget: QWidget) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 4, 8, 10)
        layout.setSpacing(14)
        layout.addWidget(widget)
        layout.addStretch()

        scroll.setWidget(container)
        return scroll

    def switch_page(self, index: int):
        # Index 3: 테마 에디터 (아직 개발 중 -> 팝업 후 접근 차단)
        if index == 3:
            is_ko = I18nManager.get_lang() == LANG_KO
            QMessageBox.information(
                self,
                "기능 개발 중" if is_ko else "Under Development",
                "현재 비주얼 테마 에디터(Theme Studio) 기능은 개발 중입니다.\n\n추후 정식 업데이트를 통해 드래그앤드롭 커스텀 편집기가 제공될 예정입니다.\n(테마 제작은 themes/THEME_GUIDE.md 규격을 참조해 주세요.)"
                if is_ko else "The Visual Theme Studio is currently under development.\nIt will be available in a future update.\n(Refer to themes/THEME_GUIDE.md for manual authoring.)"
            )
            # 이전 활성 버튼 체크 상태 유지
            cur_idx = self.stack.currentIndex()
            btn = self.nav_group.button(cur_idx)
            if btn:
                btn.setChecked(True)
            return

        self.stack.setCurrentIndex(index)
        self._update_page_header()

    def _update_page_header(self):
        t = I18nManager.t
        idx = self.stack.currentIndex()
        headers = [
            ("page_media_title", "page_media_desc"),
            ("page_hud_title", "page_hud_desc"),
            ("page_community_title", "page_community_desc"),
            ("page_editor_title", "page_editor_desc"),
            ("page_conn_title", "page_conn_desc"),
            ("page_console_title", "page_console_desc"),
            ("page_settings_title", "page_settings_desc"),
        ]
        title_key, desc_key = headers[idx]
        self.lbl_page_title.setText(t(title_key))
        self.lbl_page_desc.setText(t(desc_key))

    def connect_signals(self):
        self.serial_manager.log_signal.connect(self.log_widget.log)
        self.card_conn.serial_status_changed.connect(self.on_serial_status_changed)
        self.card_conn.ip_updated_signal.connect(lambda _: self.save_current_settings())
        self.card_conn.before_send_wifi_signal.connect(self._on_before_send_wifi)
        self.card_overlay.settings_changed.connect(self.sync_live_settings)
        self.card_media.rb_demo.toggled.connect(self.sync_live_settings)
        self.card_media.rb_file.toggled.connect(self.sync_live_settings)
        self.card_media.rb_screen.toggled.connect(self.sync_live_settings)
        self.card_settings.btn_refresh_wifi.clicked.connect(self.serial_manager.query_wifi_profiles)
        self.card_settings.btn_del_wifi.clicked.connect(self.on_delete_wifi_profile)
        self.serial_manager.wifi_profiles_signal.connect(self.card_settings.update_wifi_profiles)
        self.log_widget.log("10D FCD ready.", "10D FCD 쿨러 제어 시스템이 준비되었습니다.")

    def on_delete_wifi_profile(self):
        ssid = self.card_settings.get_selected_wifi_ssid()
        is_ko = I18nManager.get_lang() == LANG_KO
        if not ssid:
            QMessageBox.information(
                self,
                "선택 필요" if is_ko else "Selection Required",
                "삭제할 Wi-Fi 네트워크를 목록에서 선택해 주세요." if is_ko else "Please select a Wi-Fi profile from the list."
            )
            return

        ret = QMessageBox.question(
            self,
            "Wi-Fi 삭제 확인" if is_ko else "Confirm Delete",
            f"기기에서 [{ssid}] 네트워크 프로필을 삭제하시겠습니까?" if is_ko else f"Delete [{ssid}] from ESP32?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if ret == QMessageBox.StandardButton.Yes:
            self.serial_manager.delete_wifi_profile(ssid)

    def sync_live_settings(self):
        """스트리밍 중에도 위젯 토글/모드/FPS/화질 변경을 즉시 반영"""
        if self.worker and self.worker.isRunning():
            new_settings = self.card_overlay.get_settings()
            new_settings["mode"] = self.card_media.get_mode()
            self.worker.settings.update(new_settings)
            self.worker.notify_settings_changed()

    def load_saved_settings(self):
        cfg = SettingsManager.load()
        I18nManager.set_lang(cfg.get("lang", LANG_KO))
        self.card_conn.apply_settings(cfg)
        self.card_media.apply_settings(cfg)
        self.card_overlay.apply_settings(cfg)
        self.card_settings.apply_settings(cfg)
        tid = cfg.get("theme_id", "design1_classic")
        self.theme_engine.load_theme(tid)
        self.card_community.active_theme_id = tid
        self.card_community.populate_themes()

    def _on_before_send_wifi(self):
        """공유기 재설정 전 실행 중인 스트리밍을 안전하게 일시 정지하여 소켓 충돌 및 멈춤 방지"""
        if self.worker and self.worker.isRunning():
            self.log_widget.log(
                "Stopping wireless stream before Wi-Fi configuration...",
                "공유기 재연결을 위해 무선 스트리밍을 안전하게 일시 중지합니다."
            )
            self.toggle_stream(silent=True)

    def auto_connect_on_startup(self):
        """프로그램 시작 시 이전 연결 기록(IP 또는 COM 포트)이 있으면 자동 연결"""
        target_ip = self.card_conn.get_target_ip().strip()
        port = self.card_conn.get_selected_port().strip()

        # 1. 시리얼 포트 연결 기록이 있으면 시리얼 연결
        if port and not self.serial_manager.is_connected():
            if hasattr(self.card_conn, "btn_port_conn"):
                self.card_conn.btn_port_conn.click()

        # 2. 유효한 IP가 있는 경우에만 백그라운드 조용한 자동 연결 시도 (에러 팝업 없음!)
        if target_ip and target_ip != "0.0.0.0" and not (self.worker and self.worker.isRunning()):
            self.log_widget.log(
                f"Auto-connecting to saved target {target_ip}...",
                f"이전 연결 기록({target_ip})을 감지하여 자동 스트리밍을 시작합니다..."
            )
            self.toggle_stream(silent=True)
        else:
            # 신규 사용자이거나 아직 Wi-Fi가 설정되지 않은 경우 부드러운 온보딩 안내
            self.log_widget.log(
                "Welcome to 10D FCD! Please configure Wi-Fi in the [Device & Wi-Fi] tab.",
                "10D FCD에 오신 것을 환영합니다! [장치 연결 & Wi-Fi] 탭에서 기기를 연결해 주세요."
            )

    def _on_settings_changed(self):
        self.save_current_settings()
        st = self.card_settings.get_settings()
        flip = st.get("flip_180", False)
        # 1. 시리얼 연결 상태면 즉시 기기 NVS로 전송
        if self.serial_manager.is_connected():
            self.serial_manager.set_device_flip(flip)
        # 2. Wi-Fi 스트리밍 연결 상태면 실시간 TCP VCMD로 전송
        if self.worker and self.worker.isRunning():
            self.worker.send_command(f"FLIP:{1 if flip else 0}")

    def save_current_settings(self):
        ov = self.card_overlay.get_settings()
        st = self.card_settings.get_settings()
        wifi_ssid, wifi_pw = self.card_conn.get_wifi_credentials()
        data = {
            "lang": I18nManager.get_lang(),
            "com_port": self.card_conn.get_selected_port(),
            "target_ip": self.card_conn.get_target_ip(),
            "wifi_ssid": wifi_ssid,
            "wifi_pw": wifi_pw,
            "media_mode": self.card_media.get_mode(),
            "media_path": self.card_media.get_media_path(),
            "hud_on_media": self.card_media.get_hud_on_media(),
            "theme_id": getattr(self.card_community, "active_theme_id", "design1_classic"),
            "show_cpu": ov["show_cpu"],
            "show_ram": ov["show_ram"],
            "show_time": ov["show_time"],
            "show_fps": ov["show_fps"],
            "fps": ov["fps"],
            "quality": ov["quality"],
            "hud_alpha": ov.get("hud_alpha", 190),
            "autostart": st["autostart"],
            "min_to_tray": st["min_to_tray"],
            "start_minimized": st["start_minimized"],
            "flip_180": st.get("flip_180", False),
        }
        SettingsManager.save(data)

    def reset_all_settings(self):
        """모든 설정값을 공장 초기화하고 UI를 리셋"""
        data = {
            "lang": LANG_KO,
            "com_port": "",
            "target_ip": "",
            "wifi_ssid": "",
            "wifi_pw": "",
            "media_mode": "DEMO",
            "media_path": "",
            "hud_on_media": False,
            "show_cpu": True,
            "show_ram": True,
            "show_time": True,
            "show_fps": True,
            "fps": 20,
            "quality": 90,
            "autostart": False,
            "min_to_tray": True,
            "start_minimized": False
        }
        SettingsManager.save(data)
        self.load_saved_settings()
        self.retranslate_ui()
        self.log_widget.log("All settings reset to defaults.", "모든 설정이 초기값으로 재설정되었습니다.")

    def on_serial_status_changed(self, connected: bool):
        t = I18nManager.t
        if connected:
            self.lbl_serial_badge.setText(t("badge_serial_on"))
            self.lbl_serial_badge.setStyleSheet(
                "color: #10B981; font-size: 13px; font-weight: 700; padding: 7px 10px; "
                "background-color: #0D231C; border: 1px solid #10B981; border-radius: 6px;"
            )
            # 시리얼 연결 즉시 기기 NVS로 회전 및 언어 설정 자동 동기화
            flip = self.card_settings.get_settings().get("flip_180", False)
            self.serial_manager.set_device_flip(flip)
            self.serial_manager.set_device_language(I18nManager.get_lang())
            self.serial_manager.sync_device_time()
            self.serial_manager.query_wifi_profiles()
        else:
            self.lbl_serial_badge.setText(t("badge_serial_off"))
            self.lbl_serial_badge.setStyleSheet(
                "color: #64748B; font-size: 13px; font-weight: 600; padding: 7px 10px; "
                "background-color: #12151D; border-radius: 6px;"
            )

    def toggle_language(self):
        cur = I18nManager.get_lang()
        new_lang = LANG_EN if cur == LANG_KO else LANG_KO
        I18nManager.set_lang(new_lang)

        self.retranslate_ui()
        self.save_current_settings()

        if self.serial_manager.is_connected():
            self.serial_manager.set_device_language(new_lang)

    def retranslate_ui(self):
        t = I18nManager.t
        self.btn_nav_media.setText(f"  🎨   {t('nav_media')}")
        self.btn_nav_hud.setText(f"  📊   {t('nav_hud')}")
        self.btn_nav_community.setText(f"  🌐   {t('nav_community')}")
        self.btn_nav_editor.setText(f"  🛠️   {t('nav_editor')}")
        self.btn_nav_conn.setText(f"  📡   {t('nav_conn')}")
        self.btn_nav_console.setText(f"  🖥️   {t('nav_console')}")
        self.btn_nav_settings.setText(f"  ⚙️   {t('nav_settings')}")

        self.card_conn.retranslate()
        self.card_media.retranslate()
        self.card_overlay.retranslate()
        self.card_community.retranslate()
        self.card_editor.retranslate()
        self.card_settings.retranslate()

        self.btn_lang_toggle.setText(t("lang_switch_btn"))
        self.lbl_pv_title.setText(t("preview_title"))
        self._update_page_header()
        self.on_serial_status_changed(self.serial_manager.is_connected())

        if not (self.worker and self.worker.isRunning()):
            self.btn_toggle_stream.setText(t("start_stream"))
            self.lbl_stream_stat.setText(t("stat_standby"))
            self.preview_widget.set_blank()
        else:
            self.btn_toggle_stream.setText(t("stop_stream"))

    def toggle_stream(self, silent: bool = False):
        t = I18nManager.t
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.btn_toggle_stream.setText(t("start_stream"))
            self.btn_toggle_stream.setObjectName("PrimaryButton")
            self.btn_toggle_stream.style().unpolish(self.btn_toggle_stream)
            self.btn_toggle_stream.style().polish(self.btn_toggle_stream)
            return

        ip = self.card_conn.get_target_ip()
        if not ip or ip == "0.0.0.0":
            self.log_widget.log("Target IP required.", "쿨러 기기 IP 주소가 유효하지 않습니다.")
            if not silent:
                self.btn_nav_conn.setChecked(True)
                self.switch_page(4)
                QMessageBox.warning(self, t("conn_err_title"), t("conn_err_no_ip"))
            return

        settings = self.card_overlay.get_settings()
        settings["mode"] = self.card_media.get_mode()
        settings["hud_on_media"] = self.card_media.get_hud_on_media()
        settings["flip_180"] = self.card_settings.get_settings().get("flip_180", False)

        self.worker = StreamWorker(
            ip=ip,
            port=DEFAULT_TCP_PORT,
            media_manager=self.media_manager,
            overlay_engine=self.overlay_engine,
            settings=settings,
            theme_engine=self.theme_engine
        )
        self.worker.log_signal.connect(self.log_widget.log)
        self.worker.stat_signal.connect(self.on_stat_update)
        self.worker.frame_preview_signal.connect(self.preview_widget.update_frame)
        self.worker.connect_failed_signal.connect(lambda err: self.on_connect_failed(ip, err, silent=silent))
        self.worker.stopped_signal.connect(self.on_stream_stopped)

        self.worker.start()
        self.btn_toggle_stream.setText(t("stop_stream"))
        self.btn_toggle_stream.setObjectName("StopButton")
        self.btn_toggle_stream.style().unpolish(self.btn_toggle_stream)
        self.btn_toggle_stream.style().polish(self.btn_toggle_stream)

    def on_connect_failed(self, ip: str, err: str, silent: bool = False):
        t = I18nManager.t
        if not silent:
            self.btn_nav_conn.setChecked(True)
            self.switch_page(4)
            msg = t("conn_err_unreachable").format(ip=ip, port=DEFAULT_TCP_PORT, err=err)
            QMessageBox.warning(self, t("conn_err_title"), msg)
        else:
            self.log_widget.log(
                f"Cannot reach saved target ({ip}). Standby mode.",
                f"저장된 기기({ip})에 연결할 수 없습니다. 쿨러 전원 및 공유기 연결을 확인해 주세요."
            )

    def on_stat_update(self, fps, kbps):
        t = I18nManager.t
        self.lbl_stream_stat.setText(f"{t('stat_streaming')}  |  {fps:4.1f} FPS  |  {kbps:5.1f} KB/s")

    def on_theme_changed(self, theme_id: str):
        self.save_current_settings()
        theme_name = self.theme_engine.current_theme.get("name_ko", theme_id) if I18nManager.get_lang() == LANG_KO else self.theme_engine.current_theme.get("name", theme_id)
        self.log_widget.log(f"Theme applied: {theme_id}", f"새 디자인 테마 [{theme_name}]가 적용되었습니다.")
        if self.worker and self.worker.isRunning():
            self.worker.notify_settings_changed()

    def on_stream_stopped(self):
        t = I18nManager.t
        self.btn_toggle_stream.setText(t("start_stream"))
        self.btn_toggle_stream.setObjectName("PrimaryButton")
        self.btn_toggle_stream.style().unpolish(self.btn_toggle_stream)
        self.btn_toggle_stream.style().polish(self.btn_toggle_stream)
        self.lbl_stream_stat.setText(t("stat_standby"))
        self.preview_widget.set_blank()

    def _check_shutdown_flag(self):
        if self._shutdown_flag.exists():
            try:
                self._shutdown_flag.unlink()
            except Exception:
                pass
            self.close()
            QApplication.quit()

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip(f"{APP_NAME} v{APP_VERSION}")
        self.tray_icon.setIcon(self.windowIcon())

        tray_menu = QMenu()
        act_show = QAction("열기 (Open)", self)
        act_show.triggered.connect(self.show_and_activate)
        tray_menu.addAction(act_show)

        tray_menu.addSeparator()

        act_exit = QAction("완전 종료 (Exit)", self)
        act_exit.triggered.connect(self.force_quit)
        tray_menu.addAction(act_exit)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show_and_activate()

    def show_and_activate(self):
        self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
        self.activateWindow()

    def force_quit(self):
        self._is_force_quit = True
        self.save_current_settings()
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(1500)
        if self.serial_manager.is_connected():
            self.serial_manager.disconnect_port()
        QApplication.quit()

    def closeEvent(self, event):
        """창 종료(X) 시: 트레이 최소화 설정 여부에 따라 트레이 숨김 또는 완전 종료"""
        if getattr(self, "_is_force_quit", False):
            event.accept()
            return

        st = self.card_settings.get_settings()
        if st.get("min_to_tray", True):
            event.ignore()
            self.hide()
            if self.tray_icon and self.tray_icon.isVisible():
                self.tray_icon.showMessage(
                    APP_NAME,
                    "백그라운드에서 계속 실행 중입니다. 트레이 아이콘을 클릭하면 다시 열립니다."
                    if I18nManager.get_lang() == LANG_KO else "Running in background. Click tray icon to restore.",
                    QSystemTrayIcon.MessageIcon.Information,
                    2000
                )
        else:
            self.force_quit()
            event.accept()
