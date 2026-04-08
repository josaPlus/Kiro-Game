import json
from pathlib import Path

SAVE_PATH = Path("data/save.json")


class SaveManager:
    def save_result(self, result: dict) -> None:
        """Append result to data/save.json, creating file/dir as needed."""
        SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
        existing = self.load_results()
        existing.append(result)
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2)

    def load_results(self) -> list[dict]:
        """Return all saved results (empty list if file absent or malformed)."""
        try:
            with open(SAVE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
