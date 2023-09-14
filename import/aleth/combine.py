import csv
from pathlib import Path

from settings import BASE_DIR

exclude = [
    "0x12dCD9E8D1577b5E4F066d8e7D404404Ef045342",  # gauge
    "0x989AEb4d175e16225E39E87d0D97A3360524AD80",  # convex
    "0x718AbE90777F5B778B52D553a5aBaa148DD0dc5D",  # yearn
    "0x5D98cE7d43c47F23f15F2F55c690ACC075658Cb1",  # yearn
    "0x3Cf54F3A1969be9916DAD548f3C084331C4450b5",  # yearn
]

balances = []

sum_ = 0

for file in [
    "pool_snapshot.csv",
    "gauge_snapshot.csv",
    "convex_snapshot.csv",
    "yearn_snapshot.csv",
    "concentrator_snapshot.csv",
]:
    with open(Path(BASE_DIR, "data", "aleth", file), "r") as file:
        reader = csv.reader(file)
        is_first = True
        for row in reader:
            if is_first:
                is_first = False
                continue
            if row[0] not in exclude:
                balances.append(row)
                sum_ += int(row[1])

print(f"Sum of lp of users: {sum_}, total from pool = 24763590359241671361762")

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

with open(Path(BASE_DIR, "data", "aleth_overall.csv"), "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows(balances)
