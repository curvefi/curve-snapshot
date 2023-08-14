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

    def total_supply(self, block_identifier: BlockIdentifier = "latest") -> float:
        return self.contract.functions.totalSupply().call(
            block_identifier=block_identifier
        )

    def balanceOf(
        self, address: str, block_identifier: BlockIdentifier = "latest"
    ) -> float:
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
