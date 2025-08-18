from mcdreforged.utils.serializer import Serializable


class Order(Serializable):
    time: str
    sender: str
    receiver: str
    item: str
    comment: str


class IdGivenOrder(Serializable):
    id: int
    time: str
    sender: str
    receiver: str
    item: str
    comment: str


class OrderData(Serializable):
    players: list[str] = []
    orders: dict[str | int, IdGivenOrder] = []

    def get_next_id(self) -> int:
        """获取下一个合法 id"""
        order_id = 1
        for order in self.orders.values():
            if order_id == order.id:
                order_id += 1
        return order_id

    def add_order(self, order: Order | IdGivenOrder) -> int:
        """添加订单

        订单对象可以是简单的 Order, 也可以是能够自定义 id 的 IdGivenOrder.
        如果是 Order, 会自动分配一个 id;
        如果是 IdGivenOrder, 则会直接使用给定的 id

        .. attention::
            **方法不会检查 IdGivenOrder 的 id 合法性，推荐使用 Order 自动分配 id.**
        """
        if isinstance(order, Order):
            order_id = self.get_next_id()
            self.orders[str(order_id)] = IdGivenOrder(
                id=order_id,
                time=order.time,
                sender=order.sender,
                receiver=order.receiver,
                item=order.item,
                comment=order.comment
            )
            return order_id
        elif isinstance(order, IdGivenOrder):
            self.orders[order.id] = order
            return order.id
        else:
            assert False

    def remove_order(self, order_id: int):
        self.orders.pop(f"{order_id}")

    def get_orderid_by_receiver(self, receiver: str) -> list:
        """根据 receiver 获取订单 id"""
        return [order for order in self.orders.values() if order.receiver == receiver]

    def get_orderid_by_sender(self, sender: str) -> list:
        """根据 sender 获取订单 id"""
        return [order for order in self.orders.values() if order.sender == sender]

    def add_player(self, player: str):
        self.players.append(player)

    def remove_player(self, player: str):
        self.players.remove(player)
