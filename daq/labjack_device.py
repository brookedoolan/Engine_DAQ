from labjack import ljm
import threading
import time

class LabJackDevice:
    def __init__(self, ip, name):
        self.name = name
        self.handle = ljm.openS("T7", "ETHERNET", ip)
        print(f"{name} connected.")