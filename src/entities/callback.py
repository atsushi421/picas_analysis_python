from typing import Optional


class Callback:
    def __init__(
        self,
        id: int,
        period: int,
        execution: int,
        chain_id: int,
        cpu_id: Optional[int] = None,
        executor_id: Optional[int] = None,
    ) -> None:
        self.id: int = id
        self.type: str
        self.T: int = period
        self.C: int = execution
        if period != 0:
            self.D: int = period
            self.type = "timer"
        else:
            self.type = "regular"

        self.executor: int = 0
        self.priority: int = 0
        if cpu_id is not None:
            self.cpu = cpu_id
        if executor_id is not None:
            self.executor = executor_id

        self.chain_id: int = chain_id
        self.chain_T: int
        self.chain_c: int = 0

        self.wcrt: int = 0
        # self.job_index: int = 1
        # self.jobs = []

        # For analysis purpose
        self.segment_flag: bool = False
        self.segment_C: int = 0
        self.chain_on_cpu: bool = False
