import json

from mcdreforged.api.types import PluginServerInterface, InfoCommandSource

from mcdrpost import constants, play_sound
from mcdrpost.config import Configuration
from mcdrpost.exception import InvalidOrder, InvalidRegisteredPlayerList
from mcdrpost.order_data import OrderData, Order, IdGivenOrder
from mcdrpost.utils import tr, replace_offhand, get_offhand_item, formatted_time, can_command_item


class PostManager:
    """
    邮寄管理器

    Attributes:
        config (Configuration): 插件配置信息
        logger (MCDReforgedLogger): MCDR 日志
        server (PluginServerInterface): MCDR 服务器接口
        orders (OrderData): 订单数据
    """

    def __init__(self, server: PluginServerInterface):
        self.config = server.load_config_simple(
            constants.CONFIG_FILE_NAME,
            target_class=Configuration,
            file_format="yaml",
        )
        self.logger = server.logger
        self.server = server

        self.orders = server.load_config_simple(
            constants.ORDERS_DATA_FILE_NAME,
            target_class=OrderData,
        )
        self.__check_orders()

        self.is_allow_item: int = can_command_item(server)

    def __check_orders(self) -> None:
        """检查 order 的合法性

        Raises:
            InvalidOrder: 如果 order 不合法，即 key 和 order.id 对不上
            InvalidRegisteredPlayerList: 如果已注册玩家有重复
        """
        if len(self.orders.players) != len(set(self.orders.players)):
            if not self.config.auto_fix:
                raise InvalidRegisteredPlayerList("已注册玩家有重复")
            self.logger.error("已注册玩家有重复")
        if self.config.auto_fix:
            need_fix = []
        else:
            need_fix = None
        for order_id, order in self.orders.orders.items():
            if str(order.id) != order_id:
                if need_fix is None:
                    raise InvalidOrder(f"Order (from {order.sender} to {order.receiver}) had invalid id")

                self.logger.error(f"Order (from {order.sender} to {order.receiver}) had invalid id")
                self.logger.error(f"Fixing order id to {order.id}")
                need_fix.append((order_id, order))

        if not need_fix:
            return

        for order_id, order in need_fix:
            self.orders.orders.pop(order_id)
            self.orders.orders[str(order.id)] = order

    def save_orders(self):
        """保存 orders"""
        self.server.save_config_simple(
            self.orders,
            constants.ORDERS_DATA_FILE_NAME,
            in_data_folder=True,
        )

    def reload_orders(self):
        """重新加载 orders"""
        self.orders = self.server.load_config_simple(
            constants.ORDERS_DATA_FILE_NAME,
            target_class=OrderData,
        )
        self.__check_orders()

    def is_storage_full(self, player: str):
        """检查玩家发送的订单是否已达上限"""
        if self.config.max_storage_num == -1:
            return False
        return len(self.orders.get_orderid_by_sender(player)) >= self.config.max_storage_num

    def is_player_sendable(self, player: str):
        """检查这个玩家是否可以被发送（即登陆过服务器）"""
        return player in self.orders.players

    def post_item(self, src: InfoCommandSource, receiver: str, comment: str | None = None) -> None:
        """邮寄物品

        Args:
            src (InfoCommandSource): 命令源
            receiver (str): 接收者
            comment (str | None, optional): 备注. Defaults to None.
        """
        server = self.server
        sender = src.get_info().player
        item_json = get_offhand_item(server, sender)

        if comment is None:
            comment = tr('no_comment')

        if self.is_storage_full(sender):
            src.reply(tr('at_max_storage', self.config.max_storage_num))
            return
        if not self.is_player_sendable(receiver):
            src.reply(tr('no_receiver', receiver))
            return
        if sender == receiver:
            src.reply(tr('same_person'))
            return
        if not item_json:
            src.reply(tr('check_offhand'))
            return

        item_tag = item_json.get('tag', '')
        item = str(item_json.get('id')) + (
            json.dumps(item_tag, ensure_ascii=False) if len(item_tag) > 0 else ''
        ) + ' ' + str(item_json.get('Count', ''))

        # 添加订单
        order_id = self.orders.add_order(Order(
            sender=sender,
            receiver=receiver,
            item=item,
            comment=comment,
            time=formatted_time()
        ))

        replace_offhand(server, sender, 'minecraft:air', self.is_allow_item)
        src.reply(tr('reply_success_post'))
        server.tell(receiver, tr('hint_receive', f"{order_id}"))
        play_sound.successfully_post(server, sender, receiver)
        self.save_orders()

    def receive_item(self, src: InfoCommandSource, order_id: int) -> None:
        """接受物品

        Args:
            src (InfoCommandSource): 信息命令源
            order_id (int): 订单 id
        """
        player = src.get_info().player

        # 副手有东西 拒绝接收
        if get_offhand_item(self.server, player):
            src.reply(tr('clear_offhand'))
            return

        if str(order_id) not in self.orders.orders:
            src.reply(tr('uncheck_orderid'))
            return

        order = self.orders.orders[f"{order_id}"]
        replace_offhand(self.server, player, order.item, self.is_allow_item)
        play_sound.receive(self.server, player)
        self.orders.remove_order(order_id)

    def get_post_list(self, src: InfoCommandSource) -> list:
        sender = src.get_info().player
        return self.orders.get_orderid_by_sender(sender)

    def get_receive_list(self, src: InfoCommandSource) -> list:
        receiver = src.get_info().player
        return self.orders.get_orderid_by_receiver(receiver)

    def get_players(self) -> list[str]:
        return self.orders.players

    def get_all_orders(self) -> list[IdGivenOrder]:
        return [o for o in self.orders.orders.values()]

    def add_player(self, src: InfoCommandSource, player: str) -> None:
        if self.is_player_sendable(player):
            src.reply(tr('has_player'))
            return

        self.orders.add_player(player)
        src.reply(tr('login_success', player))
        self.logger.info(tr('login_log', player))
        self.save_orders()

    def remove_player(self, src: InfoCommandSource, player: str) -> None:
        if not self.is_player_sendable(player):
            src.reply(tr('cannot_del_player'))
            return
        self.orders.remove_player(player)
        src.reply(tr('del_player_success', player))
        self.logger.info(tr('del_player_log', player))
        self.save_orders()
