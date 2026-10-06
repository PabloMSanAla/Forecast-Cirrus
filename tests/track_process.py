import argparse
import csv
from datetime import datetime
import os
import sys
import time
import psutil

def track_process(pid: int, output_file: str = "process_stats.csv", interval: float = 5.0):
    try:
        proc = psutil.Process(pid)
    except psutil.NoSuchProcess:
        print(f"Error: No process found with PID {pid}.")
        sys.exit(1)

    # Prime psutil's internal CPU measurement timer
    proc.cpu_percent(interval=None)

    file_exists = os.path.isfile(output_file)
    fields = [
        "timestamp",
        "pid",
        "name",
        "status",
        "cpu_percent",
        "rss_mb",
        "vms_mb",
        "num_threads",
        "read_bytes",
        "write_bytes",
    ]

    with open(output_file, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        if not file_exists:
            writer.writeheader()

        print(f"Tracking PID {pid} ('{proc.name()}') every {interval}s -> {output_file}")
        print("Press Ctrl+C to abort monitoring manually.\n")

        try:
            while proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE:
                time.sleep(interval)

                with proc.oneshot():
                    mem_info = proc.memory_info()
                    
                    try:
                        io_counters = proc.io_counters()
                        read_bytes = io_counters.read_bytes
                        write_bytes = io_counters.write_bytes
                    except (psutil.AccessDenied, AttributeError):
                        read_bytes, write_bytes = "N/A", "N/A"

                    row = {
                        "timestamp": datetime.now().isoformat(timespec="seconds"),
                        "pid": pid,
                        "name": proc.name(),
                        "status": proc.status(),
                        "cpu_percent": proc.cpu_percent(interval=None),
                        "rss_mb": round(mem_info.rss / (1024 * 1024), 2),
                        "vms_mb": round(mem_info.vms / (1024 * 1024), 2),
                        "num_threads": proc.num_threads(),
                        "read_bytes": read_bytes,
                        "write_bytes": write_bytes,
                    }

                writer.writerow(row)
                f.flush()  # Ensures data is written immediately to disk

        except psutil.NoSuchProcess:
            pass  # Process exited during the interval
        except KeyboardInterrupt:
            print("\nMonitoring paused/stopped by user.")
            return

    print(f"\nProcess {pid} has finished. Log finalized in '{output_file}'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Log PID metrics to CSV every N seconds.")
    parser.add_argument("pid", type=int, help="Target process PID")
    parser.add_argument("-o", "--output", default="process_stats.csv", help="Destination CSV path (default: process_stats.csv)")
    parser.add_argument("-i", "--interval", type=float, default=5.0, help="Sampling frequency in seconds (default: 5.0)")

    args = parser.parse_args()
    track_process(args.pid, args.output, args.interval)