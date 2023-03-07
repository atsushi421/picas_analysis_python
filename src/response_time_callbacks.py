from typing import List, Tuple
from .entities import Chain, CPU, Callback, Executor
import sys
import math


class ResponseTime:
    def __init__(self, chains: List[Chain], cpus: List[CPU]) -> None:
        self._chains = chains
        self._cpus = cpus

    def response_time_callbacks(self) -> Tuple[List[Chain], List[int]]:
        # reshape callbacks and distinguish segment tasks for each chain/CPU
        callbacks: List[Callback] = []
        executors: List[Executor] = []
        idx = 0

        for cpu in self._cpus:
            chain_segment_priority = [sys.maxsize] * len(self._chains)
            chain_segment_task_idx = [0] * len(self._chains)
            chain_segment_exe_time = [0] * len(self._chains)
            for e in cpu.executors:
                for c in e.callbacks:
                    cur_cb = c
                    cur_chain = cur_cb.chain_id
                    if cur_cb.priority < chain_segment_priority[cur_chain]:
                        chain_segment_priority[cur_chain] = cur_cb.priority
                        chain_segment_task_idx[cur_chain] = idx
                    chain_segment_exe_time[cur_chain] += cur_cb.C
                    callbacks.append(cur_cb)
                    idx += 1
                executors.append(e)

            # set segment callbacks
            for s in range(len(self._chains)):
                # remove callbacks of self._chains, it'll fiil at the end of analysis
                self._chains[s].timer_cb = None
                self._chains[s].regular_cbs = []
                if chain_segment_exe_time[s] != 0:
                    callbacks[chain_segment_task_idx[s]].segment_flag = True
                    callbacks[
                        chain_segment_task_idx[s]
                    ].segment_C = chain_segment_exe_time[s]

        executors.sort(key=lambda x: x.id)
        callbacks.sort(key=lambda x: x.id)

        # compute the WCRT of individual callbacks
        for i in range(len(callbacks)):
            flag = True

            # cb id
            t_id = callbacks[i].id

            # check segment task
            segment_flag = callbacks[i].segment_flag

            # executor of target callback
            t_exe = callbacks[i].executor_id

            # priority of target callback
            t_prio = callbacks[i].priority

            # chain of target callback
            t_chain = callbacks[i].chain_id

            # chain on cpu
            t_chain_cpu = callbacks[i].chain_on_cpu

            # cpu
            t_cpu = callbacks[i].cpu_id

            # blocking time by lower priority tasks within executor
            B = 0
            for c in executors[t_exe].callbacks:
                cb = c
                if cb.chain_id != t_chain and cb.priority < t_prio:
                    if cb.C > B:
                        B = cb.C

            # initial R
            if segment_flag:
                R = callbacks[i].segment_C + B
            else:
                R = callbacks[i].C + B

            R_prev = R
            while flag:
                W = 0
                for cb in callbacks:
                    # for j in range(len(callbacks)):
                    # only consider callback on higher- or same priority executor
                    if (
                        cb.id != t_id
                        and executors[t_exe].priority
                        <= executors[cb.executor_id].priority
                    ):
                        # check current chain is on a single cpu
                        if (
                            t_chain_cpu
                            and cb.chain_id != t_chain
                            and cb.cpu_id == t_cpu
                        ) or (not t_chain_cpu and cb.cpu_id == t_cpu):
                            timer_prio, timer_P, timer_cpu = self.find_timer_callback(
                                executors, cb.chain_id
                            )
                            if cb.chain_on_cpu:
                                P = max(cb.chain_C, timer_P)
                            else:
                                P = timer_P

                            if (
                                executors[t_exe].priority
                                < executors[cb.executor_id].priority
                            ) or (t_prio < cb.priority):
                                if timer_prio >= t_prio or timer_cpu != t_cpu:
                                    W += math.ceil(R / P) * cb.C
                                else:
                                    W += cb.C

                if segment_flag:
                    R = W + callbacks[i].segment_C + B
                else:
                    R = W + callbacks[i].C + B

                if R <= R_prev:
                    callbacks[i].wcrt = R
                    break

                R_prev = R

        # reshape callbacks to self._chains where they belong to
        for c in callbacks:
            # for c in range(len(callbacks)):
            if c.type == "timer":
                self._chains[c.chain_id].timer_cb = c
            else:
                self._chains[c.chain_id].regular_cbs.append(c)

        # Theorem 1
        # capture WCRT with considering time delay by prior chain instance
        chain_latency: List[int] = [0] * len(self._chains)
        for i in range(len(self._chains)):
            chain = self._chains[i]
            if chain.timer_cb and chain.timer_cb.segment_flag:
                chain_latency[i] += chain.timer_cb.wcrt
            for rcb in chain.regular_cbs:
                if rcb.segment_flag:
                    chain_latency[i] += rcb.wcrt

            if chain.timer_cb and chain_latency[i] > chain.timer_cb.T:
                chain_latency[i] += chain.timer_cb.T

        return self._chains, chain_latency

    @staticmethod
    def find_timer_callback(
        executors: List[Executor], chain_id: int
    ) -> Tuple[int, int, int]:
        for e in range(len(executors)):
            for c in range(len(executors[e].callbacks)):
                cb = executors[e].callbacks[c]
                if cb.chain_id == chain_id and cb.type == "timer":
                    timer_prio = cb.priority
                    timer_P = cb.T
                    timer_cpu = cb.cpu_id

                    return timer_prio, timer_P, timer_cpu

        raise NotImplementedError("Bug")
