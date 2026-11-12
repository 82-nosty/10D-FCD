# -*- coding: utf-8 -*-
"""
High-Speed TCP Socket Streamer Worker (PyQt6 QThread)
"""
import time
import socket
import struct
from PyQt6.QtCore import QThread, pyqtSignal
from config import MAGIC_HEADER, DEFAULT_TCP_PORT

class StreamWorker(QThread):
    log_signal = pyqtSignal(str, str)
    stat_signal = pyqtSignal(float, float)  # fps, kbps
    frame_preview_signal = pyqtSignal(object)  # PIL Image
    connect_failed_signal = pyqtSignal(str)
    stopped_signal = pyqtSignal()

    def __init__(self, ip, port, media_manager, overlay_engine, settings, theme_engine=None):
        super().__init__()
        self.ip = ip
        self.port = port
        self.media_manager = media_manager
        self.overlay_engine = overlay_engine
        self.settings = settings
        self.theme_engine = theme_engine
        self.running = False
        self._wake_flag = False
        self._cmd_queue = []

    def send_command(self, cmd_str: str):
        """기기로 VCMD 제어 패킷 큐잉 (예: FLIP:1, FLIP:0)"""
        self._cmd_queue.append(cmd_str)
        self._wake_flag = True

    def notify_settings_changed(self):
        self._wake_flag = True

    def stop(self):
        self.running = False
        self._wake_flag = True

    def _connect_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)  # 무선 Wi-Fi 지연 대응 5초 타임아웃
        sock.connect((self.ip, self.port))
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        return sock

    def run(self):
        self.log_signal.emit(f"Connecting to CYD ({self.ip}:{self.port})...",
                             f"기기 TCP 소켓({self.ip}:{self.port})에 연결 중...")
        try:
            sock = self._connect_socket()
            self.log_signal.emit("Connected! Wireless streaming started.",
                                 "CYD 기기 연결 완료. 고속 무선 스트리밍을 시작합니다.")
            # 연결 즉시 하드웨어 회전 상태(NVS 동기화) 패킷 전송 및 전용 ACK 수거
            flip_state = self.settings.get("flip_180", False)
            init_cmd = f"FLIP:{1 if flip_state else 0}".encode('ascii')
            cmd_pkt = b'VCMD' + struct.pack('>I', len(init_cmd)) + init_cmd
            try:
                sock.sendall(cmd_pkt)
                sock.settimeout(1.5)
                sock.recv(1)  # VCMD 처리 완료 ACK('K') 안전 수거
                sock.settimeout(5.0)
            except Exception:
                sock.settimeout(5.0)
        except Exception as e:
            self.log_signal.emit(f"Connection failed: {e}", f"연결 실패: {e}")
            self.connect_failed_signal.emit(str(e))
            self.stopped_signal.emit()
            return

        self.running = True
        reconnect_attempts = 0
        max_reconnects = 5
        in_flight = 0
        fps_counter = 0
        byte_counter = 0
        fps_timer = time.time()
        start_time = time.time()

        from core.system_monitor import SystemMonitor

        while self.running:
            # 0. 큐잉된 제어 명령 패킷 전송 (FLIP, LANG 등) 및 전용 ACK 수거
            while self._cmd_queue:
                cmd_item = self._cmd_queue.pop(0)
                cmd_bytes = cmd_item.encode('ascii')
                pkt = b'VCMD' + struct.pack('>I', len(cmd_bytes)) + cmd_bytes
                try:
                    sock.sendall(pkt)
                    sock.settimeout(1.5)
                    sock.recv(1)  # VCMD 전용 ACK 수거
                    sock.settimeout(5.0)
                except Exception:
                    sock.settimeout(5.0)

            target_fps = self.settings.get("fps", 20)
            quality = self.settings.get("quality", 75)
            frame_interval = 1.0 / target_fps
            loop_start = time.time()

            # 1. 미디어 프레임 획득
            mode = self.settings.get("mode", "DEMO")
            current_fps = fps_counter / max(0.1, time.time() - fps_timer)
            stats = SystemMonitor.get_stats()

            if mode == "SCREEN":
                frame = self.media_manager.capture_screen_frame()
            elif mode == "FILE":
                frame = self.media_manager.get_next_frame()
                if frame is None:
                    if self.theme_engine and self.theme_engine.current_theme:
                        frame = self.theme_engine.render_theme_frame(time.time() - start_time, stats, current_fps)
                    else:
                        frame = self.overlay_engine.generate_demo_frame(time.time() - start_time)
            else:
                # DEMO 모드: 선택된 디자인 테마 렌더링
                if self.theme_engine and self.theme_engine.current_theme:
                    frame = self.theme_engine.render_theme_frame(time.time() - start_time, stats, current_fps)
                else:
                    frame = self.overlay_engine.generate_demo_frame(time.time() - start_time)

            # 2. 오버레이 합성 (FILE/SCREEN 모드에서 hud_on_media 토글 시에만 표시)
            show_hud = (mode != "DEMO") and bool(self.settings.get("hud_on_media", False))
            if show_hud:
                hud_opacity = int(self.settings.get("hud_alpha", 190))
                frame = self.overlay_engine.apply_overlay(
                    frame, stats,
                    show_cpu=self.settings.get("show_cpu", True),
                    show_ram=self.settings.get("show_ram", True),
                    show_time=self.settings.get("show_time", True),
                    show_fps=self.settings.get("show_fps", True),
                    fps_val=current_fps,
                    hud_alpha=hud_opacity
                )

            # 3. 인코딩: 정지 사진(IMAGE)은 100% 무손실 RAW RGB565 ('VRAW'), 영상/GIF/데모는 고속 4:4:4 JPEG ('VLIF')
            is_static_image = (mode == "FILE" and self.media_manager.file_type == "IMAGE")
            if is_static_image:
                payload_bytes = self.overlay_engine.encode_raw_rgb565(frame)
                magic = b'VRAW'
                # 최적 새로고침 주기: HUD 표시 시 1.0초(시계/점유율 동기화), 순수 사진 시 5.0초(유휴 부하 최소화)
                frame_interval = 1.0 if show_hud else 5.0
            else:
                payload_bytes = self.overlay_engine.encode_jpeg(frame, quality=quality)
                magic = MAGIC_HEADER

            frame_len = len(payload_bytes)

            # 4. 프로토콜 전송: Magic (4B) + Len (4B) + Data
            header = magic + struct.pack('>I', frame_len)
            try:
                sock.sendall(header + payload_bytes)
                if is_static_image:
                    # RAW 프레임은 즉시 ACK 수거
                    while in_flight > 0:
                        if not sock.recv(1):
                            raise ConnectionError("Device disconnected")
                        in_flight -= 1
                    ack = sock.recv(1)
                    if not ack:
                        raise ConnectionError("Device disconnected")
                else:
                    in_flight += 1
                    if in_flight >= 2:
                        ack = sock.recv(1)
                        if not ack:
                            raise ConnectionError("Device disconnected")
                        in_flight -= 1
                byte_counter += len(header) + frame_len
                fps_counter += 1
                reconnect_attempts = 0
            except Exception as e:
                if not self.running:
                    break
                reconnect_attempts += 1
                if reconnect_attempts > max_reconnects:
                    self.log_signal.emit(f"Transmission error: {e}", f"패킷 전송 오류 발생: {e}")
                    break
                self.log_signal.emit(
                    f"Connection dropped ({e}), reconnecting ({reconnect_attempts}/{max_reconnects})...",
                    f"연결 일시 끊김({e}) - 자동 재연결 시도 ({reconnect_attempts}/{max_reconnects})..."
                )
                try:
                    sock.close()
                except Exception:
                    pass
                time.sleep(0.5)
                if not self.running:
                    break
                try:
                    sock = self._connect_socket()
                    in_flight = 0
                    self.log_signal.emit("Reconnected! Resuming stream.", "재연결 성공! 스트리밍을 이어서 진행합니다.")
                    continue
                except Exception:
                    continue

            # 5. UI 미리보기 전송 (정지 사진은 매번, 애니메이션은 매 4프레임마다 - GUI 부하 최소화)
            if is_static_image or fps_counter % 4 == 0:
                self.frame_preview_signal.emit(frame)

            # 통계 계산
            now = time.time()
            if now - fps_timer >= 1.0:
                cur_fps = fps_counter / (now - fps_timer)
                cur_kbps = (byte_counter / 1024.0) / (now - fps_timer)
                self.stat_signal.emit(cur_fps, cur_kbps)
                fps_counter = 0
                byte_counter = 0
                fps_timer = now

            # FPS 동기화 (중지 및 실시간 설정 변경 시 즉시 반응하도록 0.05초 단위로 분할 대기)
            self._wake_flag = False
            elapsed = time.time() - loop_start
            sleep_time = frame_interval - elapsed
            while sleep_time > 0 and self.running and not self._wake_flag:
                step = min(0.05, sleep_time)
                time.sleep(step)
                sleep_time -= step

        try:
            sock.close()
        except:
            pass

        self.running = False
        self.stopped_signal.emit()
        self.log_signal.emit("Stream session finished.", "스트리밍 세션이 종료되었습니다.")

