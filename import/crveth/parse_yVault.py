import csv
import json
from pathlib import Path

from web3 import Web3

from contract.erc20 import ERC20Contract, YERC20Contract
from contract.pool_contract import PoolContract
from settings import BASE_DIR, settings, web3_provider

lp = "0xEd4064f376cB8d68F770FB1Ff088a3d0F3FF5c4d"
lp_contract = ERC20Contract(lp)
gauge = "0x1cEBdB0856dd985fAe9b8fEa2262469360B8a3a6"
gauge_contract = ERC20Contract(gauge)
yearn_addr = "0x6f0Ace0F94f4B9890Dfa99A4175B3Ef0288C16B3"
yearn_contract = YERC20Contract(yearn_addr)
pool = "0x8301AE4fc9c624d1D396cbDAa1ed877821D7C511"
pool_contract = PoolContract(pool)
yearn_vault_addr = "0x3DD9636CA2b554cCCd219d73796e80d819c90CBa"
yearn_vault_token_addr = "0x6A5468752f8DB94134B6508dAbAC54D3b45efCE6"
yearn_vault = YERC20Contract(yearn_vault_token_addr)
start_block = 13676983
block = 17807829
web3 = Web3(web3_provider)


current_block = json.loads(Web3.to_json(web3.eth.get_block("latest")))["number"]

total_assets = yearn_vault.totalAssets(block_identifier=block)
print(total_assets)


lp_total_supply = lp_contract.total_supply(block_identifier=block)
lp_yearn_supply = (
    yearn_contract.balanceOf(yearn_vault_addr, block_identifier=block)
    * yearn_contract.pricePerShare(block_identifier=block)
    // 10**18
)
balances = pool_contract.balances(block_identifier=block)
balances = (
    balances[0] * lp_yearn_supply / lp_total_supply,
    balances[1] * lp_yearn_supply / lp_total_supply,
)
price_per_share = yearn_vault.pricePerShare(block_identifier=block) / 10**18

eth_per_lp, crv_per_lp = (
    price_per_share * balances[0] / lp_yearn_supply,
    price_per_share * balances[1] / lp_yearn_supply,
)

users = []
with open(Path(BASE_DIR, "data", "crveth", "all_users_yvault.csv"), "r") as file:
    reader = csv.reader(file)
    for row in reader:
        users.append(row[0])

user_balances = []
sum_ = 0

for user in users:
    balance = int(yearn_vault.balanceOf(user, block_identifier=block) * price_per_share)
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
    sum_,
    current_block,
)
with open(
    Path(BASE_DIR, "data", "crveth", "yvault_snapshot.csv"), "w", newline=""
) as file:
    writer = csv.writer(file)
    writer.writerows(data)

with open(
    Path(BASE_DIR, "data", "crveth", "yvault_overall.csv"), "w", newline=""
) as file:
    writer = csv.writer(file)
    writer.writerows(
        [
            [
                "Total LP",
                "Balances ETH",
                "Balances alETH",
                "ETH per LP",
                "CRV per LP",
                "Total User Balances",
            ],
            [
                lp_yearn_supply,
                balances[0],
                balances[1],
                eth_per_lp,
                crv_per_lp,
                sum_,
            ],
        ]
    )
