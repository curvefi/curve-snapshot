import csv
import json
from pathlib import Path

from web3 import Web3

from contract.erc20 import ERC20Contract
from settings import BASE_DIR, web3_provider

lp = "0xEd4064f376cB8d68F770FB1Ff088a3d0F3FF5c4d"
lp_contract = ERC20Contract(lp)
gauge = "0x1cEBdB0856dd985fAe9b8fEa2262469360B8a3a6"
gauge_contract = ERC20Contract(gauge)
yearn_contract = ERC20Contract("0x6f0Ace0F94f4B9890Dfa99A4175B3Ef0288C16B3")
start_block = 13676983
block = 17807829
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


for i in range((block - start_block) // 1000 + 1):
    start, end = start_block + 1000 * i, start_block + 1000 * (i + 1)
    print(start, end)
    events = yearn_contract.get_transfer_events(fromBlock=start, toBlock=end)
    for event in events:
        print(event["args"]["_to"])
        users.add(event["args"]["_to"])


with open(Path(BASE_DIR, "data", "crveth", "all_users.csv"), "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows([[u] for u in users])
