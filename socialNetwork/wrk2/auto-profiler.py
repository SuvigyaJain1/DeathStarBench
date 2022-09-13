# from msilib.schema import File
import subprocess
import os
import time
import csv
import re

# Address for the master node
NGINX_URL = "http://localhost:31111"
OUTPUT_DIR = "./test-run-11th-sept-1"

TO_STRING = ["Distribution", "Threads", "Connections(s)", "Duration", "Script", "Endpoint", "Requests Per Second"]
PARAMS_LIST = PARAMS_LIST = [
    ["fixed", 8, 16, 60,  "scripts/social-network/compose-post.lua", "wrk2-api/post/compose", 10],
    ["fixed", 8, 16, 60,  "scripts/social-network/compose-post.lua", "wrk2-api/post/compose", 100],
    ["fixed", 8, 16, 60,  "scripts/social-network/compose-post.lua", "wrk2-api/post/compose", 200],
    ["fixed", 8, 16, 60,  "scripts/social-network/compose-post.lua", "wrk2-api/post/compose", 500],
    ["fixed", 8, 16, 60,  "scripts/social-network/compose-post.lua", "wrk2-api/post/compose", 750],
    ["fixed", 8, 16, 60,  "scripts/social-network/compose-post.lua", "wrk2-api/post/compose", 1000],
    ["fixed", 1, 1, 60,  "scripts/social-network/compose-post.lua", "wrk2-api/post/compose", 1000],
    ["fixed", 2, 2, 60,  "scripts/social-network/compose-post.lua", "wrk2-api/post/compose", 1000],
    ["fixed", 4, 4, 60,  "scripts/social-network/compose-post.lua", "wrk2-api/post/compose", 1000],
    ["fixed", 8, 8, 60,  "scripts/social-network/compose-post.lua", "wrk2-api/post/compose", 1000],
    ["fixed", 8, 16, 60,  "scripts/social-network/compose-post.lua", "wrk2-api/post/compose", 1000],
    ["fixed", 8, 32, 60,  "scripts/social-network/compose-post.lua", "wrk2-api/post/compose", 1000],
    ["fixed", 8, 64, 60,  "scripts/social-network/compose-post.lua", "wrk2-api/post/compose", 1000],
    ["fixed", 8, 16, 60,  "scripts/social-network/read-user-timeline.lua", "wrk2-api/user-timeline/read", 10],
    ["fixed", 8, 16, 60,  "scripts/social-network/read-user-timeline.lua", "wrk2-api/user-timeline/read", 100],
    ["fixed", 8, 16, 60,  "scripts/social-network/read-user-timeline.lua", "wrk2-api/user-timeline/read", 200],
    ["fixed", 8, 16, 60,  "scripts/social-network/read-user-timeline.lua", "wrk2-api/user-timeline/read", 500],
    ["fixed", 8, 16, 60,  "scripts/social-network/read-user-timeline.lua", "wrk2-api/user-timeline/read", 750],
    ["fixed", 8, 16, 60,  "scripts/social-network/read-user-timeline.lua", "wrk2-api/user-timeline/read", 1000],
    ["fixed", 1, 1, 60,  "scripts/social-network/read-user-timeline.lua", "wrk2-api/user-timeline/read", 1000],
    ["fixed", 2, 2, 60,  "scripts/social-network/read-user-timeline.lua", "wrk2-api/user-timeline/read", 1000],
    ["fixed", 4, 4, 60,  "scripts/social-network/read-user-timeline.lua", "wrk2-api/user-timeline/read", 1000],
    ["fixed", 8, 8, 60,  "scripts/social-network/read-user-timeline.lua", "wrk2-api/user-timeline/read", 1000],
    ["fixed", 8, 16, 60,  "scripts/social-network/read-user-timeline.lua", "wrk2-api/user-timeline/read", 1000],
    ["fixed", 8, 32, 60,  "scripts/social-network/read-user-timeline.lua", "wrk2-api/user-timeline/read", 1000],
    ["fixed", 8, 64, 60,  "scripts/social-network/read-user-timeline.lua", "wrk2-api/user-timeline/read", 1000],
]
OBSERVABLES = [2,4,6]
HEADERS = ['Run ID', 'Command Number'] + [TO_STRING[i] for i in OBSERVABLES] + ['Mean', 'StdDeviation', 'Max', 'Total count', 'Buckets', 'SubBuckets', 'P50', 'P75', 'P90', 'P99', 'P99.9', 'P99.99', 'P99.999']
NUM_RUNS = 3

FOLDER_ID = 0
FILE_ID = 0

rows = []

def parse(run_id, data, line):
    line = line[2:-2]
    stats = line.split(',')

    for stat in stats:
        key, value = stat.split('=')
        key, value = key.strip(), value.strip()
        data[key] = float(value)

def parse_latency(f):
    output = f.read()
    print(re.findall(r"Latency Distribution [.\n\s\S]*100.000\%.*[s/m]", output))
    latency = re.findall(r"Latency Distribution [.\n\s\S]*100.000\%.*[s/m]", output)[0]
    latencies = re.findall(r"[0-9]*\.[0-9]*\%.*", latency)
    latencies = list(map(lambda x: x.strip().split()[1], latencies))
    return latencies

def parse_file(run_id, data, file): 
    with open (file) as f:
        latencies = parse_latency(f)
        headers = ['P50', 'P75', 'P90', 'P99', 'P99.9', 'P99.99', 'P99.999']
        for i in range(len(headers)):
            data[headers[i]] = latencies[i]
        f.seek(0)
        for line in f:
            if line[0] == '#':
                parse(run_id, data, line)

def run(dist, n_thread, n_conns, dur_sec, script, endpoint, req_per_sec, path):
        cmd = f' ./wrk -D {dist} -t {n_thread} -c {n_conns} -d {dur_sec}s -L -s {script} {NGINX_URL}/{endpoint} -R {req_per_sec} > {path}'
        print(cmd)
        os.system(cmd)
        print("exited")
        time.sleep(10)
        # os.system(f"cp ./wrk-output.txt {path}")
        # print(cmd)

def get_runid():
    global FILE_ID
    FILE_ID += 1
    return str(FILE_ID)

def get_path(folder, filename):
    return f"{OUTPUT_DIR}/{folder}/{filename}"

def get_folder():
    global FOLDER_ID
    FOLDER_ID += 1
    folder = f"COMMAND_{FOLDER_ID}"
    os.system(f"mkdir -p {OUTPUT_DIR}/{folder}")
    return folder

def populate_observables(run_id, data, params):
    for factor in OBSERVABLES:
        data[TO_STRING[factor]] = params[factor]

def main():
    # PARAMS_LIST.se()
    # print("params list reversed")
    for params in PARAMS_LIST:
        dist, n_thread, n_conns, dur_sec, script, endpoint, rps = params
        folder = get_folder()
        for i in range(NUM_RUNS):
            data = {}
            run_id = get_runid()
            data['Run ID'] = run_id
            data['Command Number'] = FOLDER_ID
            populate_observables(run_id, data, params)
            path = get_path(folder, run_id)
            run(dist, n_thread, n_conns, dur_sec, script, endpoint, rps, path)
            parse_file(run_id, data, path)
            rows.append(data)

if __name__ == "__main__":
    main()
    # print(headers)
    # print(rows)
    with open(f'./{OUTPUT_DIR}/output.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = HEADERS)
        writer.writeheader()
        writer.writerows(rows)
