import functools
import time
from collections import deque

class NotAliveError(Exception):
    pass

def circuit_breaker(state_count: int, error_count: int, network_errors: list, sleep_time_sec: int):
    if state_count <= 10:
        raise ValueError("state_count должен быть больше 10")
    if error_count >= 10:
        raise ValueError("error_count должен быть меньше 10")

    network_errors_tuple = tuple(network_errors)

    def decorator(func):
        history = deque(maxlen=state_count)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            recent_history = list(history)[-error_count:]
            
            # Шаг 3: Проверка на размыкание цепи
            if len(recent_history) == error_count and not any(recent_history):
                raise NotAliveError("Service is temporarily unavailable")
            
            # Шаг 4: Охлаждение (задержка), если последний вызов был с ошибкой
            if history and not history[-1]:
                time.sleep(sleep_time_sec)

            # Шаг 2: Вызов функции и запись результата
            try:
                result = func(*args, **kwargs)
                history.append(True)
                return result
            except network_errors_tuple:
                history.append(False)
                raise
                
        return wrapper
        
    return decorator