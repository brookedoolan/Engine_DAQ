from daq.labjack_device import LabJackDevice
import config.system_config as system_config
from labjack import ljm

class DAQManager:
    def __init__(self):
        self.devices = {
            "T7": LabJackDevice(system_config.T7_IP, "T7"),
            "T7_PRO": LabJackDevice(system_config.T7_PRO_IP, "T7_PRO"),
        }

    # READ ANALOG (returns full merged dict)
    def read_analog(self):
        data = {}

        # ---- PRESSURES (T7) ----
        for name, (dev, ain) in system_config.PRESSURE_MAP.items():
            value = ljm.eReadName(self.devices[dev].handle, ain)
            data[name] = value

        # ---- TEMPS (T7_PRO) ----
        for name, (dev, ain) in system_config.TEMP_MAP.items():
            value = ljm.eReadName(self.devices[dev].handle, ain)
            data[name] = value

        # ---- THRUST (T7) ----
        for name, (dev, ain) in system_config.THRUST_MAP.items():
            value = ljm.eReadName(self.devices[dev].handle, ain)
            data[name] = value

        return data
    
    # Digital write for valves (T7 only)
    def set_digital(self, name, state: bool):

        if name not in system_config.VALVE_DIO_MAP:
            print(f"Unknown valve: {name}")
            return

        dev, dio = system_config.VALVE_DIO_MAP[name]

        ljm.eWriteName(self.devices[dev].handle, f"{dio}_DIRECTION", 1)
        ljm.eWriteName(self.devices[dev].handle, dio, int(state))


    def close(self):
        for dev in self.devices.values():
            ljm.close(dev.handle)
        print("All LabJacks closed.")