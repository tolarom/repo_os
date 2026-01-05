import threading
import time
import random

# Shared particle buffer of 100 particle slots (50 pair slots)
particle_buffer = [None] * 100

# Indices: point to particle-slot index (0..99). We always advance by 2.
in_index = 0
out_index = 0

# Semaphores and lock (initial values as described)
empty_pairs = threading.Semaphore(50)  # 50 free pair-slots (each pair uses 2 particle slots)
full_pairs = threading.Semaphore(0)    # pairs available to consumer
mutex = threading.Lock()               # protect buffer and indices (binary semaphore)

# For demonstrating correct behavior, keep small counters and prints
stop_event = threading.Event()
producer_id_counter = 0
producer_id_lock = threading.Lock()

def produce_pair_body(pid):
    """Simulate producing two particles (P1, P2)"""
    # Particle contents can be any object; here we use a tuple with producer id and local pair id
    p1 = f"P1_from_producer{pid}"
    p2 = f"P2_from_producer{pid}"
    return p1, p2

def producer(proc_num, produce_delay=0.1):
    global in_index, producer_id_counter
    while not stop_event.is_set():
        # Produce a pair (outside critical section)
        with producer_id_lock:
            pid = producer_id_counter
            producer_id_counter += 1
        p1, p2 = produce_pair_body(pid)

        # Wait for an available pair slot (ensures two consecutive free slots)
        empty_pairs.acquire()

        # Place the pair into two consecutive particle slots atomically
        with mutex:
            idx = in_index
            particle_buffer[idx] = p1
            particle_buffer[(idx + 1) % 100] = p2
            # advance by 2 (wrap around 100)
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
    # Start multiple producers and one consumer
    num_producers = 3
    producers = []
    for i in range(num_producers):
        t = threading.Thread(target=producer, args=(i, 0.05), daemon=True)
        producers.append(t)
        t.start()

    consumer_thread = threading.Thread(target=consumer, args=(0.1,), daemon=True)
    consumer_thread.start()

    # Let them run for a short while
    try:
        time.sleep(3)
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        # Give threads a moment to finish printing
        time.sleep(0.5)
        print("Stopping.")