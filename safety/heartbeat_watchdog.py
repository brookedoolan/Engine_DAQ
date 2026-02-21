from PyQt6.QtCore import QObject, pyqtSignal
import time
import config.system_config as system_config

class HeartbeatWatchdog(QObject):
    abort_signal = pyqtSignal(str)

    def __init__(self, timeout_seconds=1.0):
        super().__init__()
        self.last_update_time = time.time()

    def beat(self):
        # Call this whenever new DAQ data arrives
        self.last_update_time = time.time()

    def check(self):
        timeout = system_config.HEARTBEAT_TIMEOUT_S
        delta = time.time() - self.last_update_time

        if delta > timeout:
            print(f"[HEARTBEAT TIMEOUT] {delta:.2f} > {timeout}s")
            self.abort_signal.emit("DAQ HEARTBEAT TIMEOUT")
        