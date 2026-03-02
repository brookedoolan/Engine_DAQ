from labjack import ljm 
import config.system_config as system_config

# aims to mirror dummy_daq.py
# will probably need to change config to fit with AINX/DIOX/EIOX

class LabJackDaq:
    
    def __init__(self, ip=None):

        # Open connection
        if ip:
            self.handle = ljm.openS("T7", "ETHERNET", ip)
        else:
            self.handle = ljm.openS("T7", "ANY", "ANY")

        print("LabJack connected.")

        # Configure AIN ranges once at startup
        for ch in system_config.PRESSURE_CHANNELS + system_config.TEMP_CHANNELS:
            ljm.eWriteName(self.handle, f"{ch}_RANGE", 10)
            ljm.eWriteName(self.handle, f"{ch}_RESOLUTION_INDEX", 1)

        # Track valves
        self.valve_states = {v: False for v in system_config.VALVES}


    # Read analog (gui expects dict)

    def read_analog(self):
        data = {}

        # Pressures
        for name, ain in system_config.PRESSURE_MAP.items():
            value = ljm.eReadName(self.handle, ain)
            data[name] = value

        # Temperatures
        for name, ain in system_config.TEMP_MAP.items():
            value = ljm.eReadName(self.handle, ain)
            data[name] = value

        # Thrust (TBC)
        for name, ain in system_config.THRUST_MAP.items():
            value = ljm.eReadName(self.handle, ain)
            data[name] = value

        return data
    
    # Digital write (gui uses valve names)
    
    def set_digital(self, name, state: bool):
        # Map names to DIO/EIO channels
        # EXAMPLEEEEEEE !!!
        if name not in system_config.VALVE_DIO_MAP:
            print(f"Unknown valve: {name}")
            return

        dio = system_config.VALVE_DIO_MAP[name]

        ljm.eWriteName(self.handle, f"{dio}_DIRECTION", 1)
        ljm.eWriteName(self.handle, dio, int(state))

        self.valve_states[name] = state

        print(f"{name} -> {'OPEN' if state else 'CLOSED'}")

    def close(self):
        ljm.close(self.handle)
        print("LabJack closed.")