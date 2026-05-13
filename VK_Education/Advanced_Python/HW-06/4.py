import asyncio
import argparse
import json
import sys

BASE_DELAY = 0.5 

async def simulate_service(name: str, delay: float) -> dict:
    if "ConnectionError" in name:
        raise ConnectionError(f"Ошибка соединения при обращении к {name}")
        
    await asyncio.sleep(delay)
    return {"name": name, "status": "ok", "latency": delay}


async def check_services(
    configs: list[dict], 
    timeout_per_service: float, 
    max_retries: int = 3, 
    concurrency: int = 2
) -> list[dict]:

    semaphore = asyncio.Semaphore(concurrency)
    
    total_tasks = len(configs)
    completed_tasks = 0
    
    async def fetch(config: dict) -> dict:
        nonlocal completed_tasks  # Позволяет изменять переменную из внешней области видимости
        
        name = config.get("name", "unknown")
        delay = config.get("delay", 0.0)
        total_allowed_attempts = max_retries + 1 
        
        result_dict = None
        
        async with semaphore:
            for attempt in range(total_allowed_attempts):
                try:
                    async with asyncio.timeout(timeout_per_service):
                        result = await simulate_service(name, delay)
                        result["attempts"] = attempt + 1
                        result_dict = result
                        break  # Если всё прошло успешно, выходим из цикла retry
                        
                except (TimeoutError, ConnectionError) as e:
                    if attempt < max_retries:
                        attempt_index = attempt + 1
                        sleep_time = BASE_DELAY * (2 ** attempt_index)
                        await asyncio.sleep(sleep_time)
                    else:
                        result_dict = {
                            "name": name,
                            "status": "error",
                            "latency": timeout_per_service if isinstance(e, TimeoutError) else 0.0,
                            "attempts": total_allowed_attempts
                        }
        
        # Обновляем прогресс-бар после того, как сервис (со всеми попытками) отработал
        completed_tasks += 1
        print(f"\rПрогресс: {completed_tasks}/{total_tasks} сервисов завершено...", end="", flush=True)
        
        return result_dict

    tasks = [fetch(config) for config in configs]
    results = await asyncio.gather(*tasks)
    
    # Перенос строки, чтобы не затирать прогресс-бар следующим выводом
    print() 
    return list(results)


def main():
    # 1. Настройка argparse
    parser = argparse.ArgumentParser(description="Асинхронный CLI-агрегатор виртуальных сервисов")
    parser.add_argument("--timeout", type=float, default=1.0, help="Таймаут ожидания одного сервиса (сек)")
    parser.add_argument("--retries", type=int, default=3, help="Количество повторных попыток")
    parser.add_argument("--concurrency", type=int, default=2, help="Ограничение одновременных запросов")
    parser.add_argument("--output", type=str, help="Путь к файлу для сохранения JSON-отчета (например, report.json)")
    
    args = parser.parse_args()

    configs = [
        {"name": "Service A", "delay": 0.5},
        {"name": "Service B", "delay": 0.3},
        {"name": "Service C (Timeout)", "delay": 5.0},
        {"name": "Service D", "delay": 0.1},
        {"name": "Service E (ConnectionError)", "delay": 0.1},
    ]
    
    print(f"Запуск агрегатора (timeout={args.timeout}, retries={args.retries}, concurrency={args.concurrency})")
    
    # Запускаем event loop
    results = asyncio.run(check_services(configs, args.timeout, args.retries, args.concurrency))
    
    # 3. Сохранение в JSON-файл
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        print(f"Отчет успешно сохранен в файл: {args.output}")
    
    # 4. Проверка на ошибки для exit code
    has_errors = any(res["status"] != "ok" for res in results)
    
    if has_errors:
        print("Завершено с ошибками: один или несколько сервисов недоступны.")
        sys.exit(1)
    else:
        print("Успешно: все сервисы доступны.")
        sys.exit(0)


if __name__ == "__main__":
    main()