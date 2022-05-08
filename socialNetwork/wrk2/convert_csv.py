import os
from csv import DictWriter

FOLDER='outputs'

def apply_grep(filepath, pattern):
    cmd = f"grep -P '{pattern}' -H -o {FOLDER}/{filepath} >> ./means.txt"
    os.system(cmd)


os.system("echo ''| cat > ./means.txt")

for rps in os.listdir(FOLDER):
    rps_dir = os.path.join(os.getcwd(), FOLDER, rps)
    for file in os.listdir(rps_dir):
        wrk_out = os.path.join(rps_dir, file)
        apply_grep(os.path.join(rps,file), "(?<=Mean    =    )[0-9]*.[?0-9]*")


data_dict = []
with open("./means.txt", "r") as f:
    data = f.read().strip()
    lines = data.split('\n')
    for line in lines:
        file, mean = line.split(':', maxsplit=1)
        _, rps, idx = file.split('/', maxsplit=2)

        data_dict.append({"rps":rps, "idx":idx, "mean":mean})


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