# File location: clean_5g_emulator_api/ptp/ptp.py
# File location: clean_5g_emulator_api/ptp/ptp.py
import time

def synchronize_clock():
    print("Synchronizing clock using PTP")
    while True:
        print("PTP synchronization in progress...")
        time.sleep(60)

if __name__ == "__main__":
    synchronize_clock()