# -*- coding: utf-8 -*-
"""
10D FCD - Serial Manager for ESP32 UART Communication
"""
import time
import threading
import serial
import serial.tools.list_ports
from PyQt6.QtCore import QObject, pyqtSignal
from core.i18n import I18nManager, LANG_KO


class SerialManager(QObject):
    log_signal = pyqtSignal(str, str)
    error_signal = pyqtSignal(str, str)  # (title, detail_msg) -> UI 팝업용
    wifi_connected_signal = pyqtSignal(str)
    scan_result_signal = pyqtSignal(list)
    wifi_profiles_signal = pyqtSignal(list)
    busy_signal = pyqtSignal(bool)

    def __init__(self, baudrate=921600):
        super().__init__()
        self.baudrate = baudrate
        self.ser = None

    @property
    def is_open(self) -> bool:
        return bool(self.ser and self.ser.is_open)

    @staticmethod
    def list_ports():
        return [p.device for p in serial.tools.list_ports.comports()]

    def connect_port(self, port):
        if self.ser and self.ser.is_open:
            self.ser.close()
        try:
            self.ser = serial.Serial(port, self.baudrate, timeout=1)
            self.log_signal.emit(f"Serial port {port} opened.", f"시리얼 포트 {port}가 정상 연결되었습니다.")
            return True
        except Exception as e:
            err_msg = str(e)
            self.log_signal.emit(f"Failed to open port {port}: {err_msg}", f"포트 {port} 연결 실패: {err_msg}")
            is_ko = I18nManager.get_lang() == LANG_KO
            title = "시리얼 포트 연결 실패" if is_ko else "Serial Connection Failed"
            detail = (
                f"[{port}] 포트에 연결할 수 없습니다.\n\n"
                f"• 올바른 쿨러(USB-UART) 포트인지 확인하세요. (보통 COM3~COM9)\n"
                f"• 다른 프로그램(아두이노 등)이 포트를 사용 중이면 닫아주세요.\n\n"
                f"오류 상세: {err_msg}"
            ) if is_ko else (
                f"Cannot open [{port}].\n\n"
                f"• Verify it is the correct ESP32 USB-UART port.\n"
                f"• Close any other app using this port.\n\n"
                f"Details: {err_msg}"
            )
            self.error_signal.emit(title, detail)
            return False

    def disconnect_port(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.ser = None
            self.log_signal.emit("Serial port disconnected.", "시리얼 포트 연결 해제됨.")

    def is_connected(self):
        return self.ser is not None and self.ser.is_open

    def set_device_language(self, lang):
        """ESP32 기기로 언어 변경 명령 전송 (SET_LANG:KO 또는 SET_LANG:EN)"""
        if not self.is_connected():
            return
        try:
            cmd = f"SET_LANG:{lang}\n"
            self.ser.write(cmd.encode('utf-8'))
            self.log_signal.emit(f"Device language set to {lang}.", f"기기 언어가 {lang} 모드로 변경되었습니다.")
        except Exception as e:
            self.log_signal.emit(f"Failed to set language: {e}", f"기기 언어 설정 실패: {e}")

    def set_device_flip(self, flip: bool):
        """ESP32 기기로 180도 화면 회전 명령 전송 (SET_FLIP:1 또는 SET_FLIP:0)"""
        if not self.is_connected():
            return
        try:
            cmd = f"SET_FLIP:{1 if flip else 0}\n"
            self.ser.write(cmd.encode('utf-8'))
            self.log_signal.emit(
                f"Device rotation sent: {'180 Flip' if flip else '0 Normal'}.",
                f"기기 화면 회전 명령 전송: {'180도 반전' if flip else '정방향'} (기기 NVS 영구 저장)"
            )
        except Exception as e:
            self.log_signal.emit(f"Failed to set flip: {e}", f"기기 회전 설정 실패: {e}")

    def sync_device_time(self):
        """PC의 현재 로컬 타임스탬프를 기기로 전송하여 NTP 차단 환경에서도 완벽한 시계 보정"""
        if not self.is_connected():
            return
        try:
            now_epoch = int(time.time())
            cmd = f"SET_TIME:{now_epoch}\n"
            self.ser.write(cmd.encode('utf-8'))
            self.log_signal.emit(f"PC time synced to device: {now_epoch}", "PC 시스템 시간이 기기와 동기화되었습니다.")
        except Exception as e:
            self.log_signal.emit(f"Time sync error: {e}", f"시간 동기화 오류: {e}")

    def query_device_ip(self):
        """ESP32에 현재 할당된 Wi-Fi IP 조회 요청"""
        if not self.is_connected():
            return
        try:
            self.ser.reset_input_buffer()
            self.ser.write(b"GET_IP\n")
            start = time.time()
            while time.time() - start < 1.5:
                line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                if line.startswith("WIFI_IP:"):
                    ip = line[8:].strip()
                    if ip and ip != "0.0.0.0":
                        self.wifi_connected_signal.emit(ip)
                        self.log_signal.emit(f"Device IP synced: {ip}", f"기기 IP 동기화 완료: {ip}")
                    return
        except Exception:
            pass

    def query_wifi_profiles(self):
        """ESP32 NVS에 저장된 다중 Wi-Fi 프로필 목록 조회"""
        if not self.is_connected():
            return

        def _query_thread():
            try:
                self.ser.reset_input_buffer()
                self.ser.write(b"GET_WIFI_PROFILES\n")
                start = time.time()
                while time.time() - start < 2.0:
                    line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    if line.startswith("WIFI_PROFILES:"):
                        payload = line[14:].strip()
                        profiles = []
                        if payload:
                            items = payload.split(";")
                            for it in items:
                                parts = it.split("|")
                                if len(parts) >= 2:
                                    profiles.append({
                                        "ssid": parts[0],
                                        "type": parts[1],
                                        "id": parts[2] if len(parts) > 2 else ""
                                    })
                        self.wifi_profiles_signal.emit(profiles)
                        self.log_signal.emit(f"Fetched {len(profiles)} saved Wi-Fi profiles from ESP32.",
                                             f"기기에 저장된 {len(profiles)}개의 Wi-Fi 프로필 목록을 불러왔습니다.")
                        return
            except Exception as e:
                self.log_signal.emit(f"Failed to fetch profiles: {e}", f"프로필 조회 실패: {e}")

        threading.Thread(target=_query_thread, daemon=True).start()

    def delete_wifi_profile(self, ssid: str):
        """ESP32 NVS에서 특정 Wi-Fi 프로필 삭제"""
        if not self.is_connected():
            return
        try:
            cmd = f"DEL_WIFI_PROFILE:{ssid}\n"
            self.ser.write(cmd.encode('utf-8'))
            self.log_signal.emit(f"Requested deletion of profile [{ssid}] from ESP32.",
                                 f"기기에서 [{ssid}] Wi-Fi 프로필 삭제를 요청했습니다.")
            # 삭제 후 목록 새로고침
            threading.Timer(0.3, self.query_wifi_profiles).start()
        except Exception as e:
            self.log_signal.emit(f"Delete profile error: {e}", f"프로필 삭제 오류: {e}")

    def scan_wifi(self):
        if not self.is_connected():
            is_ko = I18nManager.get_lang() == LANG_KO
            self.error_signal.emit(
                "시리얼 연결 필요" if is_ko else "Serial Required",
                "먼저 상단에서 쿨러 USB 포트(COM)를 연결해 주세요." if is_ko else "Please connect the USB Serial port first."
            )
            return

        def _scan_thread():
            self.busy_signal.emit(True)
            self.log_signal.emit("Requesting Wi-Fi scan from ESP32...", "ESP32에 주변 와이파이 검색 요청 전송 중...")
            try:
                self.ser.reset_input_buffer()
                self.ser.write(b"SCAN\n")

                start = time.time()
                while time.time() - start < 8.0:
                    line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    if line.startswith("SCAN_RESULT:"):
                        aps = [s.strip() for s in line[12:].split(',') if s.strip()]
                        aps = list(dict.fromkeys(aps))
                        self.scan_result_signal.emit(aps)
                        self.log_signal.emit(f"Scan complete. Found {len(aps)} networks.", f"스캔 완료: 총 {len(aps)}개 와이파이 발견.")
                        self.busy_signal.emit(False)
                        return

                self.log_signal.emit("Wi-Fi scan timed out.", "와이파이 스캔 응답 시간 초과.")
                is_ko = I18nManager.get_lang() == LANG_KO
                self.error_signal.emit(
                    "Wi-Fi 스캔 실패" if is_ko else "Wi-Fi Scan Timeout",
                    "기기로부터 와이파이 스캔 응답이 없습니다. USB 연결 상태를 확인해 주세요." if is_ko else "No scan response from device. Check USB connection."
                )
            except Exception as e:
                self.log_signal.emit(f"Scan error: {e}", f"스캔 중 오류: {e}")
                is_ko = I18nManager.get_lang() == LANG_KO
                self.error_signal.emit("스캔 오류" if is_ko else "Scan Error", str(e))
            finally:
                self.busy_signal.emit(False)

        threading.Thread(target=_scan_thread, daemon=True).start()

    def connect_wifi(self, ssid, password):
        if not self.is_connected():
            return

        def _connect_thread():
            self.busy_signal.emit(True)
            self.log_signal.emit(f"Connecting ESP32 to {ssid}...", f"ESP32에 {ssid} 연결 요청 전송 중...")
            is_ko = I18nManager.get_lang() == LANG_KO
            try:
                self.ser.reset_input_buffer()
                cmd = f"CONNECT:{ssid},{password}\n"
                self.ser.write(cmd.encode('utf-8'))

                start = time.time()
                while time.time() - start < 25.0:
                    line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    if line.startswith("WIFI_CONNECTED:"):
                        ip = line.split(":", 1)[1].strip()
                        self.wifi_connected_signal.emit(ip)
                        self.log_signal.emit(f"Wi-Fi connected. IP: {ip}", f"와이파이 연결 성공. 기기 IP: {ip}")
                        self.busy_signal.emit(False)
                        return
                    elif line == "WIFI_FAIL":
                        self.log_signal.emit("Wi-Fi connection failed.", "와이파이 접속 실패. 비밀번호 확인 필요.")
                        self.error_signal.emit(
                            "공유기 연결 실패" if is_ko else "Wi-Fi Connection Failed",
                            f"[{ssid}] 공유기에 접속하지 못했습니다.\n\n• 비밀번호가 정확한지 확인하세요.\n• 2.4GHz 와이파이인지 확인하세요. (ESP32는 5GHz 전용 AP 미지원)" if is_ko
                            else f"Failed to join [{ssid}].\n\n• Check password.\n• Ensure it is a 2.4GHz network."
                        )
                        self.busy_signal.emit(False)
                        return

                self.log_signal.emit("Wi-Fi connection timed out.", "공유기 연결 응답 시간 초과.")
                self.error_signal.emit(
                    "연결 시간 초과" if is_ko else "Connection Timeout",
                    "공유기 접속 응답이 없습니다. 기기 화면 상태를 확인해 주세요." if is_ko else "No response during Wi-Fi connection."
                )
            except Exception as e:
                self.log_signal.emit(f"Wi-Fi setup error: {e}", f"와이파이 설정 오류: {e}")
                self.error_signal.emit("와이파이 설정 오류" if is_ko else "Wi-Fi Setup Error", str(e))
            finally:
                self.busy_signal.emit(False)

        threading.Thread(target=_connect_thread, daemon=True).start()

    def connect_wifi_eap(self, ssid, identity, password):
        if not self.is_connected():
            return

        def _connect_eap_thread():
            self.busy_signal.emit(True)
            self.log_signal.emit(f"Connecting ESP32 to EAP {ssid} (ID: {identity})...",
                                 f"ESP32에 교내 와이파이 {ssid} (ID: {identity}) 연결 요청 전송 중...")
            is_ko = I18nManager.get_lang() == LANG_KO
            try:
                self.ser.reset_input_buffer()
                cmd = f"CONNECT_EAP:{ssid},{identity},{password}\n"
                self.ser.write(cmd.encode('utf-8'))

                start = time.time()
                while time.time() - start < 30.0:
                    line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    if line.startswith("WIFI_CONNECTED:"):
                        ip = line.split(":", 1)[1].strip()
                        self.wifi_connected_signal.emit(ip)
                        self.log_signal.emit(f"Enterprise Wi-Fi connected. IP: {ip}", f"엔터프라이즈 와이파이 연결 성공. 기기 IP: {ip}")
                        self.busy_signal.emit(False)
                        return
                    elif line == "WIFI_FAIL":
                        self.log_signal.emit("EAP Wi-Fi connection failed.", "엔터프라이즈 와이파이 접속 실패. ID/PW 확인 필요.")
                        self.error_signal.emit(
                            "와이파이 연결 실패" if is_ko else "EAP Connection Failed",
                            f"[{ssid}] 네트워크에 접속하지 못했습니다.\n\n• 아이디와 비밀번호가 일치하는지 확인하세요.\n• 해당 AP가 2.4GHz를 지원하는지 확인하세요." if is_ko
                            else f"Failed to join [{ssid}].\n\n• Check your Identity and Password.\n• Ensure 2.4GHz is supported."
                        )
                        self.busy_signal.emit(False)
                        return

                self.log_signal.emit("EAP Wi-Fi connection timed out.", "엔터프라이즈 와이파이 연결 응답 시간 초과.")
                self.error_signal.emit(
                    "연결 시간 초과" if is_ko else "Connection Timeout",
                    "교내 와이파이 접속 응답이 없습니다. 기기 화면 상태를 확인해 주세요." if is_ko else "No response during Enterprise Wi-Fi connection."
                )
            except Exception as e:
                self.log_signal.emit(f"EAP setup error: {e}", f"교내 와이파이 설정 오류: {e}")
                self.error_signal.emit("와이파이 설정 오류" if is_ko else "Wi-Fi Setup Error", str(e))
            finally:
                self.busy_signal.emit(False)

        threading.Thread(target=_connect_eap_thread, daemon=True).start()
