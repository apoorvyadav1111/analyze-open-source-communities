import time
import subprocess
from datetime import datetime
def run_task(file_path, fileType = ""):
    print(f"{datetime.utcnow()} Running {file_path}...")
    try:
        if fileType == "comments" or fileType == "updateIssues":
            for count in range(1, 4):
                subprocess.run(["python3", file_path, str(count)])
        else:
            subprocess.run(["python3", file_path])
    except Exception as e:
        print(f"{datetime.utcnow()} Error running {file_path}: {e}")

if __name__ == "__main__":
    while True:
        file_path = "./github/getIssues/getIssues.py"
        run_task(file_path)  # Call your Python function or code here
        print(f"{datetime.utcnow()} Run complete GitHub Issues")
        # time.sleep(30)  # Sleep for 60 seconds (adjust as needed)
        if datetime.now().hour % 4 != 0:
            file_path = "./github/getComments/getComments.py"
            run_task(file_path, "comments")  # Call your Python function or code here
            print(f"{datetime.utcnow()} Run complete GitHub comments")
        else:
            file_path = "./github/updateIssueStatus/updateIssues.py"
            run_task(file_path, "updateIssues")  # Call your Python function or code here
            print(f"{datetime.utcnow()} Run complete update Issues")
        time.sleep(60 * 60)  # Sleep for 60 seconds (adjust as needed)

