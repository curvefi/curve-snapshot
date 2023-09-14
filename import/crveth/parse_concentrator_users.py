import csv
import json
from pathlib import Path

from web3 import Web3

from contract.erc20 import ConcERC20Contract
from settings import BASE_DIR, web3_provider

conc = "0x3Cf54F3A1969be9916DAD548f3C084331C4450b5"
lp_contract = ConcERC20Contract(conc)
start_block = 13676983
block = 17807829
web3 = Web3(web3_provider)


current_block = json.loads(Web3.to_json(web3.eth.get_block("latest")))["number"]

users = set()

for i in range((block - start_block) // 1000 + 1):
    start, end = start_block + 1000 * i, start_block + 1000 * (i + 1)
    print(start, end)
    events = lp_contract.get_deposit_events(_pid=4, fromBlock=start, toBlock=end)
    for event in events:
        print(event["args"]["_sender"])
        users.add(event["args"]["_sender"])


with open(
    Path(BASE_DIR, "data", "crveth", "concentrator_users.csv"), "w", newline=""
) as file:
    writer = csv.writer(file)
    writer.writerows([[u] for u in users])
