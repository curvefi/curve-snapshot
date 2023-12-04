#!/usr/bin/enb python3
import pandas as pd
from brownie import Contract, config

config["autofetch_sources"] = True

POOLS = [
    (
        "crveth",
        "0x8301ae4fc9c624d1d396cbdaa1ed877821d7c511",
        17807829,
        "crveth_overall.csv",
        2,
    ),
    (
        "aleth",
        "0xc4c319e2d4d66cca4464c0c2b32c9bd23ebe784e",
        17806742,
        "aleth_overall.csv",
        1,
    ),
    (
        "mseth",
        "0xc897b98272aa23714464ea2a0bd5180f1b8c0025",
        17806549,
        "mseth_overall.csv",
        1,
    ),
]
types = {
    "User": str,
    "LP Balance": float,
    "LP Balance - withdrawn": float,
    "is_contract": bool,
}
current_prices = {"crveth": 0.5993 / 2085}
# First coin is always ETH or WETH

replaced_addresses = {
    "0x562C0bc16A7BBe9Fb73902694D3AF8cb24Aa3768": "0x2ECd81E43C1F66185446F4af7DfEAa6AAE249f55",
    "0x01C9B838BE2c60181cef4Be3160d6F44daEe0a99": "0x1F020A4943EB57cd3b2213A66b355CB662Ea43C3",
    "0xe761bf731A06fE8259FeE05897B2687D56933110": "0x9e2b6378ee8ad2A4A95Fe481d63CAba8FB0EBBF9",
    "0x2d0aba145D6A0c071CfF3bD87CC4b8475413D895": "0x044D1552f9e159bA469787043404a6b8A0449bBB",
}


def main():
    for name, address, block, fname, pool_type in POOLS:
        pool = Contract(address)
        if hasattr(pool, "token"):
            token = Contract(pool.token())
        else:
            token = pool
        coin1_name = Contract(pool.coins(1)).symbol()
        vprice = pool.get_virtual_price(block_identifier=block)
        supply = token.totalSupply(block_identifier=block)
        balances = [pool.balances(i, block_identifier=block) for i in [0, 1]]

        df = pd.read_csv("data/" + fname, dtype=types)

        for from_addr, to_addr in replaced_addresses.items():
            cond = df["User"] == from_addr
            df.loc[cond, "contract_type"] = "multisig"
            df.loc[cond, "User"] = to_addr

        df = df[
            (df["contract_type"] == "multisig") | (df["is_contract"] == False)  # noqa
        ]

        new_df = pd.DataFrame()
        new_df["User"] = df["User"]
        new_df["ETH before hack"] = df["LP Balance"] / supply * balances[0] / 1e18
        new_df["%s before hack" % coin1_name] = (
            df["LP Balance"] / supply * balances[1] / 1e18
        )
        new_df["% not recovered by user"] = (
            df["LP Balance - withdrawn"] / df["LP Balance"] * 100
        )
        new_df["is_multisig"] = df["contract_type"] == "multisig"

        if pool_type == 1:  # Stableswap
            new_df["ETH to recover"] = (
                df["LP Balance - withdrawn"] / 1e18 * vprice / 1e18
            )

        else:  # Crypto
            balances_product = (supply / 1e18 * vprice / 1e18) ** 2
            p_new = current_prices[name]
            new_coin0 = (balances_product * p_new) ** 0.5
            new_coin1 = (balances_product / p_new) ** 0.5
            new_df["ETH to recover"] = new_coin0 * df["LP Balance - withdrawn"] / supply
            new_df["%s to recover" % coin1_name] = (
                new_coin1 * df["LP Balance - withdrawn"] / supply
            )
            new_df["Missed rewards in %s" % coin1_name] = (
                0.12
                * 4
                / 12
                * (new_coin1 * 2)
                * df["LP Balance - withdrawn"]
                / supply
            )

        new_df = new_df[
            new_df["ETH to recover"] > 1e-4
        ]  # Dust cutoff - not worth gas to claim here

        new_df.to_csv("data/%s-reprocessed.csv" % name)
