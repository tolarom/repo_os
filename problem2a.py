import threading
import time
import random  # For random sleep to simulate switches

def process1():
    while True:
        print("H", end='', flush=True)
        time.sleep(random.uniform(0, 0.1))  # Simulate possible switch
        print("E", end='', flush=True)
        time.sleep(random.uniform(0, 0.1))

def process2():
    while True:
        print("L", end='', flush=True)
        time.sleep(random.uniform(0, 0.1))

def process3():
    while True:
        print("O", end='', flush=True)
        time.sleep(random.uniform(0, 0.1))

# Start threads
t1 = threading.Thread(target=process1)
t2 = threading.Thread(target=process2)
t3 = threading.Thread(target=process3)
t1.start()
t2.start()
t3.start()

time.sleep(2)  # Run for 2 seconds to see output, then it continues infinitely
# Output example from one run: HLEOEHLOL... (varies)