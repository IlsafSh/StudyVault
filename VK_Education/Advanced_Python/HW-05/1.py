import concurrent.futures
import hashlib
import queue
from typing import Any, List, Dict

class Pipeline:
    def __init__(self) -> None:
        self.results: Dict[Any, str] = {}
        self.fetch_to_process: queue.Queue = queue.Queue()
        self.process_to_store: queue.Queue = queue.Queue()

    def fetcher(self, task_id: Any) -> str:
        return f"payload_for_task_{task_id}"

    def processor(self, data: str) -> str:
        hashed = data.encode('utf-8')
        for _ in range(100_000):
            hashed = hashlib.sha256(hashed).digest()
        return hashed.hex()

    def storer(self, task_id: Any, result: str) -> None:
        self.results[task_id] = result

    def worker(self, task_id: Any) -> None:
        fetched_data = self.fetcher(task_id)
        self.fetch_to_process.put(fetched_data)

        data_to_process = self.fetch_to_process.get()
        processed_data = self.processor(data_to_process)
        self.process_to_store.put(processed_data)
        self.fetch_to_process.task_done()

        data_to_store = self.process_to_store.get()
        self.storer(task_id, data_to_store)
        self.process_to_store.task_done()

    def run(self, tasks: List[Any]) -> None:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            list(executor.map(self.worker, tasks))