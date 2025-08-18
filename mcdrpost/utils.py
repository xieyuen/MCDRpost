# -*- coding: utf-8 -*-
import time

from mcdreforged.api.types import PluginServerInterface


def formatted_time() -> str:
    """获取当前时间的格式化的字符串"""
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())


def get_offhand_item(server: PluginServerInterface, player: str) -> dict | None:
    """获取玩家副手物品

    Args:
        server (PluginServerInterface): MCDR插件接口
        player (str): 玩家名

    Returns:
        dict | None: 物品信息，若获取失败返回 None
    """
    mc_data_api = server.get_plugin_instance('minecraft_data_api')

    try:
        if server.is_rcon_running():
            offhand_item_str = server.rcon_query(f'data get entity {player} Inventory[{{Slot:-106b}}]')
            offhand_item = mc_data_api.convert_minecraft_json(offhand_item_str)
        else:
            server.logger.info("Please config rcon of server correctly.")
            offhand_item = mc_data_api.get_player_info(player, 'Inventory[{Slot:-106b}]')

        if type(offhand_item) == dict:
            return offhand_item
        else:
            return None
    except Exception as e:
        server.logger.info("Error occurred during getOffhandItem" + e.__class__.__name__)
        return None


def replace_offhand(server: PluginServerInterface, player: str, item: str, command_item=-1):
    """替换副手物品

    Args:
        server (PluginServerInterface): MCDR插件接口
        player (str): 玩家名
        item (str): 要替换的物品名
        command_item (int): 是否可用item命令， -1为不可知，0为不可用（需要用replaceitem），1为可用
    """
    if command_item == 1:
        server.execute(f'item replace entity {player} weapon.offhand with {item}')
    elif command_item == 0:
        server.execute(f'replaceitem entity {player} weapon.offhand {item}')
    elif command_item == -1:
        server.execute(f'item replace entity {player} weapon.offhand with {item}')
        server.execute(f'replaceitem entity {player} weapon.offhand {item}')
    else:
        assert False, f"异常的状态: {command_item=}"


def can_command_item(server: PluginServerInterface) -> int:
    """判断是否可用item命令

    -1 为不可知（未开启 rcon ），0 为不可用（需要用 replaceitem ），1 为可用

    利用 rcon 发送 ``help item replace``，若可用 item 命令则会返回相应帮助信息(信息内包含item replace)
    """
    try:
        if server.is_rcon_running():
            help_msg = server.rcon_query('help item replace')
            if 'item replace' in help_msg:
                return 1
            else:
                return 0
        else:
            return -1
    except Exception as e:
        server.logger.warning(e)
        return -1


def tr(tag: str, *args):
    """translation"""
    _str = PluginServerInterface.get_instance().tr(f'mcdrpost.{tag}', *args)
    return _str
