import csv
from pathlib import Path

from contract.erc20 import ERC20Contract
from settings import BASE_DIR

lp = "0xC4C319E2D4d66CcA4464C0c2B32c9Bd23ebe784e"
lp_contract = ERC20Contract(lp)

exclude = [
    "0x12dCD9E8D1577b5E4F066d8e7D404404Ef045342",  # gauge
    "0x989AEb4d175e16225E39E87d0D97A3360524AD80",  # convex
    "0x718AbE90777F5B778B52D553a5aBaa148DD0dc5D",  # yearn
    "0x5D98cE7d43c47F23f15F2F55c690ACC075658Cb1",  # yearn
    "0x3Cf54F3A1969be9916DAD548f3C084331C4450b5",  # concentrator
    "0x35a9384473b7581Fbf5c0edBaa7831C1Ab65bdB5",  # beefy
    "0xAB8e74017a8Cc7c15FFcCd726603790d26d7DeCa",  # alch old
]

contract_types = {
    "0xC53127AF77cBa7D07DC08e271bD0826c55f97467": "multisig",
    "0x3bCF3Db69897125Aa61496Fc8a8B55A5e3f245d5": "multisig",
    "0x27bE856E8B8d24220E53B933e29D46A477858cE7": "multisig",
    "0x01C9B838BE2c60181cef4Be3160d6F44daEe0a99": "convex strategy proxy",
    "0xD5bA79D098679730CbF45d4CFcf52aAD5aC8bC8E": "numisme convex strategy",
    "0xc0BCA9516a8cdF027D20dE68821E781B381C2CbA": "yAxis convex strategy",
    "0x93A62dA5a14C80f265DAbC077fCEE437B1a0Efde": "yearn treasury vault",
    "0x41267Fe98489fb8437dd2Eddf4484FbA140ffDfc": "Yieldster vault",
    "0xaBb8B277F49de499b902A1E09A2aCA727595b544": "multisig",
    "0xc5C5D181a08e4F127ADA2d3BE2636e206D7aAf24": "unknown convex strategy",
    "0x3222D0Ab7626f4F9Bc9f1070CE1dE322B481bDA5": "Enso wallet proxy",
    "0xb634316E06cC0B358437CbadD4dC94F1D3a92B3b": "Trade Handler",
}

balances = {}

sum_ = 0

with open(Path(BASE_DIR, "data", "aleth", "pool_overall.csv"), "r") as file:
    reader = csv.reader(file)
    _ = next(reader)

    data_row = next(reader)
    eth_per_lp = float(data_row[3])
    aleth_per_lp = float(data_row[4])

    print(f"Per lp: {eth_per_lp}, {aleth_per_lp}")


for file in [
    "pool_snapshot.csv",
    "gauge_snapshot.csv",
    "convex_snapshot.csv",
    "yearn_snapshot.csv",
    "concentrator_snapshot.csv",
    "beefy_snapshot.csv",
    "alch_old_snapshot.csv",
]:
    with open(Path(BASE_DIR, "data", "aleth", file), "r") as file:
        reader = csv.reader(file)
        is_first = True
        for row in reader:
            if is_first:
                is_first = False
                continue
            if row[0] not in exclude:
                user = row[0]
                if user not in balances:
                    lp_minus_withdrawn = (
                        int(row[1])
                        - int(int(row[5]) / eth_per_lp / 2)
                        - int(int(row[6]) / aleth_per_lp / 2)
                    )
                    if lp_minus_withdrawn < 0:
                        lp_minus_withdrawn = 0

                    balances[user] = (
                        [row[0], int(row[1])] + [str(lp_minus_withdrawn)] + row[2:]
                    )
                else:
                    lp_minus_withdrawn = (
                        int(balances[user][1])
                        + int(row[1])
                        - int(int(row[5]) / eth_per_lp / 2)
                        - int(int(row[6]) / aleth_per_lp / 2)
                    )
                    if lp_minus_withdrawn < 0:
                        lp_minus_withdrawn = 0

                    balances[user][1] = int(balances[user][1]) + int(row[1])
                    balances[user][2] = str(lp_minus_withdrawn)
                    balances[user][8] = (
                        int(balances[user][8]) + int(row[7]) + int(row[5])
                    )  # withdrawn already applied
                    balances[user][9] = (
                        int(balances[user][9]) + int(row[8]) + int(int(row[6]))
                    )
                sum_ += int(row[1])

print(
    f"Sum of lp of users: {sum_}, total from pool = {lp_contract.total_supply(block_identifier=17806742)}"
)

balances = sorted(balances.values(), key=lambda x: int(x[1]), reverse=True)

for balance in balances:
    if balance[0] in contract_types:
        balance[4] = contract_types[balance[0]]

print(f"Sum check: {sum([x[1] for x in balances])}")
balances = [
    [
        "User",
        "LP Balance",
        "LP Balance - withdrawn",
        "is_contract",
        "contract_type",
        "events",
        "withdrawn_eth",
        "withdrawn_aleth",
        "eth_to_redeem",
        "aleth_to_redeem",
    ]
] + balances

with open(Path(BASE_DIR, "data", "aleth_overall.csv"), "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows(balances)
