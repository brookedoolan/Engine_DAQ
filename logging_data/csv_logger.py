import csv
import os
from datetime import datetime

class CSVLogger:
    def __init__(self, headers, folder="logs_NEW", prefix="daq_log"):
        os.makedirs(folder, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.path = os.path.join(folder, f"{prefix}_{timestamp}.csv")
        self.file = open(self.path, "w", newline="")
        self.writer = csv.writer(self.file)
        self.writer.writerow(headers)

    def write_row(self, row):
        self.writer.writerow(row)

    def close(self):
        self.file.flush()
        self.file.close()
        print(f"CSV log saved to {self.path}")
