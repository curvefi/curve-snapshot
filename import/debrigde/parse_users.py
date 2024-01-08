import csv
import json
from pathlib import Path

from web3 import Web3

from contract.erc20 import ERC20Contract
from settings import BASE_DIR, arbi_web3_provider

lp = "0x0a824B5d4C96EA0EC46306Efbd34Bf88fE1277e0"
lp_contract = ERC20Contract(lp, provider=arbi_web3_provider)
start_block = 4943178
block = 116468639
web3 = Web3(arbi_web3_provider)


current_block = json.loads(Web3.to_json(web3.eth.get_block("latest")))["number"]

users = set()

for i in range((block - start_block) // 10000 + 1):
    start, end = start_block + 10000 * i, start_block + 10000 * (i + 1)
    print(start, end)
    events = lp_contract.get_transfer_events(fromBlock=start, toBlock=end)
    for event in events:
        print(event["args"]["_to"])
        users.add(event["args"]["_to"])


with open(Path(BASE_DIR, "data", "debridge", "all_users.csv"), "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows([[u] for u in users])
