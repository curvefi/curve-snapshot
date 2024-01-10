import csv
import json
from pathlib import Path

from web3 import Web3

from contract.erc20 import ERC20Contract
from settings import BASE_DIR, fantom_web3_provider

lp = "0x8B63F036F5a34226065bC0a7B0aE5bb5eBA1fF3D"
lp_contract = ERC20Contract(lp, provider=fantom_web3_provider)
gauge = "0xc1c5B8aAfE653592627B54B9527C7E98326e83Ff"
gauge_contract = ERC20Contract(gauge, provider=fantom_web3_provider)
start_block = 25071568
block = 66461147
web3 = Web3(fantom_web3_provider)


current_block = json.loads(Web3.to_json(web3.eth.get_block("latest")))["number"]

users = set()

for i in range((block - start_block) // 10000 + 1):
    start, end = start_block + 10000 * i, start_block + 10000 * (i + 1)
    print(start, end)
    events = lp_contract.get_transfer_events(fromBlock=start, toBlock=end)
    for event in events:
        print(event["args"]["_to"])
        users.add(event["args"]["_to"])

for i in range((block - start_block) // 10000 + 1):
    start, end = start_block + 10000 * i, start_block + 10000 * (i + 1)
    print(start, end)
    events = gauge_contract.get_transfer_events(fromBlock=start, toBlock=end)
    for event in events:
        print(event["args"]["_to"])
        users.add(event["args"]["_to"])


with open(Path(BASE_DIR, "data", "ftml", "all_users.csv"), "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows([[u] for u in users])
