from mcdreforged.api.utils import Serializable


class Configuration(Serializable):
    """插件配置

    Attributes:
        max_storage_num (int): 每个人发送的订单的最大存储量，-1不限制
        command_prefix (str | list[str]): MCDR 命令前缀，可以注册多个作为别名，只需要放在一个列表内即可，
                                                单个前缀可以直接用字符串带起
        save_delay (int): 保存订单文件的间隔时间，单位为秒
        auto_fix (bool): 是否自动修复无效订单
        receive_tip_delay (int | float): 登录之后收件箱提示的延迟时间，单位为秒
    """
    max_storage_num: int = 5
    command_prefix: str | list[str] = ['!!po', "!!post"]
    save_delay: int = 1
    auto_fix: bool = False
    receive_tip_delay: int | float = 3
