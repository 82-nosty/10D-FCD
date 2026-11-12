# -*- coding: utf-8 -*-
"""
10D FCD Declarative JSON Theme Engine
High-performance rendering pipeline for ESP32 CYD 2.8" (240x320 portrait)
"""
import os
import json
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

class ThemeEngine:
    def __init__(self, themes_dir: str = None):
        if themes_dir is None:
            self.themes_dir = Path(__file__).resolve().parent.parent / "themes"
        else:
            self.themes_dir = Path(themes_dir)

        self.font_cache = {}
        self.themes = []
        self.current_theme = None
        self.load_themes()

    def load_themes(self):
        """themes 디렉터리 내의 모든 theme.json 검색 및 로드"""
        self.themes.clear()
        if not self.themes_dir.exists():
            self.themes_dir.mkdir(parents=True, exist_ok=True)
            return

        for entry in sorted(self.themes_dir.iterdir()):
            if entry.is_dir():
                theme_file = entry / "theme.json"
                if theme_file.exists():
                    try:
                        with open(theme_file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            data.setdefault("id", entry.name)
                            data["dir"] = str(entry)
                            preview_file = entry / "preview.png"
                            if preview_file.exists():
                                data["preview"] = str(preview_file)
                            else:
                                data.setdefault("preview", "")
                            self.themes.append(data)
                    except Exception as e:
                        print(f"[ThemeEngine] Failed to load {theme_file}: {e}")

        if self.themes and not self.current_theme:
            self.current_theme = self.themes[0]

    def list_available_themes(self):
        """UI 컴포넌트용 가용 테마 리스트 반환"""
        return list(self.themes)

    def load_theme(self, theme_id: str):
        """테마 ID로 현재 테마 전환 (set_theme_by_id alias)"""
        return self.set_theme_by_id(theme_id)

    def set_theme_by_id(self, theme_id: str):
        for th in self.themes:
            if th.get("id") == theme_id:
                self.current_theme = th
                return True
        return False

    def get_font(self, font_name: str, size: int):
        key = f"{font_name}_{size}"
        if key in self.font_cache:
            return self.font_cache[key]

        font_paths = [
            Path(self.themes_dir) / font_name,
        ]

        # Windows 폰트 경로
        font_paths.extend([
            Path("C:/Windows/Fonts") / font_name,
            Path("C:/Windows/Fonts/malgun.ttf"),
            Path("C:/Windows/Fonts/malgunbd.ttf"),
            Path("C:/Windows/Fonts/arial.ttf")
        ])

        # macOS 폰트 경로 (AppleSDGothicNeo, Helvetica, Arial)
        font_paths.extend([
            Path("/System/Library/Fonts") / font_name,
            Path("/Library/Fonts") / font_name,
            Path("/System/Library/Fonts/Supplemental") / font_name,
            Path("/System/Library/Fonts/AppleSDGothicNeo.ttc"),
            Path("/System/Library/Fonts/Helvetica.ttc"),
            Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
            Path("/Library/Fonts/Arial Unicode.ttf")
        ])

        # Linux 폰트 경로
        font_paths.extend([
            Path("/usr/share/fonts/truetype/nanum/NanumGothic.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
        ])

        font = None
        for fp in font_paths:
            if fp.exists():
                try:
                    font = ImageFont.truetype(str(fp), size)
                    break
                except Exception:
                    pass

        if font is None:
            font = ImageFont.load_default()

        self.font_cache[key] = font
        return font

    def parse_tokens(self, template_str: str, stats: dict, fps_val: float = 0.0) -> str:
        """대화형/선언형 템플릿 변수를 실시간 시스템 센서 값으로 치환"""
        if not template_str:
            return ""

        cpu_val = min(100.0, max(0.0, stats.get("cpu", 0.0)))
        cpu_freq = stats.get("cpu_freq", 0.0)
        cpu_mhz = stats.get("cpu_freq_mhz", 0.0)
        c_sta_str = f"{cpu_freq:.2f}GHz" if cpu_freq > 0.05 else ""

        ram_val = min(100.0, max(0.0, stats.get("ram", 0.0)))
        ram_used = stats.get("ram_used", 0.0)
        ram_total = stats.get("ram_total", 0.0)
        ram_free = stats.get("ram_free_gb", 0.0)
        r_sta_str = f"{ram_used:.1f}GB/{ram_total:.1f}GB" if ram_total > 0.1 else ""

        disk_val = min(100.0, max(0.0, stats.get("disk", 0.0)))
        disk_used = stats.get("disk_used_gb", 0.0)
        disk_total = stats.get("disk_total_gb", 0.0)
        disk_free = stats.get("disk_free_gb", 0.0)
        d_sta_str = f"{disk_used:.0f}GB/{disk_total:.0f}GB" if disk_total > 0.1 else ""

        now_t = time.localtime()
        days_ko = ["월", "화", "수", "목", "금", "토", "일"]
        days_en = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

        tokens = {
            # 시간 & 날짜
            "%now%": time.strftime("%H:%M", now_t),
            "%time%": stats.get("time", time.strftime("%H:%M:%S", now_t)),
            "%hh%": stats.get("hour_24", time.strftime("%H", now_t)),
            "%H%": stats.get("hour_24", time.strftime("%H", now_t)),
            "%h12%": stats.get("hour_12", time.strftime("%I", now_t)),
            "%I%": stats.get("hour_12", time.strftime("%I", now_t)),
            "%MM%": stats.get("min", time.strftime("%M", now_t)),
            "%min%": stats.get("min", time.strftime("%M", now_t)),
            "%ss%": stats.get("sec", time.strftime("%S", now_t)),
            "%sec%": stats.get("sec", time.strftime("%S", now_t)),
            "%ampm%": stats.get("ampm", time.strftime("%p", now_t)),
            "%yyyy%": stats.get("year", time.strftime("%Y", now_t)),
            "%yy%": stats.get("year_short", time.strftime("%y", now_t)),
            "%mm%": stats.get("month", time.strftime("%m", now_t)),
            "%dd%": stats.get("day", time.strftime("%d", now_t)),
            "%date%": stats.get("date", time.strftime("%Y.%m.%d", now_t)),
            "%day_ko%": stats.get("day_ko", days_ko[now_t.tm_wday]),
            "%day_en%": stats.get("day_en", days_en[now_t.tm_wday]),

            # CPU
            "%cpu%": f"{int(round(cpu_val))}",
            "%cpu_float%": f"{cpu_val:.1f}",
            "%cpu_ghz%": f"{cpu_freq:.2f}",
            "%cpu_mhz%": f"{int(round(cpu_mhz))}",
            "%cpu_cores%": str(stats.get("cpu_cores", 1)),
            "%cpu_cores_phys%": str(stats.get("cpu_cores_phys", 1)),
            "%c_sta%": c_sta_str,

            # RAM
            "%ram%": f"{ram_val:.1f}",
            "%ram_int%": f"{int(round(ram_val))}",
            "%ram_used%": f"{ram_used:.1f}",
            "%ram_used_gb%": f"{ram_used:.1f}GB",
            "%ram_total%": f"{ram_total:.1f}",
            "%ram_total_gb%": f"{ram_total:.1f}GB",
            "%ram_free%": f"{ram_free:.1f}",
            "%ram_free_gb%": f"{ram_free:.1f}GB",
            "%ram_used_mb%": f"{int(stats.get('ram_used_mb', 0))}",
            "%ram_total_mb%": f"{int(stats.get('ram_total_mb', 0))}",
            "%r_sta%": r_sta_str,

            # DISK
            "%disk%": f"{int(round(disk_val))}",
            "%disk_float%": f"{disk_val:.1f}",
            "%disk_used%": f"{disk_used:.0f}",
            "%disk_used_gb%": f"{disk_used:.0f}GB",
            "%disk_total%": f"{disk_total:.0f}",
            "%disk_total_gb%": f"{disk_total:.0f}GB",
            "%disk_free%": f"{disk_free:.0f}",
            "%disk_free_gb%": f"{disk_free:.0f}GB",
            "%d_sta%": d_sta_str,

            # 시스템 & 네트워크 & 렌더링
            "%fps%": f"{fps_val:4.1f}",
            "%fps_int%": f"{int(round(fps_val))}",
            "%host%": stats.get("hostname", "10D-PC"),
            "%hostname%": stats.get("hostname", "10D-PC"),
            "%ip%": stats.get("ip", "127.0.0.1"),
        }

        res = template_str
        for k, v in tokens.items():
            res = res.replace(k, str(v))
        return res

    def _get_metric_pct(self, binding: str, stats: dict) -> float:
        """게이지 및 바에 바인딩된 메트릭 백분율(0.0 ~ 1.0) 계산"""
        if binding == "cpu":
            val = stats.get("cpu", 0.0)
        elif binding == "ram":
            val = stats.get("ram", 0.0)
        elif binding == "disk":
            val = stats.get("disk", 0.0)
        else:
            val = stats.get(binding, 0.0)
        try:
            return max(0.0, min(100.0, float(val))) / 100.0
        except Exception:
            return 0.0

    def render_theme_frame(self, t: float, stats: dict, fps_val: float = 0.0) -> Image.Image:
        """선언형 JSON 테마에 따라 240x320 고화질 프레임 렌더링"""
        if not self.current_theme:
            return Image.new("RGB", (240, 320), (0, 0, 0))

        theme = self.current_theme
        theme_dir = Path(theme.get("dir", ""))

        # 1. 배경 (단색 또는 이미지)
        bg_color = tuple(theme.get("background_color", [0, 0, 0]))
        bg_image_rel = theme.get("background_image", "")
        if bg_image_rel and (theme_dir / bg_image_rel).exists():
            try:
                im = Image.open(theme_dir / bg_image_rel).convert("RGBA").resize((240, 320), Image.Resampling.LANCZOS)
            except Exception:
                im = Image.new("RGBA", (240, 320), bg_color + (255,))
        else:
            im = Image.new("RGBA", (240, 320), bg_color + (255,))

        draw = ImageDraw.Draw(im)

        # 2. 요소별 선언형 렌더링
        elements = theme.get("elements", [])
        for elem in elements:
            etype = elem.get("type", "")

            # A. 텍스트 요소
            if etype == "text":
                text_template = elem.get("text", "")
                rendered_text = self.parse_tokens(text_template, stats, fps_val)
                font_name = elem.get("font", "malgunbd.ttf")
                font_size = elem.get("size", 14)
                f = self.get_font(font_name, font_size)
                color = tuple(elem.get("color", [255, 255, 255]))
                x, y = elem.get("x", 0), elem.get("y", 0)
                anchor = elem.get("anchor", "la")  # la, ra, mm, ms, mt 등
                draw.text((x, y), rendered_text, fill=color, font=f, anchor=anchor)

            # B. 프로그레스 바 (가로 또는 세로)
            elif etype == "bar":
                x, y = elem.get("x", 20), elem.get("y", 200)
                w, h = elem.get("w", 200), elem.get("h", 8)
                radius = elem.get("radius", 3)
                bg_col = tuple(elem.get("bg_color", [28, 34, 46, 255]))
                fill_col = tuple(elem.get("fill_color", [0, 229, 255, 255]))
                binding = elem.get("bind", "cpu")
                direction = elem.get("direction", "horizontal")

                pct = self._get_metric_pct(binding, stats)
                draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=bg_col)

                if direction == "vertical":
                    fill_h = max(2, int(h * pct))
                    draw.rounded_rectangle([x, y + h - fill_h, x + w, y + h], radius=radius, fill=fill_col)
                else:
                    fill_w = max(4, int(w * pct))
                    draw.rounded_rectangle([x, y, x + fill_w, y + h], radius=radius, fill=fill_col)

            # C. 회전/맥동 쿨러 링 (아크 & 서클)
            elif etype == "ring":
                cx, cy = elem.get("cx", 120), elem.get("cy", 140)
                r_out = elem.get("radius", 50)
                width = elem.get("width", 5)
                color1 = tuple(elem.get("color1", [0, 229, 255]))
                color2 = tuple(elem.get("color2", [59, 130, 246]))
                speed = elem.get("speed", 120)  # 초당 회전 각도

                angle_start = (t * speed) % 360
                draw.arc([cx - r_out, cy - r_out, cx + r_out, cy + r_out],
                         start=angle_start, end=angle_start + 140,
                         fill=color1, width=width)
                draw.arc([cx - r_out, cy - r_out, cx + r_out, cy + r_out],
                         start=angle_start + 180, end=angle_start + 280,
                         fill=color2, width=width)

            # D. 게이지 아크 미터 (원형 센서 프로그레스)
            elif etype == "arc_meter" or etype == "gauge":
                cx, cy = elem.get("cx", 120), elem.get("cy", 140)
                r_out = elem.get("radius", 45)
                width = elem.get("width", 6)
                bg_col = tuple(elem.get("bg_color", [40, 50, 65]))
                fill_col = tuple(elem.get("fill_color", [0, 229, 255]))
                binding = elem.get("bind", "cpu")
                start_angle = elem.get("start_angle", 135)
                sweep_angle = elem.get("sweep_angle", 270)

                pct = self._get_metric_pct(binding, stats)
                # 배경 트랙
                draw.arc([cx - r_out, cy - r_out, cx + r_out, cy + r_out],
                         start=start_angle, end=start_angle + sweep_angle,
                         fill=bg_col, width=width)
                # 활성 트랙
                if pct > 0.01:
                    draw.arc([cx - r_out, cy - r_out, cx + r_out, cy + r_out],
                             start=start_angle, end=start_angle + (sweep_angle * pct),
                             fill=fill_col, width=width)

            # E. 라운드 사각형 박스 (HUD 카드 패널)
            elif etype == "box":
                x, y = elem.get("x", 10), elem.get("y", 10)
                w, h = elem.get("w", 220), elem.get("h", 60)
                radius = elem.get("radius", 10)
                fill = tuple(elem.get("fill", [14, 17, 24, 190]))
                outline = tuple(elem.get("outline", [45, 55, 72, 255]))
                draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=fill, outline=outline, width=1)

            # F. 구분선 (Line)
            elif etype == "line":
                x1, y1 = elem.get("x1", 20), elem.get("y1", 50)
                x2, y2 = elem.get("x2", 220), elem.get("y2", 50)
                color = tuple(elem.get("color", [35, 42, 56]))
                width = elem.get("width", 1)
                draw.line([(x1, y1), (x2, y2)], fill=color, width=width)

            # G. 이미지 오버레이 (PNG/JPG 아이콘, 로고 등)
            elif etype == "image":
                src = elem.get("src", "")
                if src and (theme_dir / src).exists():
                    try:
                        icon = Image.open(theme_dir / src).convert("RGBA")
                        iw = elem.get("w", icon.width)
                        ih = elem.get("h", icon.height)
                        if iw != icon.width or ih != icon.height:
                            icon = icon.resize((iw, ih), Image.Resampling.LANCZOS)
                        ix, iy = elem.get("x", 0), elem.get("y", 0)
                        im.paste(icon, (ix, iy), icon)
                    except Exception as e:
                        print(f"[ThemeEngine] Failed to render image element {src}: {e}")

        return im.convert("RGB")
