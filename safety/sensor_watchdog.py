from PyQt6.QtCore import QObject, pyqtSignal
import config.system_config as system_config

class SensorWatchdog(QObject):
    abort_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        # Add 3 overpressure/overtemp counts to avoid noisy data
        self.violation_counts_pressure = {}
        self.violation_counts_temp = []

    def evaluate(self, data: dict):

        # Pressure checks
        for channel, limit in system_config.PRESSURE_LIMITS.items():
            if channel in data and data[channel] > limit:
                self.violation_counts_pressure[channel] = self.violation_counts_pressure.get(channel, 0) + 1
            else:
                self.violation_counts_pressure[channel] = 0
                
            if self.violation_counts_pressure[channel] >= 3:
                self.abort_signal.emit(
                    f"{channel} OVERPRESSURE ({data[channel]:.1f} > {limit})"
                )

        # Temperature checks
        for channel, limit in system_config.TEMP_LIMITS.items():
            if channel in data and data[channel] > limit:
                self.violation_counts_temp[channel] = self.violation_counts_temp.get(channel, 0) + 1
            else:
                self.violation_counts_temp[channel] = 0
                
            if self.violation_counts_temp[channel] >= 3:
                self.abort_signal.emit(
                    f"{channel} OVERTEMP ({data[channel]:.1f} > {limit})"
                )