from PyQt6.QtCore import QThread, pyqtSignal
import time

class DAQ_Thread(QThread):
    data_ready = pyqtSignal(dict)

    def __init__(self, daq, interval_ms=100):
        super().__init__()
        self.daq = daq
        self.interval = interval_ms / 1000
        self.running = True

    def run(self):
        while self.running:
            data = self.daq.read_analog()
            self.data_ready.emit(data)
            time.sleep(self.interval)

    def stop(self):
        self.running = False
        self.wait()
