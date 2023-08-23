import csv
import json
from pathlib import Path

from web3 import Web3

from contract.erc20 import ERC20Contract
from settings import BASE_DIR, web3_provider

lp = "0xC4C319E2D4d66CcA4464C0c2B32c9Bd23ebe784e"
lp_contract = ERC20Contract(lp)
gauge = "0x12dCD9E8D1577b5E4F066d8e7D404404Ef045342"
gauge_contract = ERC20Contract(gauge)
start_block = 13227441
block = 17806740
web3 = Web3(web3_provider)


current_block = json.loads(Web3.to_json(web3.eth.get_block("latest")))["number"]

users = set()

for i in range((block - start_block) // 1000 + 1):
    start, end = start_block + 1000 * i, start_block + 1000 * (i + 1)
    print(start, end)
    events = lp_contract.get_transfer_events(fromBlock=start, toBlock=end)
    for event in events:
        print(event["args"]["_to"])
        users.add(event["args"]["_to"])


for i in range((block - start_block) // 1000 + 1):
    start, end = start_block + 1000 * i, start_block + 1000 * (i + 1)
    print(start, end)
    events = gauge_contract.get_transfer_events(fromBlock=start, toBlock=end)
    for event in events:
        print(event["args"]["_to"])
        users.add(event["args"]["_to"])


with open(Path(BASE_DIR, "data", "aleth", "all_users.csv"), "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows([[u] for u in users])
