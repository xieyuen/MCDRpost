import time

from mcdreforged.api.types import Info, InfoCommandSource, PluginServerInterface

from mcdrpost import constants
from mcdrpost.manager.command_manager import CommandManager
from mcdrpost.manager.config_manager import ConfigurationManager
from mcdrpost.manager.order_manager import OrderManager
from mcdrpost.order_data import OrderInfo
from mcdrpost.utils import get_formatted_item, get_formatted_time, get_offhand_item, play_sound, tr
from mcdrpost.utils.replace_offhand_item import replace_for_17, replace_for_lower_17
from mcdrpost.utils.translation_tags import Tags


class PostManager:
    """Post 管理器，也是插件核心逻辑处理的地方

    Attributes:
        server (PluginServerInterface): MCDR插件接口
        config_manager (ConfigurationManager): 配置管理器
        order_manger (OrderManager): 订单管理器
    """

    def __init__(self, server: PluginServerInterface) -> None:
        self.server = server
        self.config_manager = ConfigurationManager(self)
        self.order_manger = OrderManager(self)
        self.command_manager = CommandManager(self)

        if self.config_manager.environment.item_command:
            self._replace = replace_for_17
        else:
            self._replace = replace_for_lower_17

    def replace(self, player: str, item: str) -> None:
        """替换副手物品

        Args:
            player (str): 玩家名
            item (str): 要替换的物品 id
        """
        self._replace(self.server, player, item)

    def on_load(self, _server: PluginServerInterface, _prev_module):
        self.command_manager.register()

    def on_unload(self, _server: PluginServerInterface):
        self.config_manager.save()
        self.order_manger.save()

    def on_player_joined(self, server: PluginServerInterface, player: str, info: Info) -> None:
        if not self.order_manger.is_player_registered(player):
            # 还未注册的玩家
            self.order_manger.add_player(player)
            server.logger.info(tr(Tags.login_log, player))
            self.order_manger.save()
            return

            # 已注册的玩家
        if self.order_manger.has_unreceived_order(player):
            time.sleep(self.config_manager.configuration.receive_tip_delay)
            server.tell(player, tr(Tags.wait_for_receive))
            play_sound.has_something_to_receive(server, player)

    def on_server_stop(self, _server: PluginServerInterface, _server_return_code: int):
        self.save()

    def is_storage_full(self, player: str) -> bool:
        return len(self.order_manger.get_orders_by_sender(player)) >= self.config_manager.configuration.max_storage_num

    def post(self, src: InfoCommandSource, receiver: str, comment: str = None) -> None:
        sender = src.get_info().player

        if self.is_storage_full(sender):
            src.reply(tr(Tags.at_max_storage, self.config_manager.configuration.max_storage_num))
            return

        if sender == receiver:
            src.reply(tr(Tags.same_person))
            return

        if comment is None:
            comment = tr(Tags.no_comment)

        item = get_formatted_item(
            get_offhand_item(self.server, sender)
        )

        # create order
        order_id = self.order_manger.add_order(OrderInfo(
            sender=sender,
            receiver=receiver,
            item=item,
            comment=comment,
            time=get_formatted_time(),
        ))

        self.replace(sender, constants.AIR)
        src.reply(tr(Tags.reply_success_post))
        self.server.tell(receiver, tr(Tags.hint_receive, order_id))
        play_sound.successfully_post(self.server, sender, receiver)
        self.order_manger.save()

    def receive(self, src: InfoCommandSource, order_id: int):
        player = src.get_info().player

        # 副手有东西 拒绝接收
        if get_offhand_item(self.server, player):
            src.reply(tr(Tags.clear_offhand))
            return

        if order_id not in self.order_manger.get_orders_by_receiver(player):
            src.reply(tr(Tags.unchecked_orderid))
            return

        order = self.order_manger.pop_order(order_id)
        self.replace(player, order.item)
        play_sound.receive(self.server, player)

    def save(self):
        self.config_manager.save()
        self.order_manger.save()

    def reload(self):
        self.config_manager.load()
        self.order_manger.load()
