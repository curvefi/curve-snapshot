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
    }


settings = Settings()
web3_provider = Web3.HTTPProvider(settings.WEB3_PROVIDER_URL)
async_web3_provider = Web3.AsyncHTTPProvider(settings.WEB3_PROVIDER_URL)
