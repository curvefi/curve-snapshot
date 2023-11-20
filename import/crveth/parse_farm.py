import csv
import json
from pathlib import Path

from web3 import Web3

from contract.erc20 import ERC20Contract, FarmERC20Contract
from contract.pool_contract import PoolContract
from settings import BASE_DIR, settings, web3_provider

lp = "0xEd4064f376cB8d68F770FB1Ff088a3d0F3FF5c4d"
lp_contract = ERC20Contract(lp)
convex_addr = "0x085A2054c51eA5c91dbF7f90d65e728c0f2A270f"
convex_contract = ERC20Contract(convex_addr)
farm = "0xd7b17297B9884Aa73BF5E6e39e3cEC107ffe6b17"
farm_contract = FarmERC20Contract(farm)
farm_vault = "0x64EE16703874b2c6D2C9226A3Cb25CD0Ac2e1E31"
farm_vault_contract = FarmERC20Contract(farm_vault)
pool = "0x8301AE4fc9c624d1D396cbDAa1ed877821D7C511"
farm_convex_strategy = "0x506Eb3dc29389cEA11768cCe6a01Fca4996Fa30c"
pool_contract = PoolContract(pool)
start_block = 13676983
block = 17807829
web3 = Web3(web3_provider)


current_block = json.loads(Web3.to_json(web3.eth.get_block("latest")))["number"]

lp_total_supply = lp_contract.total_supply(block_identifier=block)
lp_farm_supply = lp_contract.balanceOf(
    farm, block_identifier=block
) + convex_contract.balanceOf(farm_convex_strategy, block_identifier=block)
balances = pool_contract.balances(block_identifier=block)
balances = (
    balances[0] * lp_farm_supply / lp_total_supply,
    balances[1] * lp_farm_supply / lp_total_supply,
)
price_per_share = farm_contract.getPricePerFullShare(block_identifier=block) / 10**18

eth_per_lp, crv_per_lp = balances[0] / lp_farm_supply, balances[1] / lp_farm_supply


users = []
with open(Path(BASE_DIR, "data", "crveth", "all_farm_users.csv"), "r") as file:
    reader = csv.reader(file)
    for row in reader:
        users.append(row[0])


user_balances = []
total_sum = 0
for user in users:

    if user != farm_vault:
        balance = farm_contract.underlyingBalanceWithInvestmentForHolder(
            user, block_identifier=block
        )
        balance_vault = int(farm_vault_contract.balanceOf(user, block_identifier=block) * price_per_share)

    else:
        continue

    balance = balance or balance_vault

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
                        withdrawn_eth += event["args"]["coin_amount"]
                    elif event["args"]["coin_index"] == 1:
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
        print(user, balance, bool(code))

    total_sum += balance

user_balances = sorted(user_balances, key=lambda x: x["balance"], reverse=True)


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
    total_sum,
    lp_farm_supply,
    total_sum == lp_farm_supply,
    current_block,
)
with open(
    Path(BASE_DIR, "data", "crveth", "farm_snapshot.csv"), "w", newline=""
) as file:
    writer = csv.writer(file)
    writer.writerows(data)

with open(
    Path(BASE_DIR, "data", "crveth", "farm_overall.csv"), "w", newline=""
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
                lp_farm_supply,
                balances[0],
                balances[1],
                eth_per_lp,
                crv_per_lp,
                total_sum,
            ],
        ]
    )
