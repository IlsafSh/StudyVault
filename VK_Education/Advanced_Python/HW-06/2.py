import asyncio

BASE_DELAY = 0.5

async def simulate_service(name: str, delay: float) -> dict:
    if "ConnectionError" in name:
        raise ConnectionError(f"Ошибка соединения при обращении к {name}")
        
    await asyncio.sleep(delay)
    return {"name": name, "status": "ok", "latency": delay}


async def check_services(configs: list[dict], timeout_per_service: float, max_retries: int = 3) -> list[dict]:
    
    async def fetch(config: dict) -> dict:
        name = config.get("name", "unknown")
        delay = config.get("delay", 0.0)
        
        total_allowed_attempts = max_retries + 1 
        
        for attempt in range(total_allowed_attempts):
            try:
                async with asyncio.timeout(timeout_per_service):
                    result = await simulate_service(name, delay)
                    result["attempts"] = attempt + 1
                    return result
                    
            except (TimeoutError, ConnectionError) as e:
                if attempt < max_retries:
                    attempt_index = attempt + 1
                    sleep_time = BASE_DELAY * (2 ** attempt_index)
                    await asyncio.sleep(sleep_time)
                else:
                    return {
                        "name": name,
                        "status": "error",
                        "latency": timeout_per_service if isinstance(e, TimeoutError) else 0.0,
                        "attempts": total_allowed_attempts
                    }

    tasks = [fetch(config) for config in configs]
    results = await asyncio.gather(*tasks)
    return list(results)


if __name__ == "__main__":
    async def main():
        configs = [
            {"name": "Service A", "delay": 0.5},
            # Упадет по таймауту на всех попытках
            {"name": "Service B (Timeout)", "delay": 5.0}, 
            # Будет сразу выбрасывать ConnectionError
            {"name": "Service C (ConnectionError)", "delay": 0.1},
        ]
        
        timeout_limit = 1.0
        print(f"Запуск опроса (timeout={timeout_limit}с, max_retries=3)...\n")
        
        results = await check_services(configs, timeout_limit)
        
        for res in results:
            print(res)

    asyncio.run(main())