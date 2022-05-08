import os
import sys
from csv import DictWriter

FOLDER=sys.argv[1]

def apply_grep(filepath, pattern):
    cmd = f"grep -P '{pattern}' -H -o {FOLDER}/{filepath} >> ./means.txt"
    os.system(cmd)


os.system("echo ''| cat > ./means.txt")

for rps in os.listdir(FOLDER):
    rps_dir = os.path.join(os.getcwd(), FOLDER, rps)
    for file in os.listdir(rps_dir):
        wrk_out = os.path.join(rps_dir, file)
        apply_grep(os.path.join(rps,file), "Mean.*,")


data_dict = []
with open("./means.txt", "r") as f:
    data = f.read().strip()
    lines = data.split('\n')
    for line in lines:
        file, mean = line.split(':', maxsplit=1)
        mean = mean.split('=')[1].strip()[:-1]
        idx = file.split('/')[-1]
        rps = file.split('/')[-2]        
        data_dict.append({"rps":rps, "idx":idx, "mean":mean})

print(data_dict)

with open("output.csv", 'w') as f:
    dw = DictWriter(f, ["rps", "idx", "mean"])
    dw.writeheader()

    dw.writerows(data_dict)

"""
[
    {
        "rps":sfew
        "idx":saf
        "mean":sde
    },
        {
        "rps":sfew
        "idx":saf
        "mean":sde
    },
]
"""