import csv
from pathlib import Path

from settings import BASE_DIR

exclude = [
    "0xc1c5B8aAfE653592627B54B9527C7E98326e83Ff",  # gauge
    "0x59f58431d4cBA2B7e9E8D78F064a8fa24C5134bF",  # staking
    "0xd6479545171d5D9c360129D820cC060f9A063bc8",  # beefy
]

balances = []

sum_ = 0

with open(Path(BASE_DIR, "data", "ftml", "pool_overall.csv"), "r") as file:
    reader = csv.reader(file)
    _ = next(reader)

    data_row = next(reader)
    ftm_per_lp = float(data_row[3])
    ftml_per_lp = float(data_row[4])

    print(f"Per lp: {ftm_per_lp}, {ftml_per_lp}")


for file in [
    "pool_snapshot.csv",
    "gauge_snapshot.csv",
    "staking_snapshot.csv",
    "beefy_snapshot.csv",
]:
    with open(Path(BASE_DIR, "data", "ftml", file), "r") as file:
        reader = csv.reader(file)
        is_first = True
        for row in reader:
            if is_first:
                is_first = False
                continue
            if row[0] not in exclude:
                lp_minus_withdrawn = (
                    int(row[1])
                    - int(int(row[5]) / ftm_per_lp / 2)
                    - int(int(row[6]) / ftml_per_lp / 2)
                )
                if lp_minus_withdrawn < 0:
                    lp_minus_withdrawn = 0

                balances.append(row[:2] + [str(lp_minus_withdrawn)] + row[2:])
                sum_ += int(row[1])

print(f"Sum of lp of users: {sum_}, total from pool = 15748296461660460985558")

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
        "ftm_to_redeem",
        "ftml_to_redeem",
    ]
] + balances

with open(Path(BASE_DIR, "data", "ftml_overall.csv"), "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows(balances)
