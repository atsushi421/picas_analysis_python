# Case study (Section VII-B)

# Period(only for timer callback), Execution time, Deadline(only for timer callback), Chain, Order in chain
# Case study III (overloeaded scenario)

from typing import List
import pandas as pd

from src import Callback, Executor, Chain, CPU, ResponseTime


CB_PROPERTIES = pd.DataFrame(
    data=[
        ### -- RT chain --
        # chain 0
        [80, 2.3, 0],
        [0, 16.1, 0],
        # chain 1
        [80, 2.3, 1],
        [0, 2.2, 1],
        [0, 18.4, 1],
        [0, 9.1, 1],
        # chain 2
        [100, 23.1, 2],
        [0, 7.9, 2],
        [0, 14.2, 2],
        [0, 17.9, 2],
        # chain 3
        [100, 20.6, 3],
        [0, 17.9, 3],
        [0, 6.6, 3],
        # chain 4
        [160, 1.7, 4],
        [0, 11, 4],
        [0, 6.6, 4],
        [0, 7.9, 4],
        # chain 5
        [1000, 1.7, 5],
        [0, 195.9, 5],
        ### -- BE chain --
        # chain 6
        [120, 33.2, 6],
        [0, 2.2, 6],
        # chain 7
        [120, 33.2, 7],
        [0, 6.6, 7],
        # chain 8
        [120, 33.2, 8],
        [0, 6.6, 8],
        # chain 9
        [120, 33.2, 9],
        [0, 1.7, 9],
        # chain 10
        [120, 33.2, 10],
        [0, 2.2, 10],
        # chain 11
        [120, 33.2, 11],
        [0, 2.2, 11],
    ],
    columns=["period", "execution_time", "chain_id"],
)

NUM_EXECUTOERS = 18
NUM_CPUS = 4

# Initialize chains
num_chains = int(CB_PROPERTIES["chain_id"].max()) + 1
sem_priority = num_chains
chains: List[Chain] = []
for chain_id in range(num_chains):
    chains.append(Chain(chain_id, sem_priority))
    sem_priority -= 1

# Initialize callbacks
callbacks: List[Callback] = []
for c_id in range(len(CB_PROPERTIES)):
    cb = Callback(
        c_id,
        CB_PROPERTIES.loc[c_id, "period"],
        CB_PROPERTIES.loc[c_id, "execution_time"],
        CB_PROPERTIES.loc[c_id, "chain_id"],
    )
    callbacks.append(cb)
    chains[cb.chain_id].add_callback(cb)

# Initialize executors
priority = NUM_EXECUTOERS
executors: List[Executor] = []
for exe_id in range(NUM_EXECUTOERS):
    executors.append(Executor(exe_id, priority))
    priority -= 1

# Initialize cpus
cpus: List[CPU] = [CPU(cpu_id) for cpu_id in range(NUM_CPUS)]

# Assign callback priority
callback_priority = len(CB_PROPERTIES)
for chain in chains:
    for r_cb in reversed(chain.regular_cbs):
        r_cb.priority = callback_priority
        callback_priority -= 1
        r_cb.chain_T = chain.T

    if not chain.timer_cb:
        raise NotImplementedError("BUG")
    chain.timer_cb.priority = callback_priority
    callback_priority -= 1
    chain.timer_cb.chain_T = chain.T

callbacks[0].priority = callbacks[
    2
].priority  # Since callback(1) and callback(3) are the same, i.e., a mutual callback

# If all callbacks of a chain exist on the same CPU core, set "chain_on_cpu" True
same_cpu_chain_cb_id = [0, 1, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
for i in same_cpu_chain_cb_id:
    callbacks[i].chain_on_cpu = True

# Allocate callbacks to executors manually
# RT chains
executors[0].add_callbacks(callbacks[0:3])
executors[1].add_callbacks(callbacks[3:6])
executors[2].add_callbacks(callbacks[6:10])
executors[3].add_callbacks(callbacks[10:13])
executors[4].add_callbacks(callbacks[13:17])
executors[5].add_callbacks(callbacks[17:19])

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
response_time = ResponseTime(chains, cpus)
latency = response_time.response_time_callbacks()

# Output
for chain, l in zip(chains, latency):
    cbs = [f"t{chain.timer_cb.id}"] if chain.timer_cb else []
    for rcb in chain.regular_cbs:
        cbs.append(f"t{rcb.id}")
    print(f"|Chain {chain.id} = {cbs}| End-to-end latency: {l}")
