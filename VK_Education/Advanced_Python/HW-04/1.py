import os
import json
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class Event:
    datetime: str
    event_type: str
    message: str

    @classmethod
    def from_json_line(cls, line: bytes) -> 'Event':
        data: Dict[str, Any] = json.loads(line.decode('utf-8'))
        message: str = data.get("message", "")
        params: Dict[str, Any] = data.get("params", {})
        
        if params:
            try:
                message = message.format(**params)
            except KeyError as e:
                raise ValueError(f"Отсутствует параметр для интерполяции: {e}")

        return cls(
            datetime=data["datetime"],
            event_type=data["event_type"],
            message=message
        )


class LogProcessor:
    def __init__(self, logs_dir: str) -> None:
        if not os.path.exists(logs_dir):
            raise FileNotFoundError(f"Каталог не найден: {logs_dir}")
        if not os.path.isdir(logs_dir):
            raise NotADirectoryError(f"Путь не является каталогом: {logs_dir}")
            
        self.logs_dir = logs_dir

    def get_last_events_by_service(self, service_name: str, n: int) -> List[Event]:
        if n < 0:
            raise ValueError("Количество событий N не может быть отрицательным.")
        if n == 0:
            return []

        prefix = f"{service_name}_"
        suffix = ".log"
        
        try:
            files = [
                f for f in os.listdir(self.logs_dir)
                if f.startswith(prefix) and f.endswith(suffix)
            ]
        except OSError as e:
            raise RuntimeError(f"Ошибка при чтении каталога {self.logs_dir}: {e}")

        files.sort(reverse=True)
        
        events: List[Event] = []
        
        for filename in files:
            filepath = os.path.join(self.logs_dir, filename)
            
            try:
                with open(filepath, 'rb') as f:
                    content = f.read()
                    if not content:
                        continue
                    
                    lines = content.strip(b'\n').split(b'\n')
                    
                    for line in reversed(lines):
                        if not line.strip():
                            continue
                        
                        event = Event.from_json_line(line)
                        events.append(event)
                        
                        if len(events) == n:
                            events.reverse()
                            return events
                            
            except (OSError, json.JSONDecodeError) as e:
                raise RuntimeError(f"Ошибка при обработке файла {filename}: {e}")
                
        events.reverse()
        return events