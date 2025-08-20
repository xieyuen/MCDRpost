from mcdreforged.api.utils import Serializable


class Configuration(Serializable):
    """插件配置

    Attributes:
        max_storage_num (int): 每个人发送的订单的最大存储量，-1不限制
        allow_alias (bool): 是否允许命令别名，如果为 False,则只会注册 !!po
        command_prefixes (list[str]): MCDR 命令前缀，可以注册多个作为别名，只需要放在一个列表内即可, !!po 一定会生效
        auto_fix (bool): 是否自动修复无效订单
        receive_tip_delay (int | float): 登录之后收件箱提示的延迟时间，单位为秒
    """
    max_storage_num: int = 5
    allow_alias: bool = True
    command_prefixes: list[str] = ['!!po', "!!post"]
    auto_fix: bool = False
    receive_tip_delay: float = 3
