import csv
from pathlib import Path

from settings import BASE_DIR

exclude = [
    "0x1cEBdB0856dd985fAe9b8fEa2262469360B8a3a6",  # gauge
    "0x989AEb4d175e16225E39E87d0D97A3360524AD80",  # convex
    "0xF147b8125d2ef93FB6965Db97D6746952a133934",  # yearn
    "0x52f541764E6e90eeBc5c21Ff570De0e2D63766B6",  # stakedao
    "0x3Cf54F3A1969be9916DAD548f3C084331C4450b5",  # concentrator
    "0x4e626f8Cf7529EE986a6825A7F8fB929DB740d96",  # beefy
    "0x5D77b731803916cbcdec2BBdb3Ad0649C6a6EA17",  # Bent
    "0x3DD9636CA2b554cCCd219d73796e80d819c90CBa",  # yearn strategy router - Vault
    "0xd7b17297B9884Aa73BF5E6e39e3cEC107ffe6b17",  # FARM
    "0x506Eb3dc29389cEA11768cCe6a01Fca4996Fa30c",  # FARM Convex Strategy
]

contract_types = {
    "0x4bfb33d65f4167EBE190145939479227E7bf2CB0": "multisig",
    "0x942d484C008d86C92d62fce9Cbdf010f89d4F899": "multisig",
    "0x2d0aba145D6A0c071CfF3bD87CC4b8475413D895": "multisig",
    "0xc7599b60f05639f93D26e58d56D90C526A6e7575": "multisig",
    "0x506Eb3dc29389cEA11768cCe6a01Fca4996Fa30c": "convex strategy proxy",
    "0x0e119685190CA54B5BBf5E3504F447C5E40d2410": "multisig",
    "0x70CCBE10F980d80b7eBaab7D2E3A73e87D67B775": "multisig",
    "0x114777cA6c3967ddEe23523B775e1d1f385D7Deb": "multisig",
    "0xeCb456EA5365865EbAb8a2661B0c503410e9B347": "curve pool owner",
    "0xd7b17297B9884Aa73BF5E6e39e3cEC107ffe6b17": "FARM Vault",
    "0xc8fF37F7d057dF1BB9Ad681b53Fa4726f268E0e8": "Alladin DAO",
    "0x40735598F6c70Fad69068cAe50317cc133A63991": "multisig",
    "0x9008D19f58AAbD9eD0D60971565AA8510560ab41": "CoW",
    "0x1c5Dbb5d9864738e84c126782460C18828859648": "Pickle",
    "0x8F14Fd9d3F51412036ef0460b4F5CD46d4AE7455": "Convex Strategy",
    "0x2C01B4AD51a67E2d8F02208F54dF9aC4c0B778B6": "multisig",
    "0x60F727BdeAD2ce49B00f2A2133Fc707b931D130B": "Enso wallet proxy",
    "0x2153CD859b60817b909E443e7a6a34fA80a4c7bb": "Subsafe proxy",
    "0x9323441091F39BE7F1F9331013eA245b04168e78": "unverified",
    "0x819aE01901f2365f1807Fa230711dAb70fac50c5": "Subsafe proxy",
    "0xc429910261C3820a9Bf0553825081045C610C36E": "Subsafe proxy",
    "0x57ebA9a2124EF3563Fab785014Cd61eeeAFa035e": "multisig",
    "0xb634316E06cC0B358437CbadD4dC94F1D3a92B3b": "yearn Trade Handler",
    "0xcADBA199F3AC26F67f660C89d43eB1820b7f7a3b": "yearn Trade Handler",
    "0x73152648E3C7FefebCdE692AF55d972702916623": "multisig",
    "0x0962a706770388f62670E8b5a7891863d0D92E85": "multisig",
    "0x70ed999E2849A3C85EB4a6288B90c7ecA7b807F4": "Portals.fi",
}

balances = {}

sum_ = 0

with open(Path(BASE_DIR, "data", "crveth", "pool_overall.csv"), "r") as file:
    reader = csv.reader(file)
    _ = next(reader)

    data_row = next(reader)
    eth_per_lp = float(data_row[3])
    crv_per_lp = float(data_row[4])

    print(f"Per lp: {eth_per_lp}, {crv_per_lp}")


for file in [
    "pool_snapshot.csv",
    "gauge_snapshot.csv",
    "convex_snapshot.csv",
    "yearn_snapshot.csv",
    "stakedao_snapshot.csv",
    "concentrator_snapshot.csv",
    "beefy_snapshot.csv",
    "bent_snapshot.csv",
    "yvault_snapshot.csv",
    "farm_snapshot.csv",
]:
    with open(Path(BASE_DIR, "data", "crveth", file), "r") as file:
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
                        - int(int(row[6]) / crv_per_lp / 2)
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
                        - int(int(row[6]) / crv_per_lp / 2)
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

print(f"Sum of lp of users: {sum_}, total from pool = 550348187166762515331352")

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
        "withdrawn_crv",
        "eth_to_redeem",
        "crv_to_redeem",
    ]
] + balances

with open(Path(BASE_DIR, "data", "crveth_overall.csv"), "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows(balances)
