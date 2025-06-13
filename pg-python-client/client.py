import psycopg2
import threading
import time

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "testdb",
    "user": "username",
    "password": "your_password"
}

NUM_THREADS = 1000
KEEP_CONNECTION_SECONDS = 30  # Keep the connection open for this duration
results = []

def connect_and_hold(index):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        result = cur.fetchone()
        results.append((index, result[0]))
        print(f"[Thread-{index}] ✅ Connected, holding for {KEEP_CONNECTION_SECONDS}s")
        time.sleep(KEEP_CONNECTION_SECONDS)
        cur.close()
        conn.close()
        print(f"[Thread-{index}] ✅ Connection closed")
    except Exception as e:
        print(f"[Thread-{index}] ❌ Error: {e}")
        results.append((index, None))

def main():
    threads = []
    for i in range(NUM_THREADS):
        t = threading.Thread(target=connect_and_hold, args=(i,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print(f"\n🎉 {len([r for r in results if r[1] is not None])} successful connections out of {NUM_THREADS}")

if __name__ == "__main__":
    main()
