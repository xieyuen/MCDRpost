from typing import TypedDict

from mcdreforged.api.utils import Serializable


class OrderInfo(Serializable):
    time: str
    sender: str
    receiver: str
    item: str
    comment: str


class OrderInfoDict(TypedDict):
    time: str
    sender: str
    receiver: str
    item: str
    comment: str


class Order(OrderInfo):
    id: int


class OrderData(Serializable):
    players: list[str] = []
    orders: dict[str, Order] = {}
