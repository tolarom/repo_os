import threading
import time
import random


particle_buffer = [None] * 100


in_index = 0
out_index = 0

empty_pairs = threading.Semaphore(50) 
full_pairs = threading.Semaphore(0)    
mutex = threading.Lock()               

stop_event = threading.Event()
producer_id_counter = 0
producer_id_lock = threading.Lock()

def produce_pair_body(pid):
    """Simulate producing two particles (P1, P2)"""
    
    p1 = f"P1_from_producer{pid}"
    p2 = f"P2_from_producer{pid}"
    return p1, p2

def producer(proc_num, produce_delay=0.1):
    global in_index, producer_id_counter
    while not stop_event.is_set():
        
        with producer_id_lock:
            pid = producer_id_counter
            producer_id_counter += 1
        p1, p2 = produce_pair_body(pid)

        empty_pairs.acquire()


        with mutex:
            idx = in_index
            particle_buffer[idx] = p1
            particle_buffer[(idx + 1) % 100] = p2

            in_index = (in_index + 2) % 100
            print(f"[Producer {proc_num}] placed pair {pid} at slots {idx} & {(idx+1)%100}")

        # Signal that a full pair is available for the consumer
        full_pairs.release()

        # Simulate time between productions
        time.sleep(produce_delay * random.random())

def consumer(package_delay=0.2):
    global out_index
    while not stop_event.is_set():
        # Wait until at least one pair (i.e., two particles) are available
        full_pairs.acquire()

        # Fetch the two particles atomically
        with mutex:
            idx = out_index
            p1 = particle_buffer[idx]
            p2 = particle_buffer[(idx + 1) % 100]
            particle_buffer[idx] = None
            particle_buffer[(idx + 1) % 100] = None
            out_index = (out_index + 2) % 100
            print(f"[Consumer] fetched pair from slots {idx} & {(idx+1)%100}: ({p1}, {p2})")

        # Signal that one pair-slot (two particle slots) is free now
        empty_pairs.release()

        # Simulate packaging time
        time.sleep(package_delay * random.random())

if __name__ == "__main__":

    num_producers = 3
    producers = []
    for i in range(num_producers):
        t = threading.Thread(target=producer, args=(i, 0.05), daemon=True)
        producers.append(t)
        t.start()

    consumer_thread = threading.Thread(target=consumer, args=(0.1,), daemon=True)
    consumer_thread.start()

    try:
        time.sleep(3)
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()

        time.sleep(0.5)
        print("Stopping.")