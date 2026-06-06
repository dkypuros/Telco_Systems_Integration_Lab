# File location: clean_5g_emulator_api/ran/rru/rru.py
# File location: clean_5g_emulator_api/ran/rru/rru.py
import time

def run_rru():
    print("RRU started")
    while True:
        print("RRU running...")
        time.sleep(60)

if __name__ == "__main__":
    run_rru()