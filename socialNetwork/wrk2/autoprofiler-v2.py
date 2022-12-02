#!/bin/env python3
import os
import sys
import json
import subprocess
import re
import csv

CONFIG = 'config.json'
OUTPUT_FOLDER = 'FinalWrkReadingsWithoutIstio'
NUM_ITER = 1
SCRIPTS_HOME = '/root/upstream/DeathStarBench/socialNetwork/wrk2/scripts/social-network/'

def get_output(command):
    print(command)
    return subprocess.getoutput(command)
    
def run_workload(workload):
    distribution = workload["distribution"]
    threads = workload["threads"]
    connections = workload["connections"]
    duration = workload["duration"]
    script = f'{SCRIPTS_HOME}/{workload["script"]}'
    url = workload["url"]
    rps = workload["rps"]
    wrk_command = f"wrk -D {distribution} -t {threads} -c {connections} -d {duration}s -L -s {script} {url} -R {rps}"
    wrk_output = get_output(wrk_command)
    return wrk_output

def get_workload_config(workload, iteration):
    distribution = workload["distribution"]
    threads = workload["threads"]
    connections = workload["connections"]
    duration = workload["duration"]
    workload_name = workload["script"].replace('.lua', '')
    rps = workload["rps"]
    return {"workload_iteration":iteration, "distribution":distribution,"threads":threads,"connections":connections,"duration":duration,"workload_name":workload_name, "rps":rps}

def convert(latency):
    latency = latency.strip()
    if "ms" in latency:
        return float(latency.replace('ms', ''))
    if "s" in latency:
        return float(latency.replace('s', '')) * 1000
    print("FOUND OUT OF RANGE LAT")
    return latency

def parse_latency(output):
    latency = re.findall(r"Latency Distribution [.\n\s\S]*100.000\%.*[s/m]", output)[0]
    latencies = re.findall(r"[0-9]*\.[0-9]*\%.*", latency)
    percentiles = list(map(lambda x: x.strip().split()[0], latencies))
    latencies = list(map(lambda x: x.strip().split()[1], latencies))
    
    key_value_lats = {}
    for i in range(len(percentiles)):
        percentile = percentiles[i]
        latency = latencies[i]
        key_value_lats[percentile] = convert(latency)
    return key_value_lats

def parse(line):
    data = {}
    line = line[2:-2]
    stats = line.split(',')
    for stat in stats:
        key, value = stat.split('=')
        key, value = key.strip(), value.strip()
        data[key] = float(value)
    return data

def parse_summary_stats(output):
    output_lines = output.split("\n")
    summary_stats = {}
    for line in output_lines:
        line = line.strip()
        if line and line[0] == '#':
            print(line)
            stats = parse(line)
            summary_stats.update(stats)
    return summary_stats

def get_timeouts(output):
    output_lines = output.split("\n")
    non2xx = 0
    timeouts = 0
    actual_rps = 0
    total_requests = 0
    socket_errors = {}
    for line in output_lines:
        line = line.strip()
        if "Non-2xx or 3xx responses" in line:
            non2xx = line.split(":")[1]
            non2xx = float(non2xx.strip())
        if "Requests/sec" in line:
            actual_rps = line.split(":")[1]
            actual_rps = float(actual_rps.strip())
        if "Socket errors" in line:
            line = line.replace("Socket errors: ", '').strip()
            key_val_pairs = line.split(",")
            for key_val_pair in key_val_pairs:
                key_val_pair = key_val_pair.strip()
                key, value = key_val_pair.split(" ")
                key = f'{key}_errors'
                socket_errors[key] = int(value)
        if "requests in" in line:
            total_requests = line.strip().split(' ')[0].strip()
            total_requests = int(total_requests)
        if len(socket_errors) == 0:
            socket_errors = {"connect_errors": 0, "read_errors":0, "write_errors":0, "timeout_errors":0} 
    
    
    socket_errors.update({"total_requests":total_requests, "non2xx_errors":non2xx, "actual_rps":actual_rps})
    return socket_errors

def save_wrk_output(workload_id, iteration, wrk_output):
    get_output(f"mkdir -p {OUTPUT_FOLDER}/{workload_id}")
    workload_file = f"{OUTPUT_FOLDER}/{workload_id}/{iteration}.wrk"
    get_output(f"touch {workload_file}")
    output_file = open(workload_file, 'w')
    output_file.write(wrk_output)

def derive_stats(workload, wrk_output, iteration):
    all_stats = {}
    all_stats.update(get_workload_config(workload, iteration))
    all_stats.update(parse_summary_stats(wrk_output))
    all_stats.update(parse_latency(wrk_output))
    all_stats.update(get_timeouts(wrk_output))
    return all_stats

def filter_stats(all_stats):
    del all_stats['Buckets']
    del all_stats['SubBuckets']

if __name__ == '__main__':
    config_file = open(CONFIG, 'r')
    workloads = json.load(config_file)
    workload_id = 1
    summary_stats = []
    for workload in workloads:
        for iteration in range(NUM_ITER): 
            wrk_output = run_workload(workload)
            save_wrk_output(workload_id, iteration, wrk_output)
            stats = derive_stats(workload, wrk_output, iteration)
            filter_stats(stats)
            summary_stats.append(stats)
        workload_id += 1
    
    output_path = f'{OUTPUT_FOLDER}/summary_stats.csv'
    result = {}
    
    print(summary_stats)
    
    keys = summary_stats[0].keys()

    with open(output_path, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(summary_stats) 

