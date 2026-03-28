import json
from src.botc.enums import RoleName
import os
import argparse

parser=argparse.ArgumentParser()
parser.add_argument("--name",type=str,default="bakerthebread")
args=parser.parse_args()

os.makedirs("maps",exist_ok=True)
for n in range(24):
    output={
            args.name: n,
    "chudbotc0":10,
    "chudbotc1":4,
    "chudbotc2":7,
    "chudbotc3":10
    }
    try:
        print(RoleName(n).display_name)
        name=RoleName(n).display_name.replace(" ","_")
        with open(f"maps/{name}.json","w") as file:
            json.dump(output,file)
    except:
        pass