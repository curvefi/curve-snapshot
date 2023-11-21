import csv
import json
from pathlib import Path

from web3 import Web3

from contract.erc20 import ERC20Contract, YERC20Contract
from contract.pool_contract import AlEthPoolContract
from settings import BASE_DIR, settings, web3_provider

lp = "0xC4C319E2D4d66CcA4464C0c2B32c9Bd23ebe784e"
lp_contract = ERC20Contract(lp)
convex_addr = "0x48Bc302d8295FeA1f8c3e7F57D4dDC9981FEE410"
convex_contract = ERC20Contract(convex_addr)
pool = "0xC4C319E2D4d66CcA4464C0c2B32c9Bd23ebe784e"
pool_contract = AlEthPoolContract(pool)
yearn_addr = "0x718AbE90777F5B778B52D553a5aBaa148DD0dc5D"
yearn_contract = YERC20Contract(yearn_addr)
start_block = 13227441
block = 17806742
web3 = Web3(web3_provider)

yearn = "0x718AbE90777F5B778B52D553a5aBaa148DD0dc5D"
yearn2 = "0x5D98cE7d43c47F23f15F2F55c690ACC075658Cb1"

current_block = json.loads(Web3.to_json(web3.eth.get_block("latest")))["number"]


lp_total_supply = lp_contract.total_supply(block_identifier=block)
lp_supply = lp_contract.balanceOf(yearn, block_identifier=block)
lp_supply += convex_contract.balanceOf(yearn2, block_identifier=block)
balances = pool_contract.balances(block_identifier=block)
balances = (
    balances[0] * lp_supply / lp_total_supply,
    balances[1] * lp_supply / lp_total_supply,
)
price_per_share = yearn_contract.pricePerShare(block_identifier=block) / 10**18

eth_per_lp, crv_per_lp = (
    price_per_share * balances[0] / lp_supply,
    price_per_share * balances[1] / lp_supply,
)

users = []
with open(Path(BASE_DIR, "data", "aleth", "all_users_extended.csv"), "r") as file:
    reader = csv.reader(file)
    for row in reader:
        users.append(row[0])

user_balances = []
sum_ = 0

for user in users:
    balance = int(
        yearn_contract.balanceOf(user, block_identifier=block) * price_per_share
    )
    if balance > 0:
        code = web3.eth.get_code(user, block_identifier=block)
        events = pool_contract.get_liquidity_change_logs(
            block, current_block, user=user
        )
        withdrawn_eth = 0
        withdrawn_crv = 0
        if events:
            for event in events:
                if event["event"] == "RemoveLiquidity":
                    withdrawn_eth += event["args"]["token_amounts"][0]
                    withdrawn_crv += event["args"]["token_amounts"][1]
                elif event["event"] == "RemoveLiquidityOne":
                    withdrawn_crv += event["args"]["coin_amount"]

        user_balances.append(
            {
                "user": user,
                "balance": balance,
                "is_contract": bool(code),
                "events": events,
                "withdrawn_eth": withdrawn_eth,
                "withdrawn_crv": withdrawn_crv,
            }
        )
        print(user, balance, bool(code), withdrawn_eth, withdrawn_crv)

    sum_ += balance

user_balances = sorted(user_balances, key=lambda x: x["balance"], reverse=True)


data = [
    [
        "User",
        "LP Balance",
        "is_contract",
        "contract_type",
        "events",
        "withdrawn_eth",
        "withdrawn_aleth",
        "eth_to_redeem",
        "aleth_to_redeem",
    ]
]
for user in user_balances:
    data.append(
        [
            user["user"],
            user["balance"],
            user["is_contract"],
            settings.contract_names.get(user["user"]),
            user["events"],
            user["withdrawn_eth"],
            user["withdrawn_crv"],
            int(user["balance"] * eth_per_lp - user["withdrawn_eth"]),
            int(user["balance"] * crv_per_lp - user["withdrawn_crv"]),
        ]
    )

print(
    sum_,
    current_block,
)
with open(
    Path(BASE_DIR, "data", "aleth", "yearn_snapshot.csv"), "w", newline=""
) as file:
    writer = csv.writer(file)
    writer.writerows(data)

with open(
    Path(BASE_DIR, "data", "aleth", "yearn_overall.csv"), "w", newline=""
) as file:
    writer = csv.writer(file)
    writer.writerows(
        [
            [
                "Total LP",
                "Balances ETH",
                "Balances alETH",
                "ETH per LP",
                "alETH per LP",
                "Total User Balances",
            ],
            [
                lp_supply,
                balances[0],
                balances[1],
                eth_per_lp,
                crv_per_lp,
                sum_,
            ],
        ]
    )
