# -*- coding: utf-8 -*-
"""
10D FCD - Theme Editor Scaffolding Card Component
Provides an interface and reference for authoring custom themes (240x320 Portrait).
"""
import os
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QFrame, QMessageBox, QApplication)
from PyQt6.QtCore import Qt
from core.i18n import I18nManager, LANG_KO


class ThemeEditorCard(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("", parent)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(14, 16, 14, 16)

        # 상단 안내
        self.lbl_head = QLabel()
        self.lbl_head.setStyleSheet("color: #00E5FF; font-weight: 700; font-size: 14px;")
        layout.addWidget(self.lbl_head)

        self.lbl_desc = QLabel()
        self.lbl_desc.setStyleSheet("color: #94A3B8; font-size: 13px;")
        self.lbl_desc.setWordWrap(True)
        layout.addWidget(self.lbl_desc)

        # 컨트롤 툴바 (새 테마 생성, 폴더 열기, 가이드 열기)
        row_btn = QHBoxLayout()
        self.btn_open_folder = QPushButton()
        self.btn_open_folder.clicked.connect(self._open_themes_folder)

        self.btn_open_guide = QPushButton()
        self.btn_open_guide.clicked.connect(self._open_guide_md)

        self.btn_new_theme = QPushButton()
        self.btn_new_theme.setObjectName("PrimaryButton")
        self.btn_new_theme.clicked.connect(self._create_new_theme_stub)

        row_btn.addWidget(self.btn_open_folder)
        row_btn.addWidget(self.btn_open_guide)
        row_btn.addWidget(self.btn_new_theme)
        layout.addLayout(row_btn)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #232836; max-height: 1px;")
        layout.addWidget(line)

        # 변수 토큰 레퍼런스 테이블
        self.lbl_tokens = QLabel()
        self.lbl_tokens.setStyleSheet("color: #F8FAFC; font-weight: 700; font-size: 13px;")
        layout.addWidget(self.lbl_tokens)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["변수 토큰 (Token)", "설명 (Description)", "예시 출력 (Sample)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #12151D;
                border: 1px solid #232836;
                border-radius: 8px;
                gridline-color: #1E293B;
                color: #E2E8F0;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #1A202C;
                color: #00E5FF;
                font-weight: 700;
                padding: 6px;
                border: none;
            }
        """)

        tokens_data = [
            ("%now%", "현재 시각 (24시간 HH:MM)", "14:30"),
            ("%time%", "현재 시각 (24시간 HH:MM:SS)", "14:30:45"),
            ("%hh% / %H%", "현재 시 (24시간 00~23)", "14"),
            ("%h12% / %I%", "현재 시 (12시간 01~12)", "02"),
            ("%MM% / %min%", "현재 분 (00~59)", "30"),
            ("%ss% / %sec%", "현재 초 (00~59)", "45"),
            ("%ampm%", "오전/오후 (AM / PM)", "PM"),
            ("%yyyy%", "현재 연도 4자리", "2026"),
            ("%yy%", "현재 연도 2자리", "26"),
            ("%mm%", "현재 월 2자리 (01~12)", "11"),
            ("%dd%", "현재 일 2자리 (01~31)", "13"),
            ("%date%", "현재 전체 날짜 (YYYY.MM.DD)", "2026.11.13"),
            ("%day_ko%", "한글 요일 (월~일)", "금"),
            ("%day_en%", "영문 요일 (MON~SUN)", "FRI"),
            ("%cpu%", "CPU 실시간 사용률 정수 (%)", "45"),
            ("%cpu_float%", "CPU 실시간 사용률 소수점 (%)", "45.2"),
            ("%cpu_ghz%", "CPU 동작 클럭 (GHz)", "4.20"),
            ("%cpu_mhz%", "CPU 동작 클럭 (MHz)", "4200"),
            ("%cpu_cores%", "CPU 논리 스레드/코어 수", "16"),
            ("%c_sta%", "CPU 요약 문자열 (클럭)", "4.20GHz"),
            ("%ram%", "RAM 실시간 사용률 (%)", "48.0"),
            ("%ram_int%", "RAM 실시간 사용률 정수 (%)", "48"),
            ("%ram_used_gb%", "RAM 사용 용량 (GB)", "15.3GB"),
            ("%ram_total_gb%", "RAM 전체 용량 (GB)", "32.0GB"),
            ("%ram_free_gb%", "RAM 잔여 용량 (GB)", "16.7GB"),
            ("%ram_used_mb%", "RAM 사용 용량 (MB)", "15667"),
            ("%r_sta%", "RAM 요약 문자열 (사용량/전체)", "15.3GB/32.0GB"),
            ("%disk%", "C: 드라이브 사용률 (%)", "62"),
            ("%disk_used_gb%", "C: 드라이브 사용량 (GB)", "250GB"),
            ("%disk_total_gb%", "C: 드라이브 전체 용량 (GB)", "512GB"),
            ("%disk_free_gb%", "C: 드라이브 잔여 용량 (GB)", "262GB"),
            ("%d_sta%", "C: 드라이브 요약 (사용량/전체)", "250GB/512GB"),
            ("%fps%", "무선 스트리밍 전송 FPS", "25.0"),
            ("%hostname%", "PC 시스템 호스트명", "10D-PC"),
            ("%ip%", "PC 로컬 네트워크 IP", "192.168.0.24"),
        ]

        self.table.setRowCount(len(tokens_data))
        for r, row in enumerate(tokens_data):
            for c, val in enumerate(row):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter if c != 1 else Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                if c == 0:
                    item.setForeground(Qt.GlobalColor.cyan)
                self.table.setItem(r, c, item)

        self.table.cellDoubleClicked.connect(self._copy_token)
        layout.addWidget(self.table, 1)

        self.retranslate()

    def retranslate(self):
        is_ko = I18nManager.get_lang() == LANG_KO
        self.setTitle(" 테마 에디터 & 개발자 스튜디오 " if is_ko else " Theme Editor & Studio ")
        self.lbl_head.setText("선언형 쿨러 테마 개발 환경 (Theme Studio)" if is_ko else "Declarative Theme Studio")
        self.lbl_desc.setText(
            "JSON 규격으로 텍스트, 게이지 바, 쿨러 링, 배경 이미지를 자유롭게 배치할 수 있습니다.\n"
            "표의 변수를 더블클릭하면 클립보드에 복사됩니다. 추후 비주얼 드래그앤드롭 편집기가 제공될 예정입니다."
            if is_ko else "Design custom LCD layouts using JSON. Double-click any token to copy to clipboard.\nVisual WYSIWYG editor is scheduled for a future update."
        )
        self.btn_open_folder.setText("테마 폴더 열기" if is_ko else "Open Themes Folder")
        self.btn_open_guide.setText("테마 제작 가이드(MD)" if is_ko else "Open THEME_GUIDE.md")
        self.btn_new_theme.setText("+ 새 테마 템플릿 생성" if is_ko else "+ New Theme Template")
        self.lbl_tokens.setText("실시간 동적 변수 레퍼런스 (Dynamic Tokens)" if is_ko else "Live Dynamic Tokens Reference")

    def _copy_token(self, row, col):
        if col == 0:
            token = self.table.item(row, col).text()
            QApplication.clipboard().setText(token)
            QMessageBox.information(self, "토큰 복사", f"클립보드에 복사되었습니다: {token}")

    def _open_themes_folder(self):
        folder = Path(__file__).resolve().parent.parent.parent / "themes"
        folder.mkdir(parents=True, exist_ok=True)
        try:
            os.startfile(str(folder))
        except Exception:
            subprocess.Popen(["explorer", str(folder)])

    def _open_guide_md(self):
        guide = Path(__file__).resolve().parent.parent.parent / "themes" / "THEME_GUIDE.md"
        if guide.exists():
            try:
                os.startfile(str(guide))
            except Exception:
                subprocess.Popen(["notepad", str(guide)])

    def _create_new_theme_stub(self):
        folder = Path(__file__).resolve().parent.parent.parent / "themes" / "my_custom_theme"
        folder.mkdir(parents=True, exist_ok=True)
        stub_json = folder / "theme.json"
        if not stub_json.exists():
            content = """{
  "name": "My Custom Theme",
  "name_ko": "나만의 커스텀 테마",
  "author": "User",
  "version": "1.0",
  "description": "새로 생성된 사용자 정의 쿨러 테마입니다.",
  "background_color": [10, 15, 25],
  "elements": [
    {
      "type": "text",
      "text": "%now%",
      "x": 120,
      "y": 50,
      "size": 36,
      "color": [0, 229, 255],
      "font": "malgunbd.ttf",
      "anchor": "mm"
    },
    {
      "type": "text",
      "text": "CPU: %cpu%% (%c_sta%)",
      "x": 20,
      "y": 120,
      "size": 13,
      "color": [255, 255, 255],
      "font": "malgunbd.ttf"
    },
    {
      "type": "bar",
      "bind": "cpu",
      "x": 20,
      "y": 145,
      "w": 200,
      "h": 8,
      "radius": 3,
      "bg_color": [28, 34, 46, 255],
      "fill_color": [0, 229, 255, 255]
    }
  ]
}"""
            stub_json.write_text(content, encoding="utf-8")
        is_ko = I18nManager.get_lang() == LANG_KO
        QMessageBox.information(
            self,
            "템플릿 생성 완료" if is_ko else "Template Created",
            f"새 테마 템플릿이 생성되었습니다:\n{folder}\n\ntheme.json을 수정하고 테마 커뮤니티에서 새로고침하세요!"
            if is_ko else f"New template created at:\n{folder}\nEdit theme.json and click Refresh in Theme Community!"
        )

