import random 
import config.system_config as system_config
import time
 
class DummyDaq: 
    """Simulates sensors and valves.""" 
    def __init__(self): 
        self.valves = {v: False for v in system_config.VALVES} 
        self.ignition = {"Ignition": False} 
        
    def read_analog(self): 
        data = {}
        
        # Generate 'dummy' values
        for ch in system_config.PRESSURE_CHANNELS:
            data[ch] = 300 + 10*random.random()
        
        for ch in system_config.TEMP_CHANNELS:
            data[ch] = 20 + 5*random.random()

        data["thrust"] = 20 - 5*random.random()

        return data

    def set_digital(self, name, state: bool): 
        if name in self.valves: 
            self.valves[name] = state 
            print(f"[DUMMY] {name} valve -> {'OPEN' if state else 'CLOSED'}") 
        else: 
            print(f"[DUMMY] Unknown valve: {name}") 