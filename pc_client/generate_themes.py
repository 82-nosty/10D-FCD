# -*- coding: utf-8 -*-
"""
10D FCD - 10 New Commercial Grade Themes Generator
Generates theme.json and renders true 240x320 preview.png for each theme.
"""
import os
import json
import time
from pathlib import Path
from core.theme_engine import ThemeEngine

THEMES_DIR = Path(__file__).resolve().parent / "themes"

THEMES_DATA = [
    # -------------------------------------------------------------------------
    # 1. Pro Sensor Panel (고밀도 하드웨어 센서 패널)
    # -------------------------------------------------------------------------
    {
        "id": "theme05_pro_sensor",
        "name": "Design 5: Pro Sensor Panel",
        "name_ko": "디자인 5: 프로 센서 패널 (하드웨어 모니터)",
        "author": "10D Official",
        "version": "1.0",
        "description": "CPU/RAM/DISK 3단 고밀도 하드웨어 센서 패널",
        "background_color": [8, 11, 18],
        "elements": [
            # 상단 헤더
            {"type": "box", "x": 10, "y": 8, "w": 220, "h": 46, "radius": 8, "fill": [15, 22, 35, 230], "outline": [30, 41, 59, 255]},
            {"type": "text", "text": "10D SENSOR HUD", "x": 20, "y": 14, "size": 13, "color": [0, 229, 255], "font": "malgunbd.ttf"},
            {"type": "text", "text": "%now%:%ss%", "x": 20, "y": 28, "size": 18, "color": [248, 250, 252], "font": "malgunbd.ttf"},
            {"type": "text", "text": "%fps% FPS", "x": 220, "y": 20, "size": 12, "color": [16, 185, 129], "font": "malgunbd.ttf", "anchor": "ra"},

            # 1단: CPU 카드
            {"type": "box", "x": 10, "y": 60, "w": 220, "h": 78, "radius": 8, "fill": [14, 20, 32, 220], "outline": [0, 229, 255, 120]},
            {"type": "text", "text": "CPU CORE", "x": 22, "y": 68, "size": 14, "color": [0, 229, 255], "font": "malgunbd.ttf"},
            {"type": "text", "text": "%c_sta%", "x": 105, "y": 69, "size": 12, "color": [148, 163, 184], "font": "malgun.ttf"},
            {"type": "text", "text": "%cpu%%", "x": 218, "y": 66, "size": 24, "color": [255, 255, 255], "font": "malgunbd.ttf", "anchor": "ra"},
            {"type": "bar", "bind": "cpu", "x": 22, "y": 106, "w": 196, "h": 12, "radius": 5, "bg_color": [25, 33, 48, 255], "fill_color": [0, 229, 255, 255]},

            # 2단: RAM 카드
            {"type": "box", "x": 10, "y": 144, "w": 220, "h": 78, "radius": 8, "fill": [14, 20, 32, 220], "outline": [16, 185, 129, 120]},
            {"type": "text", "text": "MEMORY", "x": 22, "y": 152, "size": 14, "color": [16, 185, 129], "font": "malgunbd.ttf"},
            {"type": "text", "text": "%ram_used_gb%", "x": 105, "y": 153, "size": 12, "color": [148, 163, 184], "font": "malgun.ttf"},
            {"type": "text", "text": "%ram%%", "x": 218, "y": 150, "size": 24, "color": [255, 255, 255], "font": "malgunbd.ttf", "anchor": "ra"},
            {"type": "bar", "bind": "ram", "x": 22, "y": 190, "w": 196, "h": 12, "radius": 5, "bg_color": [25, 33, 48, 255], "fill_color": [16, 185, 129, 255]},

            # 3단: DISK 카드
            {"type": "box", "x": 10, "y": 228, "w": 220, "h": 78, "radius": 8, "fill": [14, 20, 32, 220], "outline": [168, 85, 247, 120]},
            {"type": "text", "text": "SSD (C:)", "x": 22, "y": 236, "size": 14, "color": [168, 85, 247], "font": "malgunbd.ttf"},
            {"type": "text", "text": "%disk_used_gb%", "x": 105, "y": 237, "size": 12, "color": [148, 163, 184], "font": "malgun.ttf"},
            {"type": "text", "text": "%disk%%", "x": 218, "y": 234, "size": 24, "color": [255, 255, 255], "font": "malgunbd.ttf", "anchor": "ra"},
            {"type": "bar", "bind": "disk", "x": 22, "y": 274, "w": 196, "h": 12, "radius": 5, "bg_color": [25, 33, 48, 255], "fill_color": [168, 85, 247, 255]}
        ]
    },

    # -------------------------------------------------------------------------
    # 2. Supercar Racing Tachometer (원형 쿨러에 특화된 270도 대형 RPM 계기판)
    # -------------------------------------------------------------------------
    {
        "id": "theme06_racing_tacho",
        "name": "Design 6: Racing Tachometer",
        "name_ko": "디자인 6: 슈퍼카 타코미터 계기판 (대형 아크)",
        "author": "10D Official",
        "version": "1.0",
        "description": "스포츠카 계기판 느낌의 270도 대형 아크 게이지와 큼직한 CPU 속도계",
        "background_color": [6, 7, 10],
        "elements": [
            {"type": "text", "text": "SPORT CLUSTER", "x": 120, "y": 20, "size": 14, "color": [239, 68, 68], "font": "malgunbd.ttf", "anchor": "mm"},
            {"type": "text", "text": "%c_sta% // %fps% FPS", "x": 120, "y": 38, "size": 12, "color": [148, 163, 184], "font": "malgun.ttf", "anchor": "mm"},

            # 대형 270도 아크 게이지
            {"type": "arc_meter", "bind": "cpu", "cx": 120, "cy": 138, "radius": 74, "width": 12, "start_angle": 135, "sweep_angle": 270, "bg_color": [30, 36, 48], "fill_color": [239, 68, 68]},

            # 중앙 속도계 폰트
            {"type": "text", "text": "%cpu%", "x": 120, "y": 126, "size": 46, "color": [255, 255, 255], "font": "malgunbd.ttf", "anchor": "mm"},
            {"type": "text", "text": "CPU LOAD %", "x": 120, "y": 158, "size": 13, "color": [239, 68, 68], "font": "malgunbd.ttf", "anchor": "mm"},

            # 하단 RAM 바 & 시계
            {"type": "box", "x": 16, "y": 230, "w": 208, "h": 76, "radius": 10, "fill": [16, 20, 28, 210], "outline": [45, 55, 72, 255]},
            {"type": "text", "text": "RAM", "x": 28, "y": 240, "size": 14, "color": [59, 130, 246], "font": "malgunbd.ttf"},
            {"type": "text", "text": "%ram%% (%ram_used_gb%)", "x": 212, "y": 240, "size": 13, "color": [248, 250, 252], "font": "malgunbd.ttf", "anchor": "ra"},
            {"type": "bar", "bind": "ram", "x": 28, "y": 262, "w": 184, "h": 10, "radius": 4, "bg_color": [28, 35, 48, 255], "fill_color": [59, 130, 246, 255]},
            {"type": "text", "text": "TIME %now%:%ss%", "x": 120, "y": 288, "size": 12, "color": [148, 163, 184], "font": "malgunbd.ttf", "anchor": "mm"}
        ]
    },

    # -------------------------------------------------------------------------
    # 3. 80s Retro Synthwave (네온 핫핑크 & 시안 신스웨이브)
    # -------------------------------------------------------------------------
    {
        "id": "theme07_retro_synthwave",
        "name": "Design 7: 80s Retro Synthwave",
        "name_ko": "디자인 7: 80s 레트로 신스웨이브",
        "author": "10D Official",
        "version": "1.0",
        "description": "네온 핫핑크와 시안 컬러의 강렬한 80년대 레트로 디지털 HUD",
        "background_color": [12, 6, 24],
        "elements": [
            # 초대형 디지털 시계
            {"type": "text", "text": "%now%", "x": 120, "y": 38, "size": 48, "color": [255, 0, 128], "font": "malgunbd.ttf", "anchor": "mm"},
            {"type": "text", "text": "%yyyy%.%mm%.%dd% // %day_en%", "x": 120, "y": 74, "size": 13, "color": [0, 240, 255], "font": "malgunbd.ttf", "anchor": "mm"},
            {"type": "line", "x1": 20, "y1": 90, "x2": 220, "y2": 90, "color": [255, 0, 128], "width": 2},

            # 중앙 듀얼 회전 네온 링
            {"type": "ring", "cx": 120, "cy": 150, "radius": 48, "width": 7, "color1": [255, 0, 128], "color2": [0, 240, 255], "speed": 160},
            {"type": "text", "text": "SYNTH", "x": 120, "y": 142, "size": 17, "color": [255, 255, 255], "font": "malgunbd.ttf", "anchor": "mm"},
            {"type": "text", "text": "CORE %cpu%%", "x": 120, "y": 164, "size": 14, "color": [0, 240, 255], "font": "malgunbd.ttf", "anchor": "mm"},

            # 하단 2단 네온 바
            {"type": "box", "x": 12, "y": 218, "w": 216, "h": 94, "radius": 10, "fill": [20, 10, 36, 210], "outline": [255, 0, 128, 160]},
            {"type": "text", "text": "CPU LOAD", "x": 24, "y": 228, "size": 15, "color": [255, 0, 128], "font": "malgunbd.ttf"},
            {"type": "text", "text": "%cpu%% (%c_sta%)", "x": 216, "y": 228, "size": 14, "color": [255, 255, 255], "font": "malgunbd.ttf", "anchor": "ra"},
            {"type": "bar", "bind": "cpu", "x": 24, "y": 250, "w": 192, "h": 10, "radius": 4, "bg_color": [40, 16, 60, 255], "fill_color": [255, 0, 128, 255]},
            {"type": "text", "text": "RAM MEMORY", "x": 24, "y": 268, "size": 15, "color": [0, 240, 255], "font": "malgunbd.ttf"},
            {"type": "text", "text": "%ram%% (%ram_used_gb%)", "x": 216, "y": 268, "size": 14, "color": [255, 255, 255], "font": "malgunbd.ttf", "anchor": "ra"},
            {"type": "bar", "bind": "ram", "x": 24, "y": 290, "w": 192, "h": 10, "radius": 4, "bg_color": [15, 35, 60, 255], "fill_color": [0, 240, 255, 255]}
        ]
    },

    # -------------------------------------------------------------------------
    # 4. Cyberpunk Mecha Heavy (인더스트리얼 앰버 옐로우 & 메카 HUD)
    # -------------------------------------------------------------------------
    {
        "id": "theme08_cyberpunk_mecha",
        "name": "Design 8: Cyberpunk Mecha HUD",
        "name_ko": "디자인 8: 사이버펑크 메카 HUD (경고 옐로우)",
        "author": "10D Official",
        "version": "1.0",
        "description": "중장비 및 메카 로봇 느낌의 앰버 옐로우 인더스트리얼 테마",
        "background_color": [10, 10, 8],
        "elements": [
            # 경고 배너 헤더
            {"type": "box", "x": 10, "y": 8, "w": 220, "h": 36, "radius": 4, "fill": [250, 204, 21, 230], "outline": [255, 255, 255, 255]},
            {"type": "text", "text": "[ CAUTION // MECHA CORE ]", "x": 120, "y": 26, "size": 14, "color": [0, 0, 0], "font": "malgunbd.ttf", "anchor": "mm"},

            # 중앙 원형 메카 링
            {"type": "arc_meter", "bind": "cpu", "cx": 120, "cy": 122, "radius": 62, "width": 10, "start_angle": 135, "sweep_angle": 270, "bg_color": [40, 36, 18], "fill_color": [250, 204, 21]},
            {"type": "text", "text": "%cpu%%", "x": 120, "y": 114, "size": 38, "color": [255, 255, 255], "font": "malgunbd.ttf", "anchor": "mm"},
            {"type": "text", "text": "REACTOR OUTPUT", "x": 120, "y": 142, "size": 12, "color": [250, 204, 21], "font": "malgunbd.ttf", "anchor": "mm"},

            # 하단 메카 상태 카드
            {"type": "box", "x": 10, "y": 196, "w": 220, "h": 114, "radius": 6, "fill": [18, 18, 15, 230], "outline": [250, 204, 21, 140]},
            {"type": "text", "text": "CPU CLOCK", "x": 20, "y": 206, "size": 14, "color": [250, 204, 21], "font": "malgunbd.ttf"},
            {"type": "text", "text": "%c_sta%", "x": 220, "y": 206, "size": 14, "color": [255, 255, 255], "font": "malgunbd.ttf", "anchor": "ra"},
            {"type": "bar", "bind": "cpu", "x": 20, "y": 228, "w": 200, "h": 9, "radius": 3, "bg_color": [45, 42, 25, 255], "fill_color": [250, 204, 21, 255]},
            {"type": "text", "text": "RAM SYSTEM", "x": 20, "y": 246, "size": 14, "color": [251, 146, 60], "font": "malgunbd.ttf"},
            {"type": "text", "text": "%ram%% (%ram_used_gb%)", "x": 220, "y": 246, "size": 14, "color": [255, 255, 255], "font": "malgunbd.ttf", "anchor": "ra"},
            {"type": "bar", "bind": "ram", "x": 20, "y": 268, "w": 200, "h": 9, "radius": 3, "bg_color": [45, 30, 20, 255], "fill_color": [251, 146, 60, 255]},
            {"type": "text", "text": "FPS: %fps%  |  SYS OK", "x": 120, "y": 294, "size": 12, "color": [160, 160, 140], "font": "malgunbd.ttf", "anchor": "mm"}
        ]
    },

    # -------------------------------------------------------------------------
    # 5. Modern Minimal Bold (순백/모노크롬 큼직한 타이포그래피)
    # -------------------------------------------------------------------------
    {
        "id": "theme09_minimal_bold",
        "name": "Design 9: Modern Minimal Bold",
        "name_ko": "디자인 9: 모던 볼드 미니멀 (대형 타이포)",
        "author": "10D Official",
        "version": "1.0",
        "description": "극도로 정갈한 순백 모노크롬과 52pt 초대형 볼드 시계",
        "background_color": [10, 12, 16],
        "elements": [
            # 초대형 디지털 시계
            {"type": "text", "text": "%now%", "x": 120, "y": 48, "size": 52, "color": [255, 255, 255], "font": "malgunbd.ttf", "anchor": "mm"},
            {"type": "text", "text": "%date%  %day_en%", "x": 120, "y": 88, "size": 14, "color": [148, 163, 184], "font": "malgunbd.ttf", "anchor": "mm"},
            {"type": "line", "x1": 30, "y1": 108, "x2": 210, "y2": 108, "color": [51, 65, 85], "width": 1},

            # 중앙 메트릭 블록 (CPU & RAM 2컬럼)
            {"type": "box", "x": 14, "y": 126, "w": 102, "h": 82, "radius": 8, "fill": [18, 22, 30, 220], "outline": [45, 55, 72, 255]},
            {"type": "text", "text": "CPU", "x": 65, "y": 140, "size": 14, "color": [148, 163, 184], "font": "malgunbd.ttf", "anchor": "mm"},
            {"type": "text", "text": "%cpu%%", "x": 65, "y": 170, "size": 28, "color": [255, 255, 255], "font": "malgunbd.ttf", "anchor": "mm"},
            {"type": "text", "text": "%c_sta%", "x": 65, "y": 194, "size": 11, "color": [0, 229, 255], "font": "malgunbd.ttf", "anchor": "mm"},

            {"type": "box", "x": 124, "y": 126, "w": 102, "h": 82, "radius": 8, "fill": [18, 22, 30, 220], "outline": [45, 55, 72, 255]},
            {"type": "text", "text": "RAM", "x": 175, "y": 140, "size": 14, "color": [148, 163, 184], "font": "malgunbd.ttf", "anchor": "mm"},
            {"type": "text", "text": "%ram%%", "x": 175, "y": 170, "size": 28, "color": [255, 255, 255], "font": "malgunbd.ttf", "anchor": "mm"},
            {"type": "text", "text": "%ram_used_gb%", "x": 175, "y": 194, "size": 11, "color": [16, 185, 129], "font": "malgunbd.ttf", "anchor": "mm"},

            # 하단 바 2개
            {"type": "bar", "bind": "cpu", "x": 14, "y": 232, "w": 212, "h": 12, "radius": 6, "bg_color": [30, 36, 48, 255], "fill_color": [248, 250, 252, 255]},
            {"type": "bar", "bind": "ram", "x": 14, "y": 256, "w": 212, "h": 12, "radius": 6, "bg_color": [30, 36, 48, 255], "fill_color": [100, 116, 139, 255]},
            {"type": "text", "text": "10D FCD · %fps% FPS", "x": 120, "y": 292, "size": 13, "color": [100, 116, 139], "font": "malgunbd.ttf", "anchor": "mm"}
        ]
    },

    # -------------------------------------------------------------------------
    # 6. Sci-Fi Warp Core Reactor (우주선 워프 코어 펄스 링)
    # -------------------------------------------------------------------------
    {
        "id": "theme10_space_warp_core",
        "name": "Design 10: Sci-Fi Warp Core",
        "name_ko": "디자인 10: SF 워프 코어 리액터 (우주선 HUD)",
        "author": "10D Official",
        "version": "1.0",
        "description": "딥 코스믹 블루와 바이올렛 플라즈마의 우주선 코어 리액터",
        "background_color": [4, 8, 16],
        "elements": [
            {"type": "text", "text": "WARP CORE STATUS", "x": 120, "y": 18, "size": 13, "color": [56, 189, 248], "font": "malgunbd.ttf", "anchor": "mm"},
            {"type": "text", "text": "REACTIVITY: %cpu%%", "x": 120, "y": 36, "size": 17, "color": [255, 255, 255], "font": "malgunbd.ttf", "anchor": "mm"},

            # 대형 듀얼 회전 워프 링
            {"type": "ring", "cx": 120, "cy": 136, "radius": 62, "width": 8, "color1": [14, 165, 233], "color2": [168, 85, 247], "speed": 220},
            {"type": "ring", "cx": 120, "cy": 136, "radius": 42, "width": 5, "color1": [168, 85, 247], "color2": [14, 165, 233], "speed": -180},
            {"type": "text", "text": "WARP", "x": 120, "y": 126, "size": 18, "color": [0, 229, 255], "font": "malgunbd.ttf", "anchor": "mm"},
            {"type": "text", "text": "LEVEL %cpu%", "x": 120, "y": 148, "size": 14, "color": [255, 255, 255], "font": "malgunbd.ttf", "anchor": "mm"},

            # 하단 플라즈마 에너지 게이지
            {"type": "box", "x": 12, "y": 218, "w": 216, "h": 92, "radius": 8, "fill": [10, 16, 30, 220], "outline": [14, 165, 233, 140]},
            {"type": "text", "text": "PLASMA ENERGY (RAM)", "x": 22, "y": 228, "size": 13, "color": [168, 85, 247], "font": "malgunbd.ttf"},
            {"type": "text", "text": "%ram%% (%ram_used_gb%)", "x": 218, "y": 228, "size": 13, "color": [248, 250, 252], "font": "malgunbd.ttf", "anchor": "ra"},
            {"type": "bar", "bind": "ram", "x": 22, "y": 248, "w": 196, "h": 10, "radius": 5, "bg_color": [20, 25, 45, 255], "fill_color": [168, 85, 247, 255]},
            {"type": "text", "text": "CORE FREQ: %c_sta%", "x": 22, "y": 268, "size": 13, "color": [56, 189, 248], "font": "malgunbd.ttf"},
            {"type": "text", "text": "FPS: %fps%", "x": 218, "y": 268, "size": 13, "color": [16, 185, 129], "font": "malgunbd.ttf", "anchor": "ra"},
            {"type": "bar", "bind": "cpu", "x": 22, "y": 288, "w": 196, "h": 10, "radius": 5, "bg_color": [20, 25, 45, 255], "fill_color": [14, 165, 233, 255]}
        ]
    },

    # -------------------------------------------------------------------------
    # 7. 8-Bit Arcade Gamer HUD (레트로 RPG HP/MP 게이지)
    # -------------------------------------------------------------------------
    {
        "id": "theme11_arcade_pixel",
        "name": "Design 11: 8-Bit Arcade Gamer",
        "name_ko": "디자인 11: 8비트 아케이드 게이머 (HP/MP)",
        "author": "10D Official",
        "version": "1.0",
        "description": "고전 아케이드 RPG 감성의 HP[CPU]와 MP[RAM] 바 HUD",
        "background_color": [5, 5, 8],
        "elements": [
            # 레트로 게임 타이틀
            {"type": "box", "x": 10, "y": 8, "w": 220, "h": 40, "radius": 0, "fill": [20, 20, 30, 240], "outline": [255, 255, 255, 255]},
            {"type": "text", "text": "PLAYER 1 // %now%", "x": 20, "y": 20, "size": 14, "color": [255, 215, 0], "font": "malgunbd.ttf"},
            {"type": "text", "text": "LV.%cpu%", "x": 220, "y": 20, "size": 16, "color": [255, 255, 255], "font": "malgunbd.ttf", "anchor": "ra"},

            # HP 바 (CPU 부하)
            {"type": "box", "x": 10, "y": 58, "w": 220, "h": 68, "radius": 0, "fill": [20, 15, 15, 220], "outline": [239, 68, 68, 255]},
            {"type": "text", "text": "HP [CPU LOAD]", "x": 20, "y": 68, "size": 14, "color": [239, 68, 68], "font": "malgunbd.ttf"},
            {"type": "text", "text": "%cpu%%", "x": 220, "y": 68, "size": 22, "color": [255, 255, 255], "font": "malgunbd.ttf", "anchor": "ra"},
            {"type": "bar", "bind": "cpu", "x": 20, "y": 98, "w": 200, "h": 16, "radius": 0, "bg_color": [50, 20, 20, 255], "fill_color": [239, 68, 68, 255]},

            # MP 바 (RAM 점유)
            {"type": "box", "x": 10, "y": 136, "w": 220, "h": 68, "radius": 0, "fill": [15, 15, 25, 220], "outline": [59, 130, 246, 255]},
            {"type": "text", "text": "MP [RAM MEMORY]", "x": 20, "y": 146, "size": 14, "color": [59, 130, 246], "font": "malgunbd.ttf"},
            {"type": "text", "text": "%ram%%", "x": 220, "y": 146, "size": 22, "color": [255, 255, 255], "font": "malgunbd.ttf", "anchor": "ra"},
            {"type": "bar", "bind": "ram", "x": 20, "y": 176, "w": 200, "h": 16, "radius": 0, "bg_color": [20, 25, 60, 255], "fill_color": [59, 130, 246, 255]},

            # EXP 바 (DISK)
            {"type": "box", "x": 10, "y": 214, "w": 220, "h": 68, "radius": 0, "fill": [20, 20, 15, 220], "outline": [234, 179, 8, 255]},
            {"type": "text", "text": "EXP [SSD C:]", "x": 20, "y": 224, "size": 14, "color": [234, 179, 8], "font": "malgunbd.ttf"},
            {"type": "text", "text": "%disk%%", "x": 220, "y": 224, "size": 22, "color": [255, 255, 255], "font": "malgunbd.ttf", "anchor": "ra"},
            {"type": "bar", "bind": "disk", "x": 20, "y": 254, "w": 200, "h": 16, "radius": 0, "bg_color": [50, 40, 15, 255], "fill_color": [234, 179, 8, 255]},

            {"type": "text", "text": "INSERT COIN // 10D FCD", "x": 120, "y": 298, "size": 12, "color": [156, 163, 175], "font": "malgunbd.ttf", "anchor": "mm"}
        ]
    },

    # -------------------------------------------------------------------------
    # 8. Sci-Fi Emergency Command HUD (SF 비상 지휘 오렌지)
    # -------------------------------------------------------------------------
    {
        "id": "theme12_scifi_emergency",
        "name": "Design 12: Sci-Fi Emergency Command",
        "name_ko": "디자인 12: SF 비상 지휘 패널 (오렌지)",
        "author": "10D Official",
        "version": "1.0",
        "description": "강렬한 비상 오렌지와 블랙 SF 메카닉 인터페이스",
        "background_color": [10, 4, 0],
        "elements": [
            # EMERGENCY 배너
            {"type": "box", "x": 8, "y": 8, "w": 224, "h": 36, "radius": 0, "fill": [255, 85, 0, 240], "outline": [255, 255, 255, 255]},
            {"type": "text", "text": "EMERGENCY // SYSTEM ALERT", "x": 120, "y": 26, "size": 15, "color": [0, 0, 0], "font": "malgunbd.ttf", "anchor": "mm"},

            # 중앙 원형 아크 싱크로율
            {"type": "arc_meter", "bind": "cpu", "cx": 120, "cy": 128, "radius": 68, "width": 11, "start_angle": 135, "sweep_angle": 270, "bg_color": [45, 18, 0], "fill_color": [255, 85, 0]},
            {"type": "text", "text": "%cpu%%", "x": 120, "y": 118, "size": 42, "color": [255, 255, 255], "font": "malgunbd.ttf", "anchor": "mm"},
            {"type": "text", "text": "SYNC RATE", "x": 120, "y": 148, "size": 14, "color": [255, 85, 0], "font": "malgunbd.ttf", "anchor": "mm"},

            # 하단 파워 상태
            {"type": "box", "x": 8, "y": 210, "w": 224, "h": 102, "radius": 0, "fill": [20, 8, 0, 220], "outline": [255, 85, 0, 180]},
            {"type": "text", "text": "INTERNAL POWER (RAM)", "x": 18, "y": 220, "size": 13, "color": [255, 85, 0], "font": "malgunbd.ttf"},
            {"type": "text", "text": "%ram%% (%ram_used_gb%)", "x": 222, "y": 220, "size": 13, "color": [255, 255, 255], "font": "malgunbd.ttf", "anchor": "ra"},
            {"type": "bar", "bind": "ram", "x": 18, "y": 240, "w": 204, "h": 12, "radius": 0, "bg_color": [50, 20, 0, 255], "fill_color": [255, 85, 0, 255]},
            {"type": "text", "text": "CLOCK: %c_sta%", "x": 18, "y": 262, "size": 13, "color": [255, 160, 50], "font": "malgunbd.ttf"},
            {"type": "text", "text": "TIME %now%:%ss%", "x": 222, "y": 262, "size": 13, "color": [255, 255, 255], "font": "malgunbd.ttf", "anchor": "ra"},
            {"type": "text", "text": "CORE SYSTEM: ALL CLEAR", "x": 120, "y": 292, "size": 12, "color": [180, 80, 20], "font": "malgunbd.ttf", "anchor": "mm"}
        ]
    },

    # -------------------------------------------------------------------------
    # 9. Matrix Green Terminal (그린 CRT 모니터 해커 감성)
    # -------------------------------------------------------------------------
    {
        "id": "theme13_matrix_terminal",
        "name": "Design 13: Matrix Green Terminal",
        "name_ko": "디자인 13: 매트릭스 그린 터미널 (CRT 해커)",
        "author": "10D Official",
        "version": "1.0",
        "description": "선명한 형광 그린 CRT 감성의 커맨드라인 시스템 터미널",
        "background_color": [4, 12, 6],
        "elements": [
            # 터미널 헤더
            {"type": "text", "text": "root@%host%:~$ stats", "x": 16, "y": 14, "size": 14, "color": [34, 197, 94], "font": "malgunbd.ttf"},
            {"type": "text", "text": "IP: %ip%", "x": 16, "y": 32, "size": 12, "color": [74, 222, 128], "font": "malgun.ttf"},
            {"type": "line", "x1": 16, "y1": 50, "x2": 224, "y2": 50, "color": [34, 197, 94], "width": 1},

            # 대형 터미널 시계
            {"type": "text", "text": "%now%:%ss%", "x": 120, "y": 80, "size": 36, "color": [34, 197, 94], "font": "malgunbd.ttf", "anchor": "mm"},
            {"type": "text", "text": "[ SYSTEM STREAMING: %fps% FPS ]", "x": 120, "y": 110, "size": 12, "color": [74, 222, 128], "font": "malgunbd.ttf", "anchor": "mm"},

            # 하드웨어 블록 3개
            {"type": "box", "x": 12, "y": 130, "w": 216, "h": 50, "radius": 4, "fill": [8, 24, 12, 220], "outline": [34, 197, 94, 160]},
            {"type": "text", "text": "CPU CORE", "x": 22, "y": 138, "size": 13, "color": [34, 197, 94], "font": "malgunbd.ttf"},
            {"type": "text", "text": "%cpu%% // %c_sta%", "x": 218, "y": 138, "size": 13, "color": [240, 253, 244], "font": "malgunbd.ttf", "anchor": "ra"},
            {"type": "bar", "bind": "cpu", "x": 22, "y": 158, "w": 196, "h": 10, "radius": 3, "bg_color": [15, 40, 20, 255], "fill_color": [34, 197, 94, 255]},

            {"type": "box", "x": 12, "y": 188, "w": 216, "h": 50, "radius": 4, "fill": [8, 24, 12, 220], "outline": [34, 197, 94, 160]},
            {"type": "text", "text": "RAM USAGE", "x": 22, "y": 196, "size": 13, "color": [34, 197, 94], "font": "malgunbd.ttf"},
            {"type": "text", "text": "%ram%% // %ram_used_gb%", "x": 218, "y": 196, "size": 13, "color": [240, 253, 244], "font": "malgunbd.ttf", "anchor": "ra"},
            {"type": "bar", "bind": "ram", "x": 22, "y": 216, "w": 196, "h": 10, "radius": 3, "bg_color": [15, 40, 20, 255], "fill_color": [34, 197, 94, 255]},

            {"type": "box", "x": 12, "y": 246, "w": 216, "h": 50, "radius": 4, "fill": [8, 24, 12, 220], "outline": [34, 197, 94, 160]},
            {"type": "text", "text": "DISK STORAGE", "x": 22, "y": 254, "size": 13, "color": [34, 197, 94], "font": "malgunbd.ttf"},
            {"type": "text", "text": "%disk%% // %disk_used_gb%", "x": 218, "y": 254, "size": 13, "color": [240, 253, 244], "font": "malgunbd.ttf", "anchor": "ra"},
            {"type": "bar", "bind": "disk", "x": 22, "y": 274, "w": 196, "h": 10, "radius": 3, "bg_color": [15, 40, 20, 255], "fill_color": [34, 197, 94, 255]},

            {"type": "text", "text": "_ SYSTEM MONITOR READY", "x": 120, "y": 304, "size": 11, "color": [74, 222, 128], "font": "malgunbd.ttf", "anchor": "mm"}
        ]
    },

    # -------------------------------------------------------------------------
    # 10. Pastel Aurora Glow (감성 파스텔 듀얼 게이지 네온)
    # -------------------------------------------------------------------------
    {
        "id": "theme14_anime_aurora",
        "name": "Design 14: Pastel Aurora Glow",
        "name_ko": "디자인 14: 파스텔 오로라 네온 (감성 듀얼)",
        "author": "10D Official",
        "version": "1.0",
        "description": "파스텔 민트와 라벤더, 핑크가 어우러진 부드러운 감성 네온 HUD",
        "background_color": [12, 10, 18],
        "elements": [
            # 상단 시계 & 날짜
            {"type": "text", "text": "%now%", "x": 120, "y": 34, "size": 38, "color": [244, 114, 182], "font": "malgunbd.ttf", "anchor": "mm"},
            {"type": "text", "text": "%date%  %day_en%", "x": 120, "y": 62, "size": 13, "color": [192, 132, 252], "font": "malgun.ttf", "anchor": "mm"},

            # 중앙 듀얼 게이지 (CPU 핑크 게이지 & RAM 민트 게이지)
            {"type": "arc_meter", "bind": "cpu", "cx": 120, "cy": 142, "radius": 62, "width": 8, "start_angle": 135, "sweep_angle": 270, "bg_color": [35, 20, 40], "fill_color": [244, 114, 182]},
            {"type": "arc_meter", "bind": "ram", "cx": 120, "cy": 142, "radius": 46, "width": 8, "start_angle": 135, "sweep_angle": 270, "bg_color": [20, 35, 40], "fill_color": [94, 234, 212]},
            {"type": "text", "text": "%cpu%%", "x": 120, "y": 134, "size": 22, "color": [244, 114, 182], "font": "malgunbd.ttf", "anchor": "mm"},
            {"type": "text", "text": "RAM %ram%%", "x": 120, "y": 154, "size": 13, "color": [94, 234, 212], "font": "malgunbd.ttf", "anchor": "mm"},

            # 하단 파스텔 정보 카드
            {"type": "box", "x": 14, "y": 222, "w": 212, "h": 88, "radius": 12, "fill": [22, 18, 32, 220], "outline": [192, 132, 252, 160]},
            {"type": "text", "text": "AURORA CORE", "x": 26, "y": 234, "size": 14, "color": [244, 114, 182], "font": "malgunbd.ttf"},
            {"type": "text", "text": "%c_sta%", "x": 214, "y": 234, "size": 13, "color": [248, 250, 252], "font": "malgunbd.ttf", "anchor": "ra"},
            {"type": "bar", "bind": "cpu", "x": 26, "y": 256, "w": 188, "h": 9, "radius": 4, "bg_color": [35, 25, 50, 255], "fill_color": [244, 114, 182, 255]},
            {"type": "text", "text": "MEMORY", "x": 26, "y": 272, "size": 13, "color": [94, 234, 212], "font": "malgunbd.ttf"},
            {"type": "text", "text": "%ram_used_gb%", "x": 214, "y": 272, "size": 13, "color": [248, 250, 252], "font": "malgunbd.ttf", "anchor": "ra"},
            {"type": "bar", "bind": "ram", "x": 26, "y": 292, "w": 188, "h": 9, "radius": 4, "bg_color": [20, 40, 45, 255], "fill_color": [94, 234, 212, 255]}
        ]
    }
]

