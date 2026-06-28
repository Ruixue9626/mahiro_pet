"""
copilot_watcher.py - 用獨立 thread 監聽 copilot process
"""
import os
import time
import threading
import psutil
from PyQt6.QtCore import QObject, pyqtSignal


def _find_copilot_path() -> str:
    import shutil
    p = shutil.which("copilot")
    if p:
        return os.path.realpath(p)
    for candidate in [
        os.path.expanduser("~/.local/bin/copilot"),
        "/usr/local/bin/copilot",
        "/usr/bin/copilot",
    ]:
        if os.path.exists(candidate):
            return os.path.realpath(candidate)
    return "copilot"


COPILOT_BIN = _find_copilot_path()


class CopilotWatcher(QObject):
    copilot_started = pyqtSignal()
    copilot_stopped = pyqtSignal()
    status_changed  = pyqtSignal(str)

    POLL_INTERVAL = 0.5

    def __init__(self, parent=None):
        super().__init__(parent)
        self._active   = False
        self._running  = False
        self._thread   = None

    def start(self):
        self._active = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._active = False

    def _loop(self):
        prev = False
        while self._active:
            found = self._detect_copilot()
            if found and not prev:
                self._running = True
                self.copilot_started.emit()
                self.status_changed.emit("Copilot 工作中...")
            elif not found and prev:
                self._running = False
                self.copilot_stopped.emit()
                self.status_changed.emit("待機中")
            prev = found
            time.sleep(self.POLL_INTERVAL)

    def _detect_copilot(self) -> bool:
        try:
            for proc in psutil.process_iter(["exe", "status"]):
                try:
                    exe    = proc.info["exe"] or ""
                    status = proc.info["status"] or ""
                    if status == psutil.STATUS_ZOMBIE:
                        continue
                    if exe and os.path.realpath(exe) == COPILOT_BIN:
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception:
            pass
        return False

    @property
    def is_running(self) -> bool:
        return self._running
