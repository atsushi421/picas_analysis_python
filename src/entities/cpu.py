from typing import Any, List
from .callback import Callback
from .executor import Executor
from .chain import Chain

import sys


class CPU:
    def __init__(self, id: int) -> None:
        self.id: int = id
        self.utilization: float = 0
        self.hyperperiod: int = 0
        self.num_tasks: int = 0
        self.tasks: List[Callback]
        self.executors: List[Executor] = []
        self.executor_ids: List[int] = []
        # self.ready_queue: List[Any]
        self.on_core: Any  # FIXME
        self.low_sem_prio_chain: int = 0
        self.combined_executor_flag: bool = False

    # For analysis use
    def assign_executor(self, exe: Executor) -> None:
        exe.cpu = self.id
        for c in exe.callbacks:
            c.cpu_id = self.id

        self.executors.append(exe)
        self.executor_ids.append(exe.id)
        self.utilization += exe.util

    # For analysis use
    def find_low_sem_prio_chain_cpu(self, chains: List[Chain]) -> None:
        tmp_sem_prio = sys.maxsize
        if self.executors:
            for e in self.executors:
                tasks = e.callbacks
                for t in tasks:
                    if chains[t.chain_id].sem_priority < tmp_sem_prio:
                        tmp_sem_prio = chains[t.chain_id].sem_priority
                        self.low_sem_prio_chain = t.chain_id
