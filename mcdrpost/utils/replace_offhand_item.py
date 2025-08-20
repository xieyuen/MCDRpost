"""替换副手物品

Args:
    server (PluginServerInterface): MCDR插件接口
    player (str): 玩家名
    item (str): 要替换的物品 id
"""
from typing import TYPE_CHECKING

from mcdreforged.api.types import PluginServerInterface

if TYPE_CHECKING:
    from mcdrpost.config.environment import Environment  # noqa


def replace_for_17(server: PluginServerInterface, player: str, item: str):
    server.execute(f'item replace entity {player} weapon.offhand with {item}')


def replace_for_lower_17(server: PluginServerInterface, player: str, item: str):
    server.execute(f'replaceitem entity {player} weapon.offhand {item}')
