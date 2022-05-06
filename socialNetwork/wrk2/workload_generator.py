import subprocess
import os
import time

# Address for the master node
NGINX_URL = "http://128.199.25.250:31111"
OUTPUT_DIR = "./client-external-with-istio-readtimeline"

def run(dist, n_thread, n_conns, dur_sec, script, req_per_sec, filename):
        cmd = f"./wrk -D {dist} -t {n_thread} -c {n_conns} -d {dur_sec}s -L -s {script} {NGINX_URL}/wrk2-api/home-timeline/read -R {req_per_sec} > {OUTPUT_DIR}/{filename}.txt"
        os.system(cmd)
        time.sleep(int(dur_sec)+10)

def main():
    for i in [20,50,100,200,500,1000]:
        run("fixed", 2, 100, 60,  "./scripts/social-network/read-home-timeline.lua", i, f"rps_{i}")

if __name__ == "__main__":
    main()
