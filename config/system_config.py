# Device IPs
T7_IP = "192.168.1.207"
T7_PRO_IP = "192.168.1.208"

# Valves T7
VALVES = ['Ox_Fill', 
          'Iso', 
          'MOV', 
          'Vent', 
          'Purge', 
          'Ignition'] 

VALVE_DIO_MAP = {
    "MOV": ("T7", "DIO0"),
    "Vent": ("T7", "DIO1"),
    "Ignition": ("T7", "DIO2")
}

# T7 Sensor Channels (Pressure and load cells)
PRESSURE_CHANNELS = ['Ox_tank_pressure', 
                     'CC_pressure', 
                     'Injector_pressure', 
                     'Fill_pressure'] 

PRESSURE_MAP = {
    "Ox_tank_pressure": ("T7", "AIN0"),
    "CC_Pressure": ("T7", "AIN1"),
}

THRUST_MAP = {
    "thrust": ("T7", "AIN2")
}


# T7-Pro Sensor Channels (Temperatures)
TEMP_CHANNELS = ['Ox_tank_temp', 
                 'CC_temp', 
                 'Fill_temp', 
                 'Injector_temp'] 
 
TEMP_MAP = {
    "Ox_tank_temp": ("T7_PRO", "AIN0"),
    "CC_temp": ("T7_PRO", "AIN1"),
}

# DAQ settings 
DAQ_INTERVAL_MS = 100 
MAX_DATA_POINTS = 1000 


# Safety limits
PRESSURE_LIMITS = {
    "Ox_tank_pressure": 800,
    "CC_pressure": 600,
    "Injector_pressure": 650,
}

TEMP_LIMITS = {
    "Ox_tank_temp": 50,
    "CC_temp": 200,
    "Injector_temp": 120,
    "Fill_temp": 60,
}

HEARTBEAT_TIMEOUT_S = 1.0

# Safe valve states
DIO_SAFE_STATES = {
    "MOV": False,
    "Vent": False,
    "Ignition": False
}
