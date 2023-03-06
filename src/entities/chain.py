from typing import List
from .callback import Callback


class Chain:
    def __init__(self, id: int, sem_prio: int) -> None:
        self.type: str = "p"
        self.num_callbacks: int = 0
        self.id: int = id
        self.t_callback: List[Callback] = []
        self.r_callbacks: List[Callback] = []
        self.C: int = 0
        self.T: int = 0
        self.num_instance: int = 0  # this is only for a non-periodic chain
        self.trigger_next: bool = False
        self.next_r_callback_id: int = 0
        self.sem_priority: int = sem_prio

    def add_callback(self, callback: Callback) -> None:
        if callback.type == "timer":
            self.t_callback.append(callback)
            self.T = callback.T
        else:
            self.r_callbacks.append(callback)

        self.num_callbacks = len(self.t_callback) + len(self.r_callbacks)
        self.C += callback.C

        for c in self.t_callback:  # FIXME
            c.chain_c = self.C

        for c in self.r_callbacks:  # FIXME
            c.chain_c = self.C
