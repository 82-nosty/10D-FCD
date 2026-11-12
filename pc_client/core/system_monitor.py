# -*- coding: utf-8 -*-
"""
System Hardware Monitor (psutil)
Collects comprehensive hardware and OS metrics for 10D FCD Themes & HUD.
"""
import time
import socket
import psutil

class SystemMonitor:
    _cached_hostname = None
    _cached_ip = None
    _last_net_check = 0
    _cached_disk = None
    _last_disk_check = 0

    @classmethod
    def _get_network_info(cls):
        now = time.time()
        if cls._cached_hostname is None or (now - cls._last_net_check > 30.0):
            try:
                cls._cached_hostname = socket.gethostname()
                cls._cached_ip = socket.gethostbyname(cls._cached_hostname)
            except Exception:
                cls._cached_hostname = "10D-PC"
                cls._cached_ip = "127.0.0.1"
            cls._last_net_check = now
        return cls._cached_hostname, cls._cached_ip

    @classmethod
    def _get_disk_info(cls):
        now = time.time()
        if cls._cached_disk is None or (now - cls._last_disk_check > 5.0):
            try:
                du = psutil.disk_usage("C:\\")
                cls._cached_disk = {
                    "percent": du.percent,
                    "used_gb": du.used / (1024 ** 3),
                    "total_gb": du.total / (1024 ** 3),
                    "free_gb": du.free / (1024 ** 3)
                }
            except Exception:
                try:
                    du = psutil.disk_usage("/")
                    cls._cached_disk = {
                        "percent": du.percent,
                        "used_gb": du.used / (1024 ** 3),
                        "total_gb": du.total / (1024 ** 3),
                        "free_gb": du.free / (1024 ** 3)
                    }
                except Exception:
                    cls._cached_disk = {"percent": 0.0, "used_gb": 0.0, "total_gb": 0.0, "free_gb": 0.0}
            cls._last_disk_check = now
        return cls._cached_disk

    @classmethod
    def get_stats(cls):
        cpu = psutil.cpu_percent(interval=None)

        cpu_freq_ghz = 0.0
        cpu_freq_mhz = 0.0
        try:
            freq = psutil.cpu_freq()
            if freq and freq.current:
                cpu_freq_mhz = freq.current
                cpu_freq_ghz = freq.current / 1000.0
        except Exception:
            pass

        vm = psutil.virtual_memory()
        ram = vm.percent
        ram_used_gb = vm.used / (1024 ** 3)
        ram_total_gb = vm.total / (1024 ** 3)
        ram_free_gb = vm.available / (1024 ** 3)
        ram_used_mb = vm.used / (1024 ** 2)
        ram_total_mb = vm.total / (1024 ** 2)

        hostname, ip = cls._get_network_info()
        disk_info = cls._get_disk_info()

        now_t = time.localtime()
        days_ko = ["월", "화", "수", "목", "금", "토", "일"]
        days_en = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        day_ko = days_ko[now_t.tm_wday]
        day_en = days_en[now_t.tm_wday]

        return {
            "cpu": cpu,
            "cpu_freq": cpu_freq_ghz,
            "cpu_freq_mhz": cpu_freq_mhz,
            "cpu_cores": psutil.cpu_count(logical=True) or 1,
            "cpu_cores_phys": psutil.cpu_count(logical=False) or 1,
            "ram": ram,
            "ram_used": ram_used_gb,
            "ram_total": ram_total_gb,
            "ram_free_gb": ram_free_gb,
            "ram_used_mb": ram_used_mb,
            "ram_total_mb": ram_total_mb,
            "disk": disk_info["percent"],
            "disk_used_gb": disk_info["used_gb"],
            "disk_total_gb": disk_info["total_gb"],
            "disk_free_gb": disk_info["free_gb"],
            "hostname": hostname,
            "ip": ip,
            "time": time.strftime("%H:%M:%S", now_t),
            "date": time.strftime("%Y.%m.%d", now_t),
            "hour_24": time.strftime("%H", now_t),
            "hour_12": time.strftime("%I", now_t),
            "min": time.strftime("%M", now_t),
            "sec": time.strftime("%S", now_t),
            "year": time.strftime("%Y", now_t),
            "year_short": time.strftime("%y", now_t),
            "month": time.strftime("%m", now_t),
            "day": time.strftime("%d", now_t),
            "ampm": time.strftime("%p", now_t),
            "day_ko": day_ko,
            "day_en": day_en
        }
