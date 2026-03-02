import numpy as np
import threading

# Circular buffer for high-rate pressure streaming
# to prevent memory blow-up, gives GUI rolling data

class CircularBuffer:
    def __init__(self, size):
        self.size = size
        self.data = np.zeros(size)
        self.index = 0
        self.lock = threading.lock()
    
    def add(self, new_data):
        with self.lock:
            for value in new_data:
                self.data[self.index] = value
                self.index = (self.index + 1) % self.size

    def get_data(self):
        with self.lock:
            return np.copy(self.data)