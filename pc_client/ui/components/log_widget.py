# -*- coding: utf-8 -*-
"""
Dual-Language System Console Widget (PyQt6)
"""
import time
from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QTextEdit

class LogWidget(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(" System Console / 시스템 콘솔 ", parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 12, 6, 6)

        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)

    def log(self, en_msg: str, ko_msg: str):
        t_str = time.strftime("[%H:%M:%S] ")
        self.text_area.append(f"<span style='color:#38BDF8;'>{t_str}{en_msg}</span>")
        self.text_area.append(f"<span style='color:#10B981;'>{t_str}{ko_msg}</span>")
        self.text_area.verticalScrollBar().setValue(
            self.text_area.verticalScrollBar().maximum()
        )

