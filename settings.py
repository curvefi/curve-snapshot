from pathlib import Path

import dotenv
from pydantic import BaseSettings
from web3 import Web3

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    class Config:
        env_file = Path(BASE_DIR, ".env")
        dotenv.load_dotenv(env_file)

    WEB3_PROVIDER_URL: str = "http://localhost:8545"

    contract_names: dict[str, str] = {
        "0x1cEBdB0856dd985fAe9b8fEa2262469360B8a3a6": "gauge",
        "0x6f0Ace0F94f4B9890Dfa99A4175B3Ef0288C16B3": "yVault",
        "0x989AEb4d175e16225E39E87d0D97A3360524AD80": "convex",
        "0xF147b8125d2ef93FB6965Db97D6746952a133934": "yCRV",
        "0x52f541764E6e90eeBc5c21Ff570De0e2D63766B6": "stakedao",
        "0x941C2Acdb6B85574Ffc44419c2AA237a9e67be03": "gauge",
        "0x12dCD9E8D1577b5E4F066d8e7D404404Ef045342": "gauge",
        "0xe761bf731A06fE8259FeE05897B2687D56933110": "alchemix",
        "0x3bCF3Db69897125Aa61496Fc8a8B55A5e3f245d5": "multisig",
        "0xD5bA79D098679730CbF45d4CFcf52aAD5aC8bC8E": "numisme",
        "0x4bfb33d65f4167EBE190145939479227E7bf2CB0": "multisig",
        "0x942d484C008d86C92d62fce9Cbdf010f89d4F899": "multisig",
        "0x3DD9636CA2b554cCCd219d73796e80d819c90CBa": "yVault",
        "0x2d0aba145D6A0c071CfF3bD87CC4b8475413D895": "multisig",
        "0xc7599b60f05639f93D26e58d56D90C526A6e7575": "multisig",
        "0x506Eb3dc29389cEA11768cCe6a01Fca4996Fa30c": "multisig",
        "0x0e119685190CA54B5BBf5E3504F447C5E40d2410": "multisig",
        "0x70CCBE10F980d80b7eBaab7D2E3A73e87D67B775": "gitcoin grants",
        "0x114777cA6c3967ddEe23523B775e1d1f385D7Deb": "multisig",
        "0xeCb456EA5365865EbAb8a2661B0c503410e9B347": "pool owner",
        "0xd1DE3F9CD4AE2F23DA941a67cA4C739f8dD9Af33": "multisig"
    }


settings = Settings()
web3_provider = Web3.HTTPProvider(settings.WEB3_PROVIDER_URL)
async_web3_provider = Web3.AsyncHTTPProvider(settings.WEB3_PROVIDER_URL)
