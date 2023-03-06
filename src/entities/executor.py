from typing import List
from .callback import Callback


class Executor:
    def __init__(self, id: int, prio: int) -> None:
        self.id: int = id
        self.priority: int = prio
        self.type: str = ""
        self.callbacks: List[Callback] = []
        self.cpu: int = 0
        # self.ready_queue = []  # TODO
        self.util: float = 0

    def add_callbacks(self, tasks: List[Callback]) -> None:
        for t in tasks:
            self.util += t.C / t.T
            t.executor = self.id
            self.callbacks.append(t)

    def assign(self, callback: Callback) -> None:
        self.callbacks.append(callback)
        callback.executor = self.id
        callback.priority = self.priority
        if self.type:
            print("The executor type is already defined.")
        else:
            if callback.chain_id == 0:
                self.type = "single"
            else:
                self.type = "chain"

    # def sort_ready_callbacks(self, prev_core_t_id: int, prev_core_idx: int):
    #     ready_cb = []
    #     if self.ready_queue:
    #         # check if prev_core callback exist, it has the highest
    #         # priority because it's nonpreemptable within executor
    #         for i in range(len(self.ready_queue)):
    #             if (
    #                 self.ready_queue[i].task_id == prev_core_t_id
    #                 and self.ready_queue[i].index == prev_core_idx
    #             ):
    #                 ready_cb = self.ready_queue[i]
    #                 return ready_cb

    #         t_cb = []
    #         r_cb = []
    #         for i in range(len(self.ready_queue)):
    #             if self.ready_queue[i].timer_cb:
    #                 t_cb.append(self.ready_queue[i])
    #             else:
    #                 r_cb.append(self.ready_queue[i])

    #         # before priotizing callbacks, check whether there exists a
    #         # resumable job instances or not. Because a resumable job
    #         # has a higher priority than timer callback
    #         if t_cb:
    #             t_cb.sort(key=lambda x: x.index)

    #             for i in range(len(t_cb)):
    #                 if t_cb[i].current_exe != 0:
    #                     ready_cb = t_cb[i]
    #                     return ready_cb

    #         if r_cb:
    #             r_cb.sort(key=lambda x: x.index)

    #             for i in range(len(r_cb)):
    #                 if r_cb[i].current_exe != 0:
    #                     ready_cb = r_cb[i]
    #                     return ready_cb

    #         # Now, check new timer callback, then regular callbacks
    #         # which are ready
    #         if t_cb:
    #             t_cb.sort(key=lambda x: x.index)

    #             ready_cb = t_cb[0]
    #             return ready_cb

    #         if r_cb:
    #             r_cb.sort(key=lambda x: x.index)

    #             ready_cb = r_cb[0]
    #             return ready_cb
