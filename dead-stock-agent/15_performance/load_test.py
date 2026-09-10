# -*- coding: utf-8 -*-
"""
DUST 2 DOLLAR — Synthetic Load Testing Script
Simulates concurrent decision requests against the local HTTP server.
Zero external dependencies required (uses urllib).
"""
import time
import urllib.request
import json
import threading

URL = "http://localhost:8001/api/analyze"
CONCURRENT_USERS = 10
REQUESTS_PER_USER = 5

results = []

def send_request(user_id):
    payload = json.dumps({"product_id": 1}).encode("utf-8")
    for i in range(REQUESTS_PER_USER):
        t0 = time.time()
        try:
            req = urllib.request.Request(URL, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as response:
                status = response.status
                latency = (time.time() - t0) * 1000
                results.append((status, latency))
        except Exception as e:
            results.append((500, (time.time() - t0) * 1000))

def run_load_test():
    print(f"Starting load test: {CONCURRENT_USERS} users, {REQUESTS_PER_USER} req/user (Total {CONCURRENT_USERS * REQUESTS_PER_USER} reqs)")
    threads = []
    t_start = time.time()
    for u in range(CONCURRENT_USERS):
        t = threading.Thread(target=send_request, args=(u,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    total_time = time.time() - t_start
    success_reqs = [r for r in results if r[0] == 200]
    latencies = [r[1] for r in results]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0

    print("=" * 45)
    print(f"Total Completed: {len(results)} in {total_time:.2f}s")
    print(f"Success Rate:    {len(success_reqs) / len(results) * 100:.1f}%")
    print(f"Average Latency: {avg_latency:.2f} ms")
    print(f"Throughput:      {len(results) / total_time:.1f} req/sec")
    print("=" * 45)

if __name__ == "__main__":
    run_load_test()
