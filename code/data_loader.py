from pathlib import Path
import pandas as pd


class DataLoader:
    def __init__(self, dataset_path):
        self.dataset_path = Path(dataset_path)

    def load_all(self):
        data = {}

        csv_files = [
    "messages.csv",
    "sample_messages.csv",      # <-- ADD THIS
    "users.csv",
    "groups.csv",
    "business_accounts.csv",
    "images.csv",
    "voice_notes.csv",
    "message_history.csv",
    "message_events.csv",
    "group_members.csv",
    "user_business_history.csv",
    "daily_notification_summary.csv"
]

        for file in csv_files:
            path = self.dataset_path / file
            if path.exists():
                data[file.replace(".csv", "")] = pd.read_csv(path)

        return data