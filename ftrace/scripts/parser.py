'''
pid : [Node1, Node2, Node3....]

Node 1: 1 top level function_trace
'''
import re
import os
import json
class Line:

    def __init__(self, line):
        line = line.strip()
        self.is_log_line = self.log_line(line)
        if not self.is_log_line:
            return
        
        self.process, self.time, self.function_name = [value.strip() for value in line.split("|")]
        *procname, self.pid = self.process.split("-")

        self.time = self.time.strip()
        if self.time:
            try:
                self.time = float(re.findall(r'\d+\.?\d*', self.time)[0])
            except:
                print(self.time)
            # self.time, unit = self.time.split(" ")
        
        self.opening_bracket = "{" in self.function_name
        self.closing_bracket = "}" in self.function_name

        # if self.opening_bracket:
        self.function_name = self.function_name.strip("{")
        if self.closing_bracket:
            self.function_name = "BLANK"
    
    def log_line(self, line):
        return (line) and (not line[0] == '#') and ("|" in line) and ("<idle>" not in line) and ("====" not in line)


class Node:
    def __init__(self, line):
        if line.time:
            self.time = line.time
        else:
            self.time = 0
        self.function_name = line.function_name
        self.children = []
        if line.opening_bracket:
            self.open_brackets = 1
        else:
            self.open_brackets = 0
    
    def add_child_to_node(self, line):
        if line.closing_bracket:
            self.open_brackets -= 1
            self.time = line.time
        else: 
            if line.closing_bracket:
                self.open_brackets += 1
            self.children.append(Node(line))
    
    def to_dict(self):
        # return {"pid": self.pid, "time": self.time, }
        d = {}
        d["function_name"] = self.function_name
        d["time"] = self.time
        d["children"] = [i.to_dict() for i in self.children]
        return d



def main():
    trace_folder = 'WITHOUT_ISTIO_WITHOUT_WORKLOAD'
    num_runs=5
    os.makedirs('parsedOutputs/'+trace_folder)

    for i in range(num_runs):
        trace_file = open(trace_folder+'/'+str(i)+'.txt', 'r')
        result = {}

        def add_node_to_result(line):
            
            node = Node(line)
            pid = line.pid
            if pid not in result.keys():
                result[pid] = [node]
            else:
                if not result[pid][-1].open_brackets == 0:
                    result[pid][-1].add_child_to_node(line)
                else:
                    result[pid].append(node)

        for line in trace_file:
            line = Line(line)
            if not line.is_log_line:
                continue
            add_node_to_result(line)


        for key in result:
            new_result = []
            for node in result[key]:
                if node.open_brackets:
                    continue
                new_result.append(node.to_dict())
            result[key] = new_result

        with open('parsedOutputs/'+trace_folder+'/'+str(i)+'.json', 'w') as fptr:
            json.dump(result, indent = 2, fp=fptr)

        trace_file.close()

main()