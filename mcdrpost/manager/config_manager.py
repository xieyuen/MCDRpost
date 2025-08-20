from typing import TYPE_CHECKING

from mcdrpost import constants
from mcdrpost.config.configuration import Configuration
from mcdrpost.config.environment import Environment

if TYPE_CHECKING:
    from mcdrpost.manager.post_manager import PostManager  # noqa


class ConfigurationManager:
    """一个能够自动解析环境配置的配置管理器

    Attributes:
        environment (Environment): 环境配置，主要是 MC 版本
        configuration (Configuration): 插件配置
    """

    def __init__(self, post_manager: "PostManager") -> None:
        self._post_manager = post_manager
        self._server = post_manager.server
        self.environment = Environment(self._server)
        self.configuration: Configuration | None = None
        self.load()

    def load(self) -> None:
        self.configuration = self._server.load_config_simple(
            constants.CONFIG_FILE_NAME,
            target_class=Configuration,
            file_format=constants.CONFIG_FILE_TYPE,
        )

    def save(self) -> None:
        self._post_manager.server.save_config_simple(
            self.configuration,
            constants.CONFIG_FILE_NAME,
            file_format=constants.CONFIG_FILE_TYPE
        )
