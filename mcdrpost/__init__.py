# -*- coding: utf-8 -*-
import time

from mcdreforged.api.types import PluginServerInterface

from mcdrpost import play_sound
from mcdrpost.command import CommandTree
from mcdrpost.post_manager import PostManager
from mcdrpost.utils import tr

manager: PostManager


def on_load(server: PluginServerInterface, _old):
    global manager
    manager = PostManager(server)
    CommandTree(manager).register()


def on_unload(_server: PluginServerInterface):
    manager.save_orders()


def on_server_start(_server: PluginServerInterface):
    manager.reload_orders()


def on_server_stop(_server: PluginServerInterface, _server_return_code: int):
    manager.save_orders()


def on_player_joined(server, player, _info):
    if not manager.orders.is_player_sendable(player):
        manager.orders.add_player(player)
        server.logger.info(tr('login_log', player))
        manager.save_orders()
        return

    if manager.orders.get_orderid_by_receiver(player):  # 有未接收的邮件
        time.sleep(manager.config.receive_tip_delay)  # 延迟一定时长后再提示，防止更多进服消息混杂而看不到提示
        server.tell(player, tr('wait_for_receive'))
        play_sound.has_something_to_receive(server, player)
