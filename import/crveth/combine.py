import csv
from pathlib import Path

from settings import BASE_DIR

exclude = [
    "0x1cEBdB0856dd985fAe9b8fEa2262469360B8a3a6",  # gauge
    "0x989AEb4d175e16225E39E87d0D97A3360524AD80",  # convex
    "0xF147b8125d2ef93FB6965Db97D6746952a133934",  # yearn
    "0x52f541764E6e90eeBc5c21Ff570De0e2D63766B6",  # stakedao
    "0x3Cf54F3A1969be9916DAD548f3C084331C4450b5",  # concentrator
]

balances = []

sum_ = 0

for file in [
    "pool_snapshot.csv",
    "gauge_snapshot.csv",
    "convex_snapshot.csv",
    "yearn_snapshot.csv",
    "stakedao_snapshot.csv",
    "concentrator_snapshot.csv",
]:
    with open(Path(BASE_DIR, "data", "crveth", file), "r") as file:
        reader = csv.reader(file)
        is_first = True
        for row in reader:
            if is_first:
                is_first = False
                continue
            if row[0] not in exclude:
                balances.append(row)
                sum_ += int(row[1])

print(f"Sum of lp of users: {sum_}, total from pool = 550348187166762515331352")

balances = sorted(balances, key=lambda x: int(x[1]), reverse=True)
balances = [
    [
        "User",
        "LP Balance",
        "is_contract",
        "contract_type",
        "events",
        "withdrawn_eth",
        "withdrawn_crv",
        "eth_to_redeem",
        "crv_to_redeem",
    ]
] + balances

with open(Path(BASE_DIR, "data", "crveth_overall.csv"), "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows(balances)
