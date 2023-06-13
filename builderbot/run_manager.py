import os
import pandas as pd
import datetime

class RunManager():
    file = "runs.txt"

    def __init__(self):
        if os.path.exists(self.file):
            self.runs = pd.read_csv(self.file)
        else:
            self.runs = pd.DataFrame(columns=["run_no", "time"])
            self.save()

    @property
    def run_no(self):
        return 0 if self.runs.empty else self.runs.run_no.max()

    def start_run(self):
        now = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M")
        self.runs.loc[len(self.runs)] = {"run_no": self.run_no+1, "time": now}
        self.save()

    def save(self):
        self.runs.to_csv(self.file, index=False)

    @property
    def cache_dir(self):
        return f"cache/run_{self.run_no}/"

    @property
    def output_dir(self):
        return f"output/run_{self.run_no}/"
