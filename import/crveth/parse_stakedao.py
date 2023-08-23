import csv
import json
from pathlib import Path

from web3 import Web3

from contract.erc20 import ERC20Contract
from contract.pool_contract import PoolContract
from settings import BASE_DIR, settings, web3_provider

lp = "0xEd4064f376cB8d68F770FB1Ff088a3d0F3FF5c4d"
lp_contract = ERC20Contract(lp)
gauge = "0x1cEBdB0856dd985fAe9b8fEa2262469360B8a3a6"
gauge_contract = ERC20Contract(gauge)
stakedao_addr = "0xc0F082C886b94f36F67C6659bE01C0069968Cd0E"
stakedao_contract = ERC20Contract(stakedao_addr)
pool = "0x8301AE4fc9c624d1D396cbDAa1ed877821D7C511"
pool_contract = PoolContract(pool)
start_block = 13676983
block = 17807829
web3 = Web3(web3_provider)

convex = "0x989AEb4d175e16225E39E87d0D97A3360524AD80"
ycrv = "0xF147b8125d2ef93FB6965Db97D6746952a133934"
stakedao = "0x52f541764E6e90eeBc5c21Ff570De0e2D63766B6"


current_block = json.loads(Web3.to_json(web3.eth.get_block("latest")))["number"]


lp_total_supply = lp_contract.total_supply(block_identifier=block)
lp_stakedao_supply = gauge_contract.balanceOf(stakedao, block_identifier=block)
balances = pool_contract.balances(block_identifier=block)
balances = (
    balances[0] * lp_stakedao_supply / lp_total_supply,
    balances[1] * lp_stakedao_supply / lp_total_supply,
)

eth_per_lp, crv_per_lp = (
    balances[0] / lp_stakedao_supply,
    balances[1] / lp_stakedao_supply,
)

users = []
with open(Path(BASE_DIR, "data", "crveth", "all_users.csv"), "r") as file:
    reader = csv.reader(file)
    for row in reader:
        users.append(row[0])

user_balances_convex = []
sum_stakedao = 0

for user in users:
    balance = stakedao_contract.balanceOf(user, block_identifier=block)
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

    sum_stakedao += balance

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
        "withdrawn_crv",
        "eth_to_redeem",
        "crv_to_redeem",
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
    sum_stakedao,
    current_block,
)
with open(
    Path(BASE_DIR, "data", "crveth", "stakedao_snapshot.csv"), "w", newline=""
) as file:
    writer = csv.writer(file)
    writer.writerows(data)

with open(
    Path(BASE_DIR, "data", "crveth", "stakedao_overall.csv"), "w", newline=""
) as file:
    writer = csv.writer(file)
    writer.writerows(
        [
            [
                "Total LP",
                "Balances ETH",
                "Balances CRV",
                "ETH per LP",
                "CRV per LP",
                "Total User Balances",
            ],
            [
                lp_stakedao_supply,
                balances[0],
                balances[1],
                eth_per_lp,
                crv_per_lp,
                sum_stakedao,
            ],
        ]
    )
