import csv
from pathlib import Path

from settings import BASE_DIR

exclude = [
    "0x941C2Acdb6B85574Ffc44419c2AA237a9e67be03",  # gauge
    "0x989AEb4d175e16225E39E87d0D97A3360524AD80",  # convex
]

balances = []

sum_ = 0

with open(Path(BASE_DIR, "data", "mseth", "pool_overall.csv"), "r") as file:
    reader = csv.reader(file)
    _ = next(reader)

    data_row = next(reader)
    eth_per_lp = float(data_row[3])
    mseth_per_lp = float(data_row[4])

    print(f"Per lp: {eth_per_lp}, {mseth_per_lp}")


for file in [
    "pool_snapshot.csv",
    "gauge_snapshot.csv",
    "convex_snapshot.csv",
]:
    with open(Path(BASE_DIR, "data", "mseth", file), "r") as file:
        reader = csv.reader(file)
        is_first = True
        for row in reader:
            if is_first:
                is_first = False
                continue
            if row[0] not in exclude:
                lp_minus_withdrawn = (
                    int(row[1])
                    - int(int(row[5]) / eth_per_lp / 2)
                    - int(int(row[6]) / mseth_per_lp / 2)
                )
                if lp_minus_withdrawn < 0:
                    lp_minus_withdrawn = 0

                balances.append(row[:2] + [str(lp_minus_withdrawn)] + row[2:])
                sum_ += int(row[1])

print(f"Sum of lp of users: {sum_}, total from pool = 2260726276780465996372")

balances = sorted(balances, key=lambda x: int(x[1]), reverse=True)
balances = [
    [
        "User",
        "LP Balance",
        "LP Balance - withdrawn",
        "is_contract",
        "contract_type",
        "events",
        "withdrawn_eth",
        "withdrawn_mseth",
        "eth_to_redeem",
        "mseth_to_redeem",
    ]
] + balances

with open(Path(BASE_DIR, "data", "mseth_overall.csv"), "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows(balances)
