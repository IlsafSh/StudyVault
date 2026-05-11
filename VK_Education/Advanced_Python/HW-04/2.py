import os
import json
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

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

    def _read_file_backwards(self, filename: str) -> List[dict]:
        filepath = os.path.join(self.logs_dir, filename)
        try:
            with open(filepath, 'rb') as f:
                content = f.read().strip(b'\n')
                if not content:
                    return []
                lines = content.split(b'\n')
                return [json.loads(line) for line in reversed(lines) if line.strip()]
        except (OSError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Ошибка файла {filename}: {e}")

    def get_last_events_by_service(self, service_name: str, n: int) -> List[Event]:
        if n < 0:
            raise ValueError("N не может быть отрицательным.")
        if n == 0:
            return []

        prefix = f"{service_name}_"
        try:
            files = sorted(
                [f for f in os.listdir(self.logs_dir) if f.startswith(prefix) and f.endswith(".log")],
                reverse=True
            )
        except OSError as e:
            raise RuntimeError(f"Ошибка чтения директории: {e}")

        events: List[Event] = []
        for filename in files:
            for data in self._read_file_backwards(filename):
                events.append(Event.from_dict(data))
                if len(events) == n:
                    return events[::-1]
                    
        return events[::-1]

    def _get_all(self, n: int, param_filter: Optional[Any] = None) -> List[Event]:
        if n < 0:
            raise ValueError("N не может быть отрицательным.")
        if n == 0:
            return []

        try:
            files = [f for f in os.listdir(self.logs_dir) if f.endswith(".log")]
        except OSError as e:
            raise RuntimeError(f"Ошибка чтения директории: {e}")

        files_by_date: Dict[str, List[str]] = {}
        for f in files:
            date_str = f.rsplit('_', 1)[-1].split('.')[0]
            files_by_date.setdefault(date_str, []).append(f)

        sorted_dates = sorted(files_by_date.keys(), reverse=True)
        results: List[Event] = []

        for date_str in sorted_dates:
            hour_data: List[dict] = []
            
            for filename in files_by_date[date_str]:
                hour_data.extend(self._read_file_backwards(filename))
                
            hour_data.sort(key=lambda x: x["datetime"], reverse=True)
            
            for data in hour_data:
                if param_filter is not None and param_filter not in data.get("params", {}).values():
                    continue
                    
                results.append(Event.from_dict(data))
                if len(results) == n:
                    return results[::-1]

        return results[::-1]

    def get_last_events_all_services(self, n: int) -> List[Event]:
        return self._get_all(n)

    def get_last_events_with_param(self, param_value: Any, n: int) -> List[Event]:
        return self._get_all(n, param_filter=param_value)