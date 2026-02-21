from PyQt6.QtCore import QObject, pyqtSignal
from safety.sensor_watchdog import SensorWatchdog
from safety.heartbeat_watchdog import HeartbeatWatchdog

# SAFETY MANAGER WRAPPER
class SafetyManager(QObject):
    abort_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.sensor_watchdog = SensorWatchdog()
        self.heartbeat_watchdog = HeartbeatWatchdog()

        # Forward abort signals to GUI
        self.sensor_watchdog.abort_signal.connect(self.abort_signal.emit)
        self.heartbeat_watchdog.abort_signal.connect(self.abort_signal.emit)

    def evaluate_sensors(self, data):
        self.sensor_watchdog.evaluate(data)

    def heartbeat(self):
        self.heartbeat_watchdog.beat()

    def check_heartbeat(self):
        self.heartbeat_watchdog.check()