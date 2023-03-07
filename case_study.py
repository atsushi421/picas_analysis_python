# Case study (Section VII-B)

# Period(only for timer callback), Execution time, Deadline(only for timer callback), Chain, Order in chain
# Case study III (overloeaded scenario)

from typing import List
import numpy as np
import pandas as pd

from src import Callback, Executor, Chain, CPU, response_time_callbacks

data = pd.DataFrame(
    data=[
        [80, 2.3, 80, 1, 1],
        [0, 16.1, 0, 1, 2],
        [80, 2.3, 80, 2, 1],
        [0, 2.2, 0, 2, 2],
        [0, 18.4, 0, 2, 3],
        [0, 9.1, 0, 2, 4],
        [100, 23.1, 100, 3, 1],
        [0, 7.9, 0, 3, 2],
        [0, 14.2, 0, 3, 3],
        [0, 17.9, 0, 3, 4],
        [100, 20.6, 100, 4, 1],
        [0, 17.9, 0, 4, 2],
        [0, 6.6, 0, 4, 3],
        [160, 1.7, 160, 5, 1],
        [0, 11, 0, 5, 2],
        [0, 6.6, 0, 5, 3],
        [0, 7.9, 0, 5, 4],
        [1000, 1.7, 1000, 6, 1],
        [0, 195.9, 0, 6, 2],
        [120, 33.2, 120, 7, 1],
        [0, 2.2, 0, 7, 2],
        [120, 33.2, 120, 8, 1],
        [0, 6.6, 0, 8, 2],
        [120, 33.2, 120, 9, 1],
        [0, 6.6, 0, 9, 2],
        [120, 33.2, 120, 10, 1],
        [0, 1.7, 0, 10, 2],
        [120, 33.2, 120, 11, 1],
        [0, 2.2, 0, 11, 2],
        [120, 33.2, 120, 12, 1],
        [0, 2.2, 0, 12, 2],
    ],
    columns=["period", "execution_time", "deadline", "chain", "order_in_chain"],
)

num_executors = 18
num_cpus = 4
num_chains = int(data["chain"].max())
num_tasks = len(data)

# Initialize callbacks & chains
chains: List[Chain] = []
callbacks: List[Callback] = []
chain_idx = 0
sem_prio = num_chains
for c_id in range(len(data)):
    cb = Callback(
        c_id,
        data.loc[c_id, "period"],
        data.loc[c_id, "execution_time"],
        data.loc[c_id, "chain"] - 1,
        data.loc[c_id, "order_in_chain"] - 1,
    )
    callbacks.append(cb)
    if len(chains) < cb.chain_id + 1:
        chain_idx += 1
        chain = Chain(chain_idx, sem_prio)
        chains.append(chain)
        sem_prio -= 1
    chains[cb.chain_id].add_callback(cb)

# Initialize executors
prio = num_executors
executors: List[Executor] = []
for e in range(num_executors):
    executors.append(Executor(e, prio))
    prio -= 1

# Initialize cpus
cpus: List[CPU] = [CPU(cpu_id) for cpu_id in range(num_cpus)]

# Assign callback priority
callback_prio = num_tasks
callbacks_sorted = []
for ch in chains:
    for r_cb in reversed(ch.r_callbacks):
        r_cb.priority = callback_prio
        callback_prio -= 1
        r_cb.chain_T = ch.T
        callbacks_sorted.append(r_cb)

    t_callback = ch.t_callback
    if not t_callback:
        raise NotImplementedError("BUG")
    t_callback.priority = callback_prio
    callback_prio -= 1
    t_callback.chain_T = ch.T
    callbacks_sorted.append(t_callback)

callbacks = sorted(callbacks_sorted, key=lambda x: x.id)
callbacks[0].priority = callbacks[
    2
].priority  # Since callback(1) and callback(3) are the same, i.e., a mutual callback

# If all callbacks of a chain exist on the same CPU core, set "chain_on_cpu" True
indices = [1, 2, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]  # +1 value
for i in indices:
    callbacks[i - 1].chain_on_cpu = True

# Allocate callbacks to executors manually
# RT chains
executors[0].add_callbacks(callbacks[0:2])
executors[0].add_callbacks([callbacks[2]])
executors[1].add_callbacks(callbacks[3:5])
executors[2].add_callbacks(callbacks[6:9])
executors[3].add_callbacks(callbacks[10:12])
executors[4].add_callbacks(callbacks[13:16])
executors[5].add_callbacks(callbacks[17:18])

# BE chains
executors[6].add_callbacks([callbacks[19]])
executors[7].add_callbacks([callbacks[20]])
executors[8].add_callbacks([callbacks[21]])
executors[9].add_callbacks([callbacks[22]])
executors[10].add_callbacks([callbacks[23]])
executors[11].add_callbacks([callbacks[24]])
executors[12].add_callbacks([callbacks[25]])
executors[13].add_callbacks([callbacks[26]])
executors[14].add_callbacks([callbacks[27]])
executors[15].add_callbacks([callbacks[28]])
executors[16].add_callbacks([callbacks[29]])
executors[17].add_callbacks([callbacks[30]])

# Allocate executors to CPUs
cpus[0].assign_executor(executors[0])
cpus[0].assign_executor(executors[4])
cpus[0].assign_executor(executors[10])
cpus[0].assign_executor(executors[13])
cpus[0].assign_executor(executors[14])

cpus[1].assign_executor(executors[1])
cpus[1].assign_executor(executors[7])
cpus[1].assign_executor(executors[8])
cpus[1].assign_executor(executors[15])
cpus[1].assign_executor(executors[16])

cpus[2].assign_executor(executors[2])
cpus[2].assign_executor(executors[6])
cpus[2].assign_executor(executors[11])
cpus[2].assign_executor(executors[17])

cpus[3].assign_executor(executors[3])
cpus[3].assign_executor(executors[5])
cpus[3].assign_executor(executors[12])
cpus[3].assign_executor(executors[9])

# Compute response time of callbacks
_chains, latency = response_time_callbacks(chains, cpus)

# Output
for _c, l in zip(_chains, latency):
    print(f"[chain {_c.id}] latency: {l}")
