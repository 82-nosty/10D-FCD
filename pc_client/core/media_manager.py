# -*- coding: utf-8 -*-
"""
10D FCD - High-Quality Media, MP4 Video & Virtual Display Screen Capture Manager
Portrait 240x320 (3:4) with LANCZOS Resampling & Color/Contrast Enhancement
"""
import os
import threading
import cv2
import mss
from PIL import Image, ImageSequence, ImageOps, ImageFilter
from config import TARGET_WIDTH, TARGET_HEIGHT


class MediaManager:
    VIDEO_EXTS = (".mp4", ".avi", ".mov", ".mkv", ".webm", ".wmv", ".m4v")

    def __init__(self):
        self.frames = []
        self.delays = []
        self.is_animated = False
        self.current_index = 0
        self.file_name = "None"
        self.file_type = "NONE"  # IMAGE | GIF | VIDEO

        # MP4 스트리밍 캡처
        self.video_cap = None
        self.video_fps = 24.0

        # 화면/가상 디스플레이 캡처 (스레드 안전 로컬)
        self._thread_local = threading.local()
        self.selected_monitor_idx = 1  # mss index (1 = Primary, 2 = Secondary...)
        self.fit_mode = "COVER"  # COVER (3:4 꽉 채우기 크롭) | CONTAIN (전체 축소 레터박스)
        self.enhance_color = True

    def _fit_to_lcd(self, pil_img: Image.Image) -> Image.Image:
        """비율을 유지하면서 240x320 (3:4) LCD에 최고 화질(LANCZOS)로 맞춤"""
        if pil_img.mode != "RGB":
            if pil_img.mode in ("RGBA", "LA", "P"):
                rgba = pil_img.convert("RGBA")
                bg = Image.new("RGB", rgba.size, (0, 0, 0))
                bg.paste(rgba, mask=rgba.split()[3])
                pil_img = bg
            else:
                pil_img = pil_img.convert("RGB")

        if self.fit_mode == "CONTAIN":
            # 전체 화면이 다 보이도록 비율 유지 축소 + 검정 레터박스
            out = ImageOps.pad(
                pil_img, (TARGET_WIDTH, TARGET_HEIGHT),
                method=Image.Resampling.LANCZOS, color=(0, 0, 0)
            )
        else:
            # 3:4 비율로 중앙 크롭하여 화면 꽉 채우기
            out = ImageOps.fit(
                pil_img, (TARGET_WIDTH, TARGET_HEIGHT),
                method=Image.Resampling.LANCZOS
            )

        if self.enhance_color and self.file_type == "IMAGE":
            # 정지 사진 모드에서만 Unsharp Mask 선명화 적용 (연속 영상/가상화면은 최고 FPS 우선)
            out = out.filter(ImageFilter.UnsharpMask(radius=1.0, percent=110, threshold=3))

        return out

    def release_video(self):
        if self.video_cap is not None:
            try:
                self.video_cap.release()
            except Exception:
                pass
            self.video_cap = None

    def load_file(self, path: str):
        if not os.path.exists(path):
            return False, "File does not exist."

        self.release_video()
        self.frames = []
        self.delays = []
        self.file_name = os.path.basename(path)
        ext = os.path.splitext(path)[1].lower()

        # 1. MP4 / 동영상 파일 처리
        if ext in self.VIDEO_EXTS:
            try:
                cap = cv2.VideoCapture(path)
                if not cap.isOpened():
                    return False, "Failed to open video file."
                self.video_cap = cap
                fps = cap.get(cv2.CAP_PROP_FPS)
                self.video_fps = fps if (fps and 1 <= fps <= 120) else 24.0
                self.file_type = "VIDEO"
                self.is_animated = True
                total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                return True, f"Video ({total} frames, {self.video_fps:.1f} FPS)"
            except Exception as e:
                return False, str(e)

        # 2. 이미지 / GIF 처리
        try:
            im = Image.open(path)
            if getattr(im, "is_animated", False):
                self.is_animated = True
                self.file_type = "GIF"
                for f in ImageSequence.Iterator(im):
                    frame_rgb = self._fit_to_lcd(f)
                    d = f.info.get("duration", 50)
                    if d <= 0:
                        d = 50
                    self.frames.append(frame_rgb)
                    self.delays.append(d / 1000.0)
            else:
                self.is_animated = False
                self.file_type = "IMAGE"
                frame_rgb = self._fit_to_lcd(im)
                self.frames.append(frame_rgb)
                self.delays.append(1.0)

            self.current_index = 0
            return True, f"Loaded {len(self.frames)} frames"
        except Exception as e:
            return False, str(e)

    def get_next_frame(self):
        # 동영상 실시간 디코딩
        if self.file_type == "VIDEO" and self.video_cap is not None:
            ret, bgr = self.video_cap.read()
            if not ret:
                # 영상 끝에 도달하면 처음부터 무한 루프 재생
                self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, bgr = self.video_cap.read()
                if not ret:
                    return None
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb)
            return self._fit_to_lcd(pil_img)

        # 이미지 / GIF
        if not self.frames:
            return None
        frame = self.frames[self.current_index].copy()
        if self.is_animated:
            self.current_index = (self.current_index + 1) % len(self.frames)
        return frame

    # =========================================================================
    # 가상 디스플레이 & 멀티 모니터 초고속 캡처 (mss)
    # =========================================================================
    @staticmethod
    def list_monitors():
        """연결된 모든 모니터(가상 디스플레이 포함) 목록 반환"""
        monitors = []
        with mss.mss() as sct:
            # index 0은 전체 합산 화면, 1부터 개별 모니터
            for idx, m in enumerate(sct.monitors[1:], start=1):
                w, h = m["width"], m["height"]
                ratio = "3:4 Portrait" if abs((w / max(1, h)) - 0.75) < 0.05 else f"{w}x{h}"
                monitors.append({
                    "index": idx,
                    "width": w,
                    "height": h,
                    "label": f"Display {idx} ({w} × {h}) {'[3:4 최적화]' if '3:4' in ratio else ''}"
                })
        return monitors

    def capture_screen_frame(self) -> Image.Image:
        """선택된 모니터(또는 가상 디스플레이)를 캡처하여 240x320 고화질 프레임 반환"""
        try:
            if not hasattr(self._thread_local, "sct"):
                self._thread_local.sct = mss.mss()
            sct = self._thread_local.sct

            monitors = sct.monitors
            idx = self.selected_monitor_idx
            if idx < 1 or idx >= len(monitors):
                idx = 1

            raw = sct.grab(monitors[idx])
            pil_img = Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")
            return self._fit_to_lcd(pil_img)
        except Exception:
            return Image.new("RGB", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0))