def main():
    print(f"Generating 10 new themes in {THEMES_DIR}...")
    sample_stats = {
        "cpu": 54.0,
        "cpu_freq": 4.35,
        "cpu_freq_mhz": 4350,
        "cpu_cores": 16,
        "cpu_cores_phys": 8,
        "ram": 58.2,
        "ram_used": 18.6,
        "ram_total": 32.0,
        "ram_free_gb": 13.4,
        "disk": 64.0,
        "disk_used_gb": 328,
        "disk_total_gb": 512,
        "disk_free_gb": 184,
        "hostname": "DESKTOP-GAMING",
        "ip": "192.168.0.50",
    }

    engine = ThemeEngine(str(THEMES_DIR))

    for item in THEMES_DATA:
        t_id = item["id"]
        t_dir = THEMES_DIR / t_id
        t_dir.mkdir(parents=True, exist_ok=True)

        json_path = t_dir / "theme.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(item, f, indent=2, ensure_ascii=False)

        # 렌더링 검증 및 preview.png 생성
        item["dir"] = str(t_dir)
        engine.current_theme = item
        img = engine.render_theme_frame(t=1.5, stats=sample_stats, fps_val=27.5)
        preview_path = t_dir / "preview.png"
        img.save(preview_path, format="PNG")
        print(f" -> Created {t_id}: theme.json & preview.png (Size: {img.size})")

    # 기존 테마들의 preview.png도 업데이트
    existing_dirs = ["design1_classic", "design2_cyber", "design3_retro", "design4_minimal"]
    for ed in existing_dirs:
        ed_dir = THEMES_DIR / ed
        json_file = ed_dir / "theme.json"
        if json_file.exists():
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            data["dir"] = str(ed_dir)
            engine.current_theme = data
            img = engine.render_theme_frame(t=1.5, stats=sample_stats, fps_val=27.5)
            img.save(ed_dir / "preview.png", format="PNG")
            print(f" -> Updated preview for existing theme {ed}")

    print("All 10 new themes generated and previews rendered successfully!")

if __name__ == "__main__":
    main()

