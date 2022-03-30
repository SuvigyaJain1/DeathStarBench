import subprocess

# Address for the master node
NGINX_URL = "http://192.168.191.197:8080"
OUTPUT_DIR = "./outputs/"

def run(dist, n_thread, n_conns, dur_sec, script, req_per_sec, filename):
        cmd = f"./wrk -D {dist} -t {n_thread} -c {n_conns} -d {dur_sec}s -L\
        -s{script} {NGINX_URL}/wrk2-api/post/compose -R {req_per_sec} > {OUTPUT_DIR}/{filename}.txt"
        subprocess.run(cmd)


def main():
    for i in [1, 10, 20, 50, 100, 200, 400, 600, 800, 1000, 10000]:
        run("norm", 2, 500, 100,  "./scripts/social-network/compose-post.lua", i, f"rps_{i}")

if __name__ == "__main__":
    main()
