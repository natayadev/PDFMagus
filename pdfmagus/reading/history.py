import json
import os
from datetime import datetime

import fitz


class ReadingHistory:
    def __init__(self, file_path, log_event):
        self.file_path = file_path
        self.log_event = log_event
        self.data = self._load()
        self.current_session = None

    def _load(self):
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            self.log_event(f"Error loading reading history: {e}")
        return {}

    def _save(self):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.log_event(f"Error saving reading history: {e}")

    def get_saved_page(self, file_path):
        entry = self.data.get(file_path)
        return int(entry.get("current_page", 0)) if entry else 0

    def register_session(self, file_path, page_num):
        try:
            if not os.path.exists(file_path):
                return

            doc = fitz.open(file_path)
            total_pages = len(doc)
            doc.close()

            self.data[file_path] = {
                "name": os.path.basename(file_path),
                "current_page": page_num,
                "total_pages": total_pages,
                "last_read": datetime.now().isoformat(),
            }

            self._save()
            self.current_session = file_path
        except Exception as e:
            self.log_event(f"Error registering reading session: {e}")

    def load_last_session(self):
        try:
            if not self.data:
                return

            last_path, last_entry = max(
                self.data.items(),
                key=lambda item: item[1].get("last_read", ""),
                default=(None, None),
            )

            if last_path and os.path.exists(last_path):
                page_num = last_entry.get("current_page", 0)
                self.current_session = last_path
                self.log_event(
                    f"Last session detected: {os.path.basename(last_path)} (page {page_num + 1})"
                )
        except Exception as e:
            self.log_event(f"Error loading last reading session: {e}")

    def clear(self):
        self.data = {}
        self._save()
        self.log_event("Reading history cleared")
