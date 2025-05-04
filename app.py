from flask import Flask, jsonify, request, send_from_directory
import time
import psutil
import math
import multiprocessing

app = Flask(__name__)

# Check primality
def is_prime(n):
    if n <= 1:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True

# Serial implementation
def find_primes_serial(start, end):
    start_time = time.time()
    primes = [x for x in range(start, end) if is_prime(x)]
    duration = time.time() - start_time
    cpu_percent = psutil.cpu_percent(interval=None)
    return primes, duration, cpu_percent

# Worker for parallel computation
def worker(start, end, output):
    local_primes = [x for x in range(start, end) if is_prime(x)]
    output.extend(local_primes)

# Parallel implementation using multiprocessing
def find_primes_parallel(start, end):
    start_time = time.time()
    cpu_count = multiprocessing.cpu_count()
    chunk_size = (end - start) // cpu_count
    manager = multiprocessing.Manager()
    output = manager.list()
    jobs = []

    for i in range(cpu_count):
        chunk_start = start + i * chunk_size
        chunk_end = end if i == cpu_count - 1 else chunk_start + chunk_size
        p = multiprocessing.Process(target=worker, args=(chunk_start, chunk_end, output))
        jobs.append(p)
        p.start()

    for p in jobs:
        p.join()

    duration = time.time() - start_time
    cpu_percent = psutil.cpu_percent(interval=None)
    return list(output), duration, cpu_percent

# Serve the frontend
@app.route("/")
def index():
    return send_from_directory("static", "index.html")

# Benchmark route
@app.route("/run_prime_benchmark")
def run_benchmark():
    try:
        # Get range end from query parameter
        end = int(request.args.get("end", 100000))
        print(end)
        start = 1000

        # Run both versions
        serial_primes, serial_time, serial_cpu = find_primes_serial(start, end)
        parallel_primes, parallel_time, parallel_cpu = find_primes_parallel(start, end)

        return jsonify({
            "count": len(serial_primes),
            "serial_time": serial_time,
            "parallel_time": parallel_time,
            "serial_cpu": serial_cpu,
            "parallel_cpu": parallel_cpu
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run Flask app
if __name__ == "__main__":
    app.run(debug=True, port=2200)
