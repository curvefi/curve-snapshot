from functools import cached_property
from typing import Iterable

from web3.contract.contract import ContractEvent, EventData
from web3.types import BlockIdentifier

from contract.base import Contract


class PoolContract(Contract):
    @property
    def abi(self) -> list[dict]:
        return [
            {
                "stateMutability": "view",
                "type": "function",
                "name": "balances",
                "inputs": [{"name": "arg0", "type": "uint256"}],
                "outputs": [{"name": "", "type": "uint256"}],
            },
            {
                "name": "TokenExchange",
                "inputs": [
                    {"name": "buyer", "type": "address", "indexed": True},
                    {"name": "sold_id", "type": "uint256", "indexed": False},
                    {"name": "tokens_sold", "type": "uint256", "indexed": False},
                    {"name": "bought_id", "type": "uint256", "indexed": False},
                    {"name": "tokens_bought", "type": "uint256", "indexed": False},
                ],
                "anonymous": False,
                "type": "event",
            },
            {
                "name": "AddLiquidity",
                "inputs": [
                    {"name": "provider", "type": "address", "indexed": True},
                    {"name": "token_amounts", "type": "uint256[2]", "indexed": False},
                    {"name": "fee", "type": "uint256", "indexed": False},
                    {"name": "token_supply", "type": "uint256", "indexed": False},
                ],
                "anonymous": False,
                "type": "event",
            },
            {
                "name": "RemoveLiquidity",
                "inputs": [
                    {"name": "provider", "type": "address", "indexed": True},
                    {"name": "token_amounts", "type": "uint256[2]", "indexed": False},
                    {"name": "token_supply", "type": "uint256", "indexed": False},
                ],
                "anonymous": False,
                "type": "event",
            },
            {
                "name": "RemoveLiquidityOne",
                "inputs": [
                    {"name": "provider", "type": "address", "indexed": True},
                    {"name": "token_amount", "type": "uint256", "indexed": False},
                    {"name": "coin_index", "type": "uint256", "indexed": False},
                    {"name": "coin_amount", "type": "uint256", "indexed": False},
                ],
                "anonymous": False,
                "type": "event",
            },
        ]

    def balances(self, block_identifier: BlockIdentifier = "latest") -> tuple[int, int]:
        return self.contract.functions.balances(0).call(
            block_identifier=block_identifier
        ), self.contract.functions.balances(1).call(block_identifier=block_identifier)

    @cached_property
    def token_exchange_event(self) -> ContractEvent:
        return self.contract.events.TokenExchange

    @cached_property
    def add_liquidity_event(self) -> ContractEvent:
        return self.contract.events.AddLiquidity

    @cached_property
    def remove_liquidity_event(self) -> ContractEvent:
        return self.contract.events.RemoveLiquidity

    @cached_property
    def remove_liquidity_one_event(self) -> ContractEvent | None:
        return self.contract.events.RemoveLiquidityOne

    def get_token_exchange_logs(
        self, fromBlock: BlockIdentifier, toBlock: BlockIdentifier
    ) -> Iterable[EventData]:
        return self.token_exchange_event.get_logs(fromBlock=fromBlock, toBlock=toBlock)

    def get_liquidity_change_logs(
        self, fromBlock: BlockIdentifier, toBlock: BlockIdentifier, user: str | None
    ) -> list[EventData]:
        argument_filters = {"provider": user} if user else None
        events = list(
            self.add_liquidity_event.get_logs(
                fromBlock=fromBlock, toBlock=toBlock, argument_filters=argument_filters
            )
        )
        events.extend(
            self.remove_liquidity_event.get_logs(
                fromBlock=fromBlock, toBlock=toBlock, argument_filters=argument_filters
            )
        )
        events.extend(
            self.remove_liquidity_one_event.get_logs(
                fromBlock=fromBlock, toBlock=toBlock, argument_filters=argument_filters
            )
        )
        return events


class AlEthPoolContract(PoolContract):
    @property
    def abi(self) -> list[dict]:
        return [
            {
                "stateMutability": "view",
                "type": "function",
                "name": "balances",
                "inputs": [{"name": "arg0", "type": "uint256"}],
                "outputs": [{"name": "", "type": "uint256"}],
            },
            {
                "name": "Transfer",
                "inputs": [
                    {"name": "sender", "type": "address", "indexed": True},
                    {"name": "receiver", "type": "address", "indexed": True},
                    {"name": "value", "type": "uint256", "indexed": False},
                ],
                "anonymous": False,
                "type": "event",
            },
            {
                "name": "TokenExchange",
                "inputs": [
                    {"name": "buyer", "type": "address", "indexed": True},
                    {"name": "sold_id", "type": "int128", "indexed": False},
                    {"name": "tokens_sold", "type": "uint256", "indexed": False},
                    {"name": "bought_id", "type": "int128", "indexed": False},
                    {"name": "tokens_bought", "type": "uint256", "indexed": False},
                ],
                "anonymous": False,
                "type": "event",
            },
            {
                "name": "AddLiquidity",
                "inputs": [
                    {"name": "provider", "type": "address", "indexed": True},
                    {"name": "token_amounts", "type": "uint256[2]", "indexed": False},
                    {"name": "fees", "type": "uint256[2]", "indexed": False},
                    {"name": "invariant", "type": "uint256", "indexed": False},
                    {"name": "token_supply", "type": "uint256", "indexed": False},
                ],
                "anonymous": False,
                "type": "event",
            },
            {
                "name": "RemoveLiquidity",
                "inputs": [
                    {"name": "provider", "type": "address", "indexed": True},
                    {"name": "token_amounts", "type": "uint256[2]", "indexed": False},
                    {"name": "fees", "type": "uint256[2]", "indexed": False},
                    {"name": "token_supply", "type": "uint256", "indexed": False},
                ],
                "anonymous": False,
                "type": "event",
            },
            {
                "name": "RemoveLiquidityOne",
                "inputs": [
                    {"name": "provider", "type": "address", "indexed": True},
                    {"name": "token_amount", "type": "uint256", "indexed": False},
                    {"name": "coin_amount", "type": "uint256", "indexed": False},
                    {"name": "token_supply", "type": "uint256", "indexed": False},
                ],
                "anonymous": False,
                "type": "event",
            },
        ]
