from functools import cached_property

from web3.contract.contract import ContractEvent
from web3.types import BlockIdentifier, EventData

from contract.base import Contract


class ERC20Contract(Contract):
    @property
    def abi(self) -> list[dict]:
        return [
            {
                "name": "balanceOf",
                "inputs": [
                    {"internalType": "address", "name": "account", "type": "address"}
                ],
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function",
            },
            {
                "name": "decimals",
                "inputs": [],
                "outputs": [{"name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function",
            },
            {
                "name": "name",
                "inputs": [],
                "outputs": [{"type": "string", "name": ""}],
                "stateMutability": "view",
                "type": "function",
            },
            {
                "name": "symbol",
                "inputs": [],
                "outputs": [{"type": "string", "name": ""}],
                "stateMutability": "view",
                "type": "function",
            },
            {
                "name": "totalSupply",
                "inputs": [],
                "outputs": [{"name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function",
            },
            {
                "name": "Transfer",
                "inputs": [
                    {"name": "_from", "type": "address", "indexed": True},
                    {"name": "_to", "type": "address", "indexed": True},
                    {"name": "_value", "type": "uint256", "indexed": False},
                ],
                "anonymous": False,
                "type": "event",
            },
        ]

    @cached_property
    def name(self) -> str:
        return self.contract.functions.name().call()

    @cached_property
    def symbol(self) -> str:
        return self.contract.functions.symbol().call()

    @cached_property
    def precision(self) -> int:
        decimals = self.contract.functions.decimals().call()
        return 10**decimals

    def total_supply(self, block_identifier: BlockIdentifier = "latest") -> int:
        return self.contract.functions.totalSupply().call(
            block_identifier=block_identifier
        )

    def balanceOf(
        self, address: str, block_identifier: BlockIdentifier = "latest"
    ) -> int:
        return self.contract.functions.balanceOf(address).call(
            block_identifier=block_identifier
        )

    @cached_property
    def transfer_event(self) -> ContractEvent:
        return self.contract.events.Transfer

    def get_transfer_events(
        self,
        fromBlock: BlockIdentifier,
        toBlock: BlockIdentifier,
        _from: str = None,
        _to: str = None,
    ) -> list[EventData]:
        argument_filters = {}
        if _from:
            argument_filters["_from"] = _from
        if _to:
            argument_filters["_to"] = _to

        if not argument_filters:
            argument_filters = None

        return list(
            self.transfer_event.get_logs(
                argument_filters=argument_filters, fromBlock=fromBlock, toBlock=toBlock
            )
        )


class YERC20Contract(ERC20Contract):
    @property
    def abi(self) -> list[dict]:
        return super().abi + [
            {
                "stateMutability": "view",
                "type": "function",
                "name": "pricePerShare",
                "inputs": [],
                "outputs": [{"name": "", "type": "uint256"}],
            },
            {
                "stateMutability": "view",
                "type": "function",
                "name": "totalAssets",
                "inputs": [],
                "outputs": [{"name": "", "type": "uint256"}],
            },
        ]

    def pricePerShare(self, block_identifier: BlockIdentifier = "latest") -> int:
        return self.contract.functions.pricePerShare().call(
            block_identifier=block_identifier
        )

    def totalAssets(self, block_identifier: BlockIdentifier = "latest") -> int:
        return self.contract.functions.totalAssets().call(
            block_identifier=block_identifier
        )


class BeefyERC20Contract(ERC20Contract):
    @property
    def abi(self) -> list[dict]:
        return super().abi + [
            {
                "stateMutability": "view",
                "type": "function",
                "name": "getPricePerFullShare",
                "inputs": [],
                "outputs": [{"name": "", "type": "uint256"}],
            }
        ]

    def getPricePerFullShare(self, block_identifier: BlockIdentifier = "latest") -> int:
        return self.contract.functions.getPricePerFullShare().call(
            block_identifier=block_identifier
        )


class ConcERC20Contract(Contract):
    @property
    def abi(self) -> list[dict]:
        return [
            {
                "stateMutability": "view",
                "type": "function",
                "name": "getUserShare",
                "inputs": [
                    {"type": "uint256", "name": "_pid"},
                    {"type": "address", "name": "_account"},
                ],
                "outputs": [{"name": "", "type": "uint256"}],
            },
            {
                "stateMutability": "view",
                "type": "function",
                "name": "getTotalShare",
                "inputs": [{"type": "uint256", "name": "_pid"}],
                "outputs": [{"name": "", "type": "uint256"}],
            },
            {
                "stateMutability": "view",
                "type": "function",
                "name": "getTotalUnderlying",
                "inputs": [{"type": "uint256", "name": "_pid"}],
                "outputs": [{"name": "", "type": "uint256"}],
            },
            {
                "name": "Deposit",
                "type": "event",
                "anonymous": False,
                "inputs": [
                    {
                        "indexed": True,
                        "internalType": "uint256",
                        "name": "_pid",
                        "type": "uint256",
                    },
                    {
                        "indexed": True,
                        "internalType": "address",
                        "name": "_sender",
                        "type": "address",
                    },
                    {
                        "indexed": False,
                        "internalType": "uint256",
                        "name": "_amount",
                        "type": "uint256",
                    },
                ],
            },
        ]

    def getUserShare(
        self, _pid: int, user: str, block_identifier: BlockIdentifier = "latest"
    ) -> int:
        return self.contract.functions.getUserShare(_pid, user).call(
            block_identifier=block_identifier
        )

    def getTotalShare(
        self, _pid: int, block_identifier: BlockIdentifier = "latest"
    ) -> int:
        return self.contract.functions.getTotalShare(_pid).call(
            block_identifier=block_identifier
        )

    def getTotalUnderlying(
        self, _pid: int, block_identifier: BlockIdentifier = "latest"
    ) -> int:
        return self.contract.functions.getTotalUnderlying(_pid).call(
            block_identifier=block_identifier
        )

    @cached_property
    def deposit_event(self) -> ContractEvent:
        return self.contract.events.Deposit

    def get_deposit_events(
        self,
        fromBlock: BlockIdentifier,
        toBlock: BlockIdentifier,
        _pid: int = None,
    ) -> list[EventData]:
        argument_filters = {}
        if _pid:
            argument_filters["_pid"] = _pid

        if not argument_filters:
            argument_filters = None

        return list(
            self.deposit_event.get_logs(
                argument_filters=argument_filters, fromBlock=fromBlock, toBlock=toBlock
            )
        )


class FarmERC20Contract(BeefyERC20Contract):
    @property
    def abi(self) -> list[dict]:
        return super().abi + [
            {
                "stateMutability": "view",
                "type": "function",
                "name": "underlyingBalanceWithInvestmentForHolder",
                "inputs": [{"name": "holder", "type": "address"}],
                "outputs": [{"name": "", "type": "uint256"}],
            },
        ]

    def underlyingBalanceWithInvestmentForHolder(
        self, user: str, block_identifier: BlockIdentifier = "latest"
    ) -> int:
        return self.contract.functions.underlyingBalanceWithInvestmentForHolder(
            user
        ).call(block_identifier=block_identifier)
