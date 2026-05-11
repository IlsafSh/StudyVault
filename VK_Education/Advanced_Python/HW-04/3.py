import os
import json
from functools import lru_cache
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Event:
    datetime: str
    event_type: str
    message: str

    @classmethod
    def from_dict(cls, data: dict) -> 'Event':
        msg = data.get("message", "")
        params = data.get("params", {})
        if params:
            try:
                msg = msg.format(**params)
            except KeyError as e:
                raise ValueError(f"Ошибка интерполяции: {e}")
        return cls(data["datetime"], data["event_type"], msg)

class LogProcessor:
    def __init__(self, logs_dir: str) -> None:
        if not os.path.isdir(logs_dir):
            raise NotADirectoryError(f"Каталог не найден: {logs_dir}")
        self.logs_dir = logs_dir

    @lru_cache(maxsize=128)
    def get_error_counts(self, start_date: str, end_date: str) -> Dict[str, int]:
        if start_date > end_date:
            raise ValueError("Начальная дата не может быть больше конечной.")
            
        error_counts: Dict[str, int] = {}
        try:
            files = [f for f in os.listdir(self.logs_dir) if f.endswith(".log")]
        except OSError as e:
            raise RuntimeError(f"Ошибка чтения директории: {e}")

        for filename in files:
            parts = filename[:-4].rsplit('_', 1)
            if len(parts) != 2:
                continue
                
            service, date_str = parts[0], parts[1]
            
            if service not in error_counts:
                error_counts[service] = 0
                
            if start_date <= date_str <= end_date:
                filepath = os.path.join(self.logs_dir, filename)
                try:
                    with open(filepath, 'rb') as f:
                        for line in f:
                            if not line.strip():
                                continue
                            if json.loads(line).get("event_type") == "ERROR":
                                error_counts[service] += 1
                except (OSError, json.JSONDecodeError) as e:
                    raise RuntimeError(f"Ошибка при обработке файла {filename}: {e}")
                    
        return {k: v for k, v in error_counts.items() if v > 0}

    def get_last_error_dates(self) -> Dict[str, str]:
        try:
            files = [f for f in os.listdir(self.logs_dir) if f.endswith(".log")]
        except OSError as e:
            raise RuntimeError(f"Ошибка чтения директории: {e}")

        service_files: Dict[str, List[str]] = {}
        for f in files:
            parts = f.rsplit('_', 1)
            if len(parts) == 2:
                service_files.setdefault(parts[0], []).append(f)

        last_errors: Dict[str, str] = {}
        
        for service, s_files in service_files.items():
            s_files.sort(reverse=True)
            for filename in s_files:
                found = False
                for data in self._read_file_backwards(filename):
                    if data.get("event_type") == "ERROR":
                        last_errors[service] = data["datetime"]
                        found = True
                        break
                if found:
                    break
                    
        return last_errors