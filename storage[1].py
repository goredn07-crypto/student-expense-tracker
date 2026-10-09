"""
storage.py - Safe JSON persistence handler for Student Expense Tracker.
"""

from __future__ import annotations
import json
import os
from typing import Any, Dict, List


class StorageError(Exception):
    """Custom exception raised for persistence and file access errors."""
    pass


class StorageHandler:
    def __init__(self, filepath: str = "expenses.json") -> None:
        self.filepath = filepath
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Creates the data file and parent directories if they do not exist."""
        try:
            parent_dir = os.path.dirname(self.filepath)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)

            if not os.path.exists(self.filepath) or os.path.getsize(self.filepath) == 0:
                with open(self.filepath, "w", encoding="utf-8") as f:
                    json.dump([], f, indent=4)
        except OSError as e:
            raise StorageError(f"Failed to initialize storage file '{self.filepath}': {e}") from e

    def load_all(self) -> List[Dict[str, Any]]:
        """
        Loads all expense records from the JSON storage file safely.
        Returns an empty list if the file is empty or corrupted.
        """
        if not os.path.exists(self.filepath):
            self._ensure_file_exists()
            return []

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return []
                data = json.loads(content)
                if not isinstance(data, list):
                    raise StorageError(f"Expected list format in '{self.filepath}', got {type(data).__name__}")
                return data
        except json.JSONDecodeError:
            # Handles corrupt or partially-written files without crashing
            return []
        except OSError as e:
            raise StorageError(f"Error reading from storage file '{self.filepath}': {e}") from e

    def save_all(self, records: List[Dict[str, Any]]) -> None:
        """
        Safely writes the list of expense records to storage using atomic replacement.
        """
        if not isinstance(records, list):
            raise ValueError("Records to save must be provided as a list.")

        # Atomic write: write to temp file first to prevent corruption on sudden termination
        temp_filepath = f"{self.filepath}.tmp"
        try:
            with open(temp_filepath, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=4, ensure_ascii=False)
            os.replace(temp_filepath, self.filepath)
        except OSError as e:
            if os.path.exists(temp_filepath):
                try:
                    os.remove(temp_filepath)
                except OSError:
                    pass
            raise StorageError(f"Error writing to storage file '{self.filepath}': {e}") from e


# Convenience singleton instances for direct imports
default_storage = StorageHandler("expenses.json")


def load_expenses() -> List[Dict[str, Any]]:
    return default_storage.load_all()


def save_expenses(expenses: List[Dict[str, Any]]) -> None:
    default_storage.save_all(expenses)
