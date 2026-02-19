import time
from PyQt6.QtCore import QThread, pyqtSignal

class IgnitionSequence(QThread):
    step_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    aborted_signal = pyqtSignal()

    def __init__(self, daq):
        super().__init__()
        self.daq = daq
        self._abort = False

    def abort(self):
        self._abort = True

    # ----- HOT FIRE SEQUENCE -----    
    def run(self):
        try:
            self._step("IGNITION_SEQUENCE_START")
            # Step 0: Close Vent Valve
            self._set_valve("Vent", False)
            self._delay(5.0) # Could maybe ask for manual input here. Say if want to wait for N2O to pressurise 

            # Step 1: Igniter ON
            self._set_valve("Ignition", True)
            self._delay(3.0)

            # Step 2: Main valve OPEN
            self._set_valve("MOV", True)
            self._delay(0.5)

            # Step 3: Igniter OFF
            self._set_valve("Ignition", False)

            self._step("IGNITION_SEQUENCE_COMPLETE")
            self.finished_signal.emit()

        except RuntimeError:
            self.aborted_signal.emit()
    
    # HELPERS
    def _delay(self, seconds):
        t0 = time.time()
        while time.time() - t0 < seconds:
            if self._abort:
                raise RuntimeError("IGNITION ABORTED")
            time.sleep(0.05)

    def _set_valve(self, name, state):
        if self._abort:
            raise RuntimeError("IGNITION ABORTED")

        self.daq.set_digital(name, state)
        self._step(f"{name}_{'ON' if state else 'OFF'}")

    def _step(self, name):
        self.step_signal.emit(name)