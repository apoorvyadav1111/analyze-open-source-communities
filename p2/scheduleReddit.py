import time
import subprocess
from datetime import datetime

def run_task(file_path, fileType = ""):
    print(f"{datetime.utcnow()} Running {file_path}...")
    try:
        subprocess.run(["python3", file_path])
    except Exception as e:
        print(f"{datetime.utcnow()} Error running test.py: {e}")

if __name__ == "__main__":
    while True:
        file_path = "./reddit/main.py"
        run_task(file_path)  # Call your Python function or code here
        print(f"{datetime.utcnow()} Run complete Reddit")
        time.sleep(15*60)  # Sleep for 60 seconds (adjust as needed)
        file_path = "./reddit/update_reddit.py"
        run_task(file_path)
        print(f"{datetime.utcnow()} Run complete Update Reddit")
        time.sleep(60)

