import functools

def circuit_breaker(state_count: int, error_count: int, network_errors: list, sleep_time_sec: int):
    if state_count <= 10:
        raise ValueError("state_count должен быть больше 10")
    if error_count >= 10:
        raise ValueError("error_count должен быть меньше 10")

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    
    return decorator