import json
import time
import os

class AcidLogger:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.log_file = os.path.join(log_dir, f"run_{int(time.time())}.jsonl")

    def log(self, event: dict):
        event["timestamp"] = time.time()
        with open(self.log_file, "a") as f:
            f.write(json.dumps(event) + "\n")