# -*- coding: utf-8 -*-
"""
10D FCD - Commercial Cooler LCD Frame & HUD Renderer (Portrait 240x320)
Zero-Overlap Layout + Anti-Aliased Cooler Core Ring + 4:4:4 High-Quality JPEG
"""
import io
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from config import TARGET_WIDTH, TARGET_HEIGHT


# CYD 2.8" TN 패널 하드웨어 특성에 맞춘 역감마 LUT (Gamma 1.24)
_GAMMA = 1.24
_LUT_TABLE = np.array(
    [min(255, max(0, int(((i / 255.0) ** _GAMMA) * 255.0))) for i in range(256)],
    dtype=np.uint8
)

# 16-bit RGB565 색 띠(Banding) 제거용 4x4 Ordered Bayer 디더링 행렬 (정규화: -0.5 ~ +0.5)
_BAYER_4X4 = (
    np.array([
        [ 0,  8,  2, 10],
        [12,  4, 14,  6],
        [ 3, 11,  1,  9],
        [15,  7, 13,  5],
    ], dtype=np.float32) / 16.0 - 0.5
)
_BAYER_320X240 = np.tile(_BAYER_4X4, (TARGET_HEIGHT // 4, TARGET_WIDTH // 4))


class OverlayEngine:
    def __init__(self):
        # 고해상도 맑은고딕 / Segoe UI 폰트 로드 (프리셋 1과 동일한 대형 볼드 규격)
        try:
            self.font_brand = ImageFont.truetype("malgunbd.ttf", 16)
            self.font_main = ImageFont.truetype("malgunbd.ttf", 16)
            self.font_stat = ImageFont.truetype("malgunbd.ttf", 14)
            self.font_sub = ImageFont.truetype("malgun.ttf", 13)
            self.font_small = ImageFont.truetype("malgunbd.ttf", 11)
            self.font_clock = ImageFont.truetype("malgunbd.ttf", 28)
        except Exception:
            self.font_brand = ImageFont.load_default()
            self.font_main = ImageFont.load_default()
            self.font_stat = ImageFont.load_default()
            self.font_sub = ImageFont.load_default()
            self.font_small = ImageFont.load_default()
            self.font_clock = ImageFont.load_default()

    def generate_demo_frame(self, t):
        """
        상/하단 HUD와 절대 겹치지 않는 중앙(Y=72~214) 전용 쿨러 코어 대시보드
        2x 슈퍼샘플링으로 원 테두리를 매끄럽게 렌더링하여 JPEG 블록 노이즈 최소화
        """
        # 순수 리얼 블랙 배경
        im = Image.new("RGB", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0))

        # 중앙 쿨러 코어 영역만 2x 슈퍼샘플링(480x300)으로 그려서 축소 -> 계단현상 제거
        scale = 2
        ring_w, ring_h = TARGET_WIDTH * scale, 152 * scale
        ring_img = Image.new("RGB", (ring_w, ring_h), (0, 0, 0))
        rdraw = ImageDraw.Draw(ring_img)

        cx = ring_w // 2
        cy = ring_h // 2 - 4 * scale
        r_outer = 54 * scale
        r_inner = 42 * scale

        # 1. 은은한 외곽 다크 트랙 링
        rdraw.ellipse(
            [cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer],
            outline=(26, 32, 44), width=6 * scale
        )

        # 2. 회전하는 네온 시안 아크 (쿨러 팬 회전 느낌)
        angle_start = (t * 140) % 360
        rdraw.arc(
            [cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer],
            start=angle_start, end=angle_start + 135,
            fill=(0, 229, 255), width=6 * scale
        )
        rdraw.arc(
            [cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer],
            start=angle_start + 180, end=angle_start + 275,
            fill=(59, 130, 246), width=6 * scale
        )

        # 3. 내부 맥동 서클
        pulse = 0.5 + 0.5 * math.sin(t * 2.5)
        inner_col = (
            int(20 + 18 * pulse),
            int(30 + 30 * pulse),
            int(48 + 45 * pulse),
        )
        rdraw.ellipse(
            [cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner],
            fill=(8, 12, 18), outline=inner_col, width=2 * scale
        )

        # 고품질 LANCZOS 축소 후 중앙(Y=68)에 붙이기
        ring_smooth = ring_img.resize((TARGET_WIDTH, 152), Image.Resampling.LANCZOS)
        im.paste(ring_smooth, (0, 68))

        draw = ImageDraw.Draw(im)
        # 원 중앙 브랜드 & 상태 텍스트
        draw.text((120, 130), "10D FCD", fill=(0, 229, 255), font=self.font_brand, anchor="mm")
        draw.text((120, 152), "COOLER SYNC", fill=(148, 163, 184), font=self.font_sub, anchor="mm")

        return im

    def apply_overlay(self, im, stats, show_cpu=True, show_ram=True, show_time=True, show_fps=True, fps_val=0.0, hud_alpha=190):
        # 글래스모피즘 반투명 HUD 합성을 위해 RGBA 레이어 사용
        base = im.convert("RGBA")
        overlay_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay_layer)

        bg_alpha = max(0, min(255, int(hud_alpha)))
        box_bg = (14, 17, 24, bg_alpha)
        border_col = (45, 55, 72, min(255, bg_alpha + 65))

        # 1. 상단 전용 구역 (Y=8 ~ Y=64): 시계 + 날짜 + 우상단 FPS 배지
        if show_time or show_fps:
            draw.rounded_rectangle(
                [10, 8, TARGET_WIDTH - 10, 64],
                radius=10, fill=box_bg, outline=border_col, width=1
            )

        if show_time:
            draw.text((22, 14), stats.get("date", ""), fill=(148, 163, 184, 255), font=self.font_sub)
            draw.text((22, 28), stats.get("time", ""), fill=(255, 255, 255, 255), font=self.font_clock)

        if show_fps:
            fps_str = f"{fps_val:4.1f} FPS"
            # 우측 상단 여유 있는 칩
            chip_alpha = max(30, int(bg_alpha * 0.9))
            draw.rounded_rectangle(
                [TARGET_WIDTH - 90, 14, TARGET_WIDTH - 18, 38],
                radius=6, fill=(10, 32, 26, chip_alpha), outline=(16, 185, 129, 255), width=1
            )
            draw.text((TARGET_WIDTH - 54, 26), fps_str, fill=(16, 220, 150, 255), font=self.font_small, anchor="mm")

        # 2. 하단 전용 구역 (Y=216 ~ Y=312, 높이 96px): CPU & RAM 대형 텔레메트리 카드
        if show_cpu or show_ram:
            draw.rounded_rectangle(
                [10, 216, TARGET_WIDTH - 10, TARGET_HEIGHT - 8],
                radius=10, fill=box_bg, outline=border_col, width=1
            )

            if show_cpu:
                cpu = min(100.0, max(0.0, stats.get("cpu", 0.0)))
                cpu_freq = stats.get("cpu_freq", 0.0)
                if cpu_freq > 0.05:
                    cpu_txt = f"{int(round(cpu))}%  {cpu_freq:.2f}GHz"
                else:
                    cpu_txt = f"{int(round(cpu))}%"

                draw.text((20, 224), "CPU", fill=(56, 189, 248, 255), font=self.font_main)
                draw.text((TARGET_WIDTH - 20, 224), cpu_txt, fill=(255, 255, 255, 255), font=self.font_stat, anchor="ra")
                # 두툼한 10px 프로그레스 바
                bar_w = TARGET_WIDTH - 40
                fill_w = max(4, int(bar_w * (cpu / 100.0)))
                draw.rounded_rectangle([20, 248, 20 + bar_w, 258], radius=4, fill=(28, 34, 46, max(40, bg_alpha)))
                draw.rounded_rectangle([20, 248, 20 + fill_w, 258], radius=4, fill=(0, 229, 255, 255))

            if show_ram:
                ram = min(100.0, max(0.0, stats.get("ram", 0.0)))
                ram_used = stats.get("ram_used", 0.0)
                ram_total = stats.get("ram_total", 0.0)
                if ram_used > 0.05:
                    ram_txt = f"{ram:.1f}%  {ram_used:.1f}GB"
                else:
                    ram_txt = f"{ram:.1f}%"

                draw.text((20, 266), "RAM", fill=(16, 185, 129, 255), font=self.font_main)
                draw.text((TARGET_WIDTH - 20, 266), ram_txt, fill=(226, 232, 240, 255), font=self.font_stat, anchor="ra")
                # 두툼한 10px 프로그레스 바
                bar_w = TARGET_WIDTH - 40
                fill_w = max(4, int(bar_w * (ram / 100.0)))
                draw.rounded_rectangle([20, 290, 20 + bar_w, 300], radius=4, fill=(28, 34, 46, max(40, bg_alpha)))
                draw.rounded_rectangle([20, 290, 20 + fill_w, 300], radius=4, fill=(16, 185, 129, 255))

        # 레이어 알파 블렌딩 합성
        return Image.alpha_composite(base, overlay_layer).convert("RGB")

    def encode_jpeg(self, im, quality=95, apply_tn_color_fix=True):
        # CYD TN 패널 전용 색감/감마/명암 보정 (물 빠짐 제거 -> 깊고 진한 발색)
        target_im = im
        if apply_tn_color_fix:
            arr = np.asarray(im, dtype=np.uint8)
            arr_fixed = _LUT_TABLE[arr]
            target_im = Image.fromarray(arr_fixed, mode="RGB")
            target_im = ImageEnhance.Contrast(target_im).enhance(1.08)
            target_im = ImageEnhance.Color(target_im).enhance(1.28)

        # 48KB ESP32 더블버퍼 + 고속 4:2:0(subsampling=2) 디코딩으로 애니메이션 프레임 드랍/줄밀림 최소화
        q = quality
        while q >= 50:
            buf = io.BytesIO()
            target_im.save(buf, format="JPEG", quality=q, subsampling=2, optimize=False)
            data = buf.getvalue()
            # ESP32 MAX_FRAME_SIZE(49,152B) 안전 가드
            if len(data) <= 47500:
                return data
            q -= 5
        return data

    def encode_raw_rgb565(self, im, apply_tn_color_fix=True) -> bytes:
        """정지 사진 모드용 100% 무손실 RGB565 + 4x4 Bayer 디더링 (153,600 bytes, Little-Endian)"""
        target_im = im
        if apply_tn_color_fix:
            arr = np.asarray(im, dtype=np.uint8)
            target_im = Image.fromarray(_LUT_TABLE[arr], mode="RGB")
            target_im = ImageEnhance.Contrast(target_im).enhance(1.08)
            target_im = ImageEnhance.Color(target_im).enhance(1.22)

        # 16-bit RGB565 양자화 전 4x4 Ordered Bayer 디더링 적용 (그라데이션 색 띠 제거)
        rgb_f = np.asarray(target_im, dtype=np.float32)
        r_f = np.clip(rgb_f[:, :, 0] + _BAYER_320X240 * 7.0, 0.0, 255.0).astype(np.uint16)
        g_f = np.clip(rgb_f[:, :, 1] + _BAYER_320X240 * 3.0, 0.0, 255.0).astype(np.uint16)
        b_f = np.clip(rgb_f[:, :, 2] + _BAYER_320X240 * 7.0, 0.0, 255.0).astype(np.uint16)

        r = (r_f & 0xF8) << 8
        g = (g_f & 0xFC) << 3
        b = b_f >> 3
        rgb565 = (r | g | b).astype("<u2")  # Little-Endian (ESP32 uint16_t + setSwapBytes(true) 매칭)
        return rgb565.tobytes()
