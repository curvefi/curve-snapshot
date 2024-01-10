import csv
import json
from pathlib import Path

from web3 import Web3

from contract.erc20 import ERC20Contract, BeefyERC20Contract
from contract.pool_contract import PoolContract
from settings import BASE_DIR, settings, fantom_web3_provider

lp = "0x8B63F036F5a34226065bC0a7B0aE5bb5eBA1fF3D"
lp_contract = ERC20Contract(lp, provider=fantom_web3_provider)
pool = "0x8B63F036F5a34226065bC0a7B0aE5bb5eBA1fF3D"
pool_contract = PoolContract(pool, provider=fantom_web3_provider)
gauge = "0xc1c5B8aAfE653592627B54B9527C7E98326e83Ff"
gauge_contract = ERC20Contract(gauge, provider=fantom_web3_provider)
beefy_address = '0xd6479545171d5D9c360129D820cC060f9A063bc8'
beefy = "0xaD3aD0D7140529eD329D7c9b4D876e1fBd7B2330"
beefy_contract = BeefyERC20Contract(beefy, provider=fantom_web3_provider)
start_block = 25071568
block = 66461147
web3 = Web3(fantom_web3_provider)


current_block = json.loads(Web3.to_json(web3.eth.get_block("latest")))["number"]

lp_total_supply = lp_contract.total_supply(block_identifier=block)
lp_moo_supply = gauge_contract.balanceOf(beefy_address, block_identifier=block)
balances = pool_contract.balances(block_identifier=block)
balances = (
    balances[0] * lp_moo_supply / lp_total_supply,
    balances[1] * lp_moo_supply / lp_total_supply,
)
price_per_share = beefy_contract.getPricePerFullShare(block_identifier=block) / 10**18

ftm_per_lp, ftml_per_lp = balances[0] / lp_moo_supply, balances[1] / lp_moo_supply


users = []
with open(Path(BASE_DIR, "data", "ftml", "all_users.csv"), "r") as file:
    reader = csv.reader(file)
    for row in reader:
        users.append(row[0])


user_balances = []
total_sum = 0
for user in users:
    balance = int(beefy_contract.balanceOf(user, block_identifier=block) * price_per_share)
    if balance > 0:
        code = web3.eth.get_code(user, block_identifier=block)
        events = pool_contract.get_liquidity_change_logs(
            block, current_block, user=user
        )
        withdrawn_ftm = 0
        withdrawn_ftml = 0
        if events:
            for event in events:
                if event["event"] == "RemoveLiquidity":
                    withdrawn_ftm += event["args"]["token_amounts"][0]
                    withdrawn_ftml += event["args"]["token_amounts"][1]
                elif event["event"] == "RemoveLiquidityOne":
                    if event["args"]["coin_index"] == 0:
                        withdrawn_ftm += event["args"]["coin_amount"]
                    elif event["args"]["coin_index"] == 1:
                        withdrawn_ftml += event["args"]["coin_amount"]

        user_balances.append(
            {
                "user": user,
                "balance": balance,
                "is_contract": bool(code),
                "events": events,
                "withdrawn_ftm": withdrawn_ftm,
                "withdrawn_ftml": withdrawn_ftml,
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
        "withdrawn_ftm",
        "withdrawn_ftml",
        "ftm_to_redeem",
        "ftml_to_redeem",
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
            user["withdrawn_ftm"],
            user["withdrawn_ftml"],
            user["balance"] * ftm_per_lp - user["withdrawn_ftm"],
            user["balance"] * ftml_per_lp - user["withdrawn_ftml"],
        ]
    )

print(
    total_sum,
    lp_moo_supply,
    total_sum == lp_moo_supply,
    current_block,
)
with open(
    Path(BASE_DIR, "data", "ftml", "beefy_snapshot.csv"), "w", newline=""
) as file:
    writer = csv.writer(file)
    writer.writerows(data)

with open(
    Path(BASE_DIR, "data", "ftml", "beefy_overall.csv"), "w", newline=""
) as file:
    writer = csv.writer(file)
    writer.writerows(
        [
            [
                "Total LP",
                "Balances ETH",
                "Balances CRV",
                "FTM per LP",
                "Ftml per LP",
                "Total User Balances",
            ],
            [
                lp_moo_supply,
                balances[0],
                balances[1],
                ftm_per_lp,
                ftml_per_lp,
                total_sum,
            ],
        ]
    )
