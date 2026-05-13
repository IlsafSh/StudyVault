import asyncio

async def simulate_service(name: str, delay: float) -> dict:
    await asyncio.sleep(delay)
    return {"name": name, "status": "ok", "latency": delay}

async def check_services(configs: list[dict], timeout_per_service: float) -> list[dict]:

    async def fetch(config: dict) -> dict:
        name = config.get("name", "unknown")
        delay = config.get("delay", 0.0)
        
        try:
            async with asyncio.timeout(timeout_per_service):
                return await simulate_service(name, delay)
        except TimeoutError:
            return {
                "name": name,
                "status": "timeout",
                "latency": timeout_per_service
            }

    tasks = [fetch(config) for config in configs]
    
    results = await asyncio.gather(*tasks)
    return list(results)


if __name__ == "__main__":
    async def main():
        configs = [
            {"name": "Service A", "delay": 1.0},
            {"name": "Service B", "delay": 3.5}, # Этот сервис должен упасть по таймауту
            {"name": "Service C", "delay": 0.5},
        ]
        
        timeout_limit = 2.0
        print(f"Запуск опроса с таймаутом {timeout_limit}с...")
        
        results = await check_services(configs, timeout_limit)
        
        for res in results:
            print(res)

    # Запускаем event loop
    asyncio.run(main())