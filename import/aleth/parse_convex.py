import csv
import json
from pathlib import Path

from web3 import Web3

from contract.erc20 import ERC20Contract
from contract.pool_contract import PoolContract
from settings import BASE_DIR, settings, web3_provider

lp = "0xC4C319E2D4d66CcA4464C0c2B32c9Bd23ebe784e"
lp_contract = ERC20Contract(lp)
gauge = "0x12dCD9E8D1577b5E4F066d8e7D404404Ef045342"
gauge_contract = ERC20Contract(gauge)
pool = "0xC4C319E2D4d66CcA4464C0c2B32c9Bd23ebe784e"
pool_contract = PoolContract(pool)
convex_addr = "0x48Bc302d8295FeA1f8c3e7F57D4dDC9981FEE410"
convex_contract = ERC20Contract(convex_addr)
start_block = 13227441
block = 17806740
web3 = Web3(web3_provider)

convex = "0x989AEb4d175e16225E39E87d0D97A3360524AD80"

current_block = json.loads(Web3.to_json(web3.eth.get_block("latest")))["number"]


lp_total_supply = lp_contract.total_supply(block_identifier=block)
lp_convex_supply = gauge_contract.balanceOf(convex, block_identifier=block)
balances = pool_contract.balances(block_identifier=block)
balances = (
    balances[0] * lp_convex_supply / lp_total_supply,
    balances[1] * lp_convex_supply / lp_total_supply,
)

eth_per_lp, crv_per_lp = balances[0] / lp_convex_supply, balances[1] / lp_convex_supply

users = []
with open(Path(BASE_DIR, "data", "aleth", "all_users.csv"), "r") as file:
    reader = csv.reader(file)
    for row in reader:
        users.append(row[0])

user_balances_convex = []
sum_convex = 0

for user in users:
    balance = convex_contract.balanceOf(user, block_identifier=block)
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
                    if event["args"]["coin_index"] == 0:
                        withdrawn_eth += event["args"]["token_amount"]
                    elif event["args"]["coin_index"] == 1:
                        withdrawn_crv += event["args"]["token_amount"]
                elif event["event"] == "AddLiquidity":
                    withdrawn_eth -= event["args"]["token_amounts"][0]
                    withdrawn_crv -= event["args"]["token_amounts"][1]

        user_balances_convex.append(
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

    sum_convex += balance

user_balances_convex = sorted(
    user_balances_convex, key=lambda x: x["balance"], reverse=True
)


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
for user in user_balances_convex:
    data.append(
        [
            user["user"],
            user["balance"],
            user["is_contract"],
            settings.contract_names.get(user["user"]),
            user["events"],
            user["withdrawn_eth"],
            user["withdrawn_crv"],
            user["balance"] * eth_per_lp - user["withdrawn_eth"],
            user["balance"] * crv_per_lp - user["withdrawn_crv"],
        ]
    )

print(
    sum_convex,
    current_block,
)
with open(
    Path(BASE_DIR, "data", "aleth", "convex_snapshot.csv"), "w", newline=""
) as file:
    writer = csv.writer(file)
    writer.writerows(data)

with open(
    Path(BASE_DIR, "data", "aleth", "convex_overall.csv"), "w", newline=""
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
                lp_convex_supply,
                balances[0],
                balances[1],
                eth_per_lp,
                crv_per_lp,
                sum_convex,
            ],
        ]
    )
