import os
import subprocess
import time

FTRACE_HOME = '/sys/kernel/debug/tracing'

def output(command):
    print(command)
    op = subprocess.getoutput(command)
    print(op)
    return op

def exec(command):
    return os.system(f"{command}")

def get_commands(commands_file):
    with open(commands_file, 'r') as f:
        commands = f.read().split('\n')
    return commands

def get_pids(process_name):
    command = f"pgrep -f {process_name}"
    return output(command)

def write_to_file(filename, data):
    command = f'''echo "{data}" > {filename}'''
    return output(command)

def append_to_file(filename, data):
    command = f'''echo "{data}" >> {filename}'''
    return output(command)

def add_ftrace_pid_filter(process_name):
    pids = get_pids(process_name)
    file_path = f"{FTRACE_HOME}/set_ftrace_pid"
    append_to_file(file_path, pids)

def clear_ftrace_pid_filter():
    file_path = f"{FTRACE_HOME}/set_ftrace_pid"
    write_to_file(file_path, "")

def turn_tracing_on():
    file_path = f"{FTRACE_HOME}/tracing_on"
    write_to_file(file_path, "1")

def turn_tracing_off():
    file_path = f"{FTRACE_HOME}/tracing_on"
    write_to_file(file_path, "0")

def set_current_tracer(tracer):
    file_path = f"{FTRACE_HOME}/current_tracer"
    write_to_file(file_path, tracer)

def clear_trace_log():
    file_path = f"{FTRACE_HOME}/trace"
    write_to_file(file_path, "")

def set_graph_depth(depth):
    file_path = f"{FTRACE_HOME}/max_graph_depth"
    write_to_file(file_path, depth)

def backup_trace(destination_path):
    trace_path = f"{FTRACE_HOME}/trace"
    output(f"cp {trace_path} {destination_path}")

def async_workload_trigger(wrk_command):
    exec(f"{wrk_command} &")

def set_options(options):
    file_path = f"{FTRACE_HOME}/trace_options"
    append_to_file(file_path, options)

def setup_ftrace(processes):
    turn_tracing_off()
    set_current_tracer("function_graph")
    set_graph_depth("2")
    clear_trace_log()
    clear_ftrace_pid_filter()
    set_options("userstacktrace")
    set_options("sym-userobj")
    set_options("funcgraph-duration")
    set_options("display-graph")
    set_options("funcgraph-proc")
    for process in processes:
        add_ftrace_pid_filter(process)

def main(CONFIG):
    '''
    {
        name: w_istio_w_workload
        processes: [envoy, istiod, ...]
        with_workload: True
        workload_command: ./wrk .....
        num_traces: 5
        trace_time: 60
    }
    '''
    name = CONFIG["name"]
    num_traces = CONFIG["num_traces"]
    processes = CONFIG["processes"]
    trace_time = CONFIG["trace_time"]
    with_workload = CONFIG["with_workload"]
    workload_command = CONFIG["workload_command"]

    output(f"mkdir {name}")
    setup_ftrace(processes)

    for trace_number in range(num_traces):
        
        clear_trace_log()
        if with_workload:
            async_workload_trigger()
        
        turn_tracing_on()
        time.sleep(trace_time)
        turn_tracing_off()

        output_file = f"{name}/{trace_number}"
        backup_trace(output_file)

if __name__ == '__main__':
    CONFIG = {}
    CONFIG["name"] = "DEMO_RUN_WITH_K8S"
    CONFIG["num_traces"] = 3
    CONFIG["processes"] = ['memcached','redis','Service','mongo', 'nginx']
    CONFIG["trace_time"] = 10
    CONFIG["with_workload"] = False
    CONFIG["workload_command"] = None
    main(CONFIG)
