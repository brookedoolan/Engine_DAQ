import random 
import time
 
class DummyDaq: 
    """Simulates sensors and valves.""" 
    def __init__(self): 
        self.valves = {v: False for v in ["Ox_Fill","Iso","MOV","Vent","Purge"]} 
        self.ignition = {"Ignition": False} 
        
    def read_analog(self): 
        return { 
            "Ox_tank_pressure": 500 + 5*random.random(), 
            "CC_pressure": 300 + 8*random.random(), 
            "Ox_tank_temp": 25 + 0.8*random.random(), 
            "CC_temp": 30 + 1.5*random.random(), 
            "thrust": 50 *10*random.random(), 
            "Injector_pressure": 300 - 2*random.random() 
        } 

    def set_digital(self, name, state: bool): 
        if name in self.valves: 
            self.valves[name] = state 
            print(f"[DUMMY] {name} valve -> {'OPEN' if state else 'CLOSED'}") 
        else: 
            print(f"[DUMMY] Unknown valve: {name}") 