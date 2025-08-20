from mcdreforged.api.types import PluginServerInterface


class Environment:
    def __init__(self, server: PluginServerInterface) -> None:
        self.server = server

    @property
    def server_version(self) -> str:
        return self.server.get_server_information().version

    @property
    def item_command(self) -> bool:
        """``item`` 命令是否可用

        在 Minecraft 1.17 之后，``replaceitem`` 命令被 ``item replace``代替
        这会影响到插件替换手中物品时执行的 Minecraft 命令
        """
        return self.server_version >= "1.17"
