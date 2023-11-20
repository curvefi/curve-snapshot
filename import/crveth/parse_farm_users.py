import csv
import json
from pathlib import Path

from web3 import Web3

from contract.erc20 import ERC20Contract
from settings import BASE_DIR, web3_provider

farm = "0xd7b17297B9884Aa73BF5E6e39e3cEC107ffe6b17"
farm_contract = ERC20Contract(farm)
start_block = 14166582
block = 17807829
web3 = Web3(web3_provider)


current_block = json.loads(Web3.to_json(web3.eth.get_block("latest")))["number"]

users = set()

for i in range((block - start_block) // 1000 + 1):
    start, end = start_block + 1000 * i, start_block + 1000 * (i + 1)
    print(start, end)
    events = farm_contract.get_transfer_events(fromBlock=start, toBlock=end)
    for event in events:
        print(event["args"]["_to"])
        users.add(event["args"]["_to"])


with open(
    Path(BASE_DIR, "data", "crveth", "all_farm_users.csv"), "w", newline=""
) as file:
    writer = csv.writer(file)
    writer.writerows([[u] for u in users])
