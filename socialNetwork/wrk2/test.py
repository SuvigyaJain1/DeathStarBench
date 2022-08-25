import re

def parse_latency(latency: str):
    latencies = re.findall(r"[0-9]*\.[0-9]*\%.*", latency)
    latencies = list(map(lambda x: x.strip().split()[1], latencies))
    print(latencies)

with open ("outputs-directory-2230/COMMAND_1/2") as f:
    output = f.read()
    latency = re.findall(r"Latency Distribution [.\n\s\S]*100.000\%.*s", output)[0]
    parse_latency(latency)

