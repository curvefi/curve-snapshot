import csv
import json
from pathlib import Path

from web3 import Web3

from contract.erc20 import ERC20Contract
from settings import BASE_DIR, web3_provider

lp = "0xc897b98272AA23714464Ea2A0Bd5180f1B8C0025"
lp_contract = ERC20Contract(lp)
gauge = "0x941C2Acdb6B85574Ffc44419c2AA237a9e67be03"
gauge_contract = ERC20Contract(gauge)
start_block = 16371623
block = 17806549
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


with open(Path(BASE_DIR, "data", "mseth", "all_users.csv"), "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows([[u] for u in users])
