# Valves 
VALVES = ['Ox_Fill', 'Iso', 'MOV', 'Vent', 'Purge', 'Ignition'] 
# Plot channels 
PRESSURE_CHANNELS = ['Ox_tank_pressure', 'CC_pressure', 'Injector_pressure', 'Fill_pressure'] 
TEMP_CHANNELS = ['Ox_tank_temp', 'CC_temp', 'Fill_temp', 'Injector_temp'] 
 
# DAQ settings 
DAQ_INTERVAL_MS = 100 
MAX_DATA_POINTS = 1000 

# SAFETY LIMITS
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

HEARTBEAT_TIMEOUT_S = 3*(DAQ_INTERVAL_MS/1000)

