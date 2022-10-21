import time

with open("/sys/kernel/debug/tracing/trace_marker", "w") as fd:
    count = 0
    while count < 20:
        print(f'my marker here: ${time.perf_counter()} ${time.time()}', file=fd)
        time.sleep(1)
        count+=1