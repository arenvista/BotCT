import json
from src.botc.enums import RoleName
import os
os.makedirs("maps",exist_ok=True)
for n in range(24):
    output={
            "bakerthebread": n,
    "chudbotc0":10,
    "chudbotc1":10,
    "chudbotc2":10,
    "chudbotc3":10
    }
    with open(f"maps/{RoleName(n).display_name}.json","w") as file:
        json.dump(output,file)