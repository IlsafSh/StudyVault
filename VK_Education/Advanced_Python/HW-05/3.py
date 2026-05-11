import sys
import sysconfig
import logging
import multiprocessing
import concurrent.futures
import hashlib
import queue
import threading
from typing import Any, List, Dict

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

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

class SafePipeline(Pipeline):
    def __init__(self) -> None:
        super().__init__()
        self._lock = threading.Lock()

    def storer(self, task_id: Any, result: str) -> None:
        with self._lock:
            super().storer(task_id, result)

class AdaptivePipeline(SafePipeline):
    def __init__(self) -> None:
        super().__init__()
        
        is_nogil_build = bool(sysconfig.get_config_var("Py_GIL_DISABLED"))
        gil_is_active = getattr(sys, '_is_gil_enabled', lambda: True)()
        
        self.is_nogil = is_nogil_build and not gil_is_active

        if not self.is_nogil:
            self.manager = multiprocessing.Manager()
            self.results = self.manager.dict()
            self._lock = self.manager.Lock()
            self.fetch_to_process = self.manager.Queue()
            self.process_to_store = self.manager.Queue()

    def get_executor(self) -> concurrent.futures.Executor:
        if self.is_nogil:
            logger.info("Стратегия: GIL отключен (Free-Threading). Используется ThreadPoolExecutor.")
            return concurrent.futures.ThreadPoolExecutor()
        else:
            logger.info("Стратегия: GIL включен. Используется ProcessPoolExecutor.")
            return concurrent.futures.ProcessPoolExecutor()

    def run(self, tasks: List[Any]) -> None:
        with self.get_executor() as executor:
            list(executor.map(self.worker, tasks))