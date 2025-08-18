from mcdreforged.api.types import CommandSource
from mcdreforged.api.command import Literal, Text, GreedyText, RequirementNotMet, Integer
from mcdreforged.api.rtext import RText, RTextList, RColor, RAction
from mcdreforged.command.command_source import InfoCommandSource

from mcdrpost.utils import tr
from mcdrpost.post_manager import PostManager


def required_errmsg(src: CommandSource, id: int):
    if id == 1:
        src.reply(tr('only_for_player'))
    elif id == 2:
        src.reply(tr('no_permission'))


class CommandTree:
    """指令树

    Attributes:
        manager (PostManager): PostManager 实例
        config (Configuration): 插件配置信息
        prefix (str): 命令前缀
    """

    def __init__(self, manager: PostManager):
        self.manager = manager
        self.config = manager.config
        self.prefix = manager.config.command_prefix
        if isinstance(self.prefix, str):
            self.prefix = [self.prefix]

    def register(self):
        """注册命令树"""
        for prefix in self.prefix:
            self.manager.server.register_help_message(prefix, {
                "en_us": "post/teleport weapon hands items",
                "zh_cn": "传送/收寄副手物品",
            })
            self.manager.server.register_command(
                self.get_trees(prefix)
            )

    @staticmethod
    def print_help_message(source: CommandSource, prefix: str):
        msgs_on_helper = RText('')
        msgs_on_admin = RText('')
        if source.has_permission_higher_than(1):
            # helper以上权限的添加信息
            msgs_on_helper = RTextList(
                RText(prefix + ' ls orders', RColor.gray)
                .c(RAction.suggest_command, "!!po ls orders")
                .h(tr('hover')),
                RText(f'{tr("help.hint_ls_orders")}\n')
            )
        if source.has_permission_higher_than(2):
            # admin以上权限的添加信息
            msgs_on_admin = RTextList(
                RText(prefix + tr('help.player_add'), RColor.gray)
                .c(RAction.suggest_command, "!!po player add ")
                .h(tr('hover')), RText(f'{tr("help.hint_player_add")}\n'),
                RText(prefix + tr('help.player_remove'), RColor.gray)
                .c(RAction.suggest_command, "!!po player remove ")
                .h(tr('hover')), RText(f'{tr("help.hint_player_remove")}\n'),
            )

        source.reply(
            RTextList(
                RText('--------- §3MCDRpost §r---------\n'),
                RText(f'{tr("desc")}\n'),
                RText(f'{tr("help.title")}\n'),
                RText(prefix, RColor.gray).c(RAction.suggest_command, "!!po").h(tr('hover')),
                RText(f' | {tr("help.hint_help")}\n'),
                RText(prefix + tr('help.p'), RColor.gray).c(RAction.suggest_command, "!!po p ").h(
                    tr('hover')),
                RText(f'{tr("help.hint_p")}\n'),
                RText(prefix + ' rl', RColor.gray).c(RAction.suggest_command, "!!po rl").h(tr('hover')),
                RText(f'{tr("help.hint_rl")}\n'),
                RText(prefix + tr('help.r'), RColor.gray).c(RAction.suggest_command, "!!po r ").h(
                    tr('hover')),
                RText(f'{tr("help.hint_r")}\n'),
                RText(prefix + ' pl', RColor.gray).c(RAction.suggest_command, "!!po pl").h(tr('hover')),
                RText(f'{tr("help.hint_pl")}\n'),
                RText(prefix + tr('help.c'), RColor.gray).c(RAction.suggest_command, "!!po c ").h(
                    tr('hover')),
                RText(f'{tr("help.hint_c")}\n'),
                RText(prefix + ' ls players', RColor.gray).c(RAction.suggest_command,
                                                             "!!po ls players").h(
                    tr('hover')),
                RText(f'{tr("help.hint_ls_players")}\n'),
                msgs_on_helper,
                msgs_on_admin,
                RText('-----------------------')
            )
        )

    def output_post_list(self, src: InfoCommandSource):
        post_list = self.manager.get_post_list(src)

        msg = ""

        for order in post_list:
            msg += f"{order.id}  | {order.receiver}  | {order.time}  | {order.info}\n"

        if msg == '':
            src.reply(tr('no_post_orders'))
            return

        src.reply(
            '===========================================\n'
            '{0}\n'
            '{1}'
            '-------------------------------------------\n'
            '{2}'
            '===========================================\n'
            .format(tr('list_post_orders_title'), msg, tr('hint_cancel'))
        )

    def output_receive_list(self, src: InfoCommandSource):
        receive_list = self.manager.get_receive_list(src)

        msg = ""

        for order in receive_list:
            msg += f"{order.id}  | {order.sender}  | {order.time}  | {order.info}\n"

        if msg == '':
            src.reply(tr('no_receive_orders'))
            return

        src.reply(
            '===========================================\n'
            '{0}\n'
            '{1}\n'
            '-------------------------------------------\n'
            '{2}'
            '===========================================\n'
            .format(tr('list_receive_orders_title'), msg, tr('hint_order_receive'))
        )

    def output_all_orders(self, src: InfoCommandSource):
        all_orders = self.manager.get_all_orders()

        msg = ""

        for order in all_orders:
            msg += f"{order.id}  | {order.sender}  | {order.receiver}  | {order.time}  | {order.comment}\n"

        if not msg:
            src.reply(tr('no_orders'))
            return

        src.reply(
            '===========================================\n'
            '{0}\n'
            '{1}\n'
            '===========================================\n'
            .format(tr('list_orders_title'), msg)
        )

    def get_trees(self, prefix: str):
        """生成指令树"""
        return (
            Literal(prefix).
            runs(lambda src: self.print_help_message(src, prefix)).
            then(
                Literal('p').
                requires(lambda src: src.is_player).
                on_error(RequirementNotMet, lambda src: required_errmsg(src, 1), handled=True).
                runs(lambda src: src.reply(tr('no_input_receiver'))).
                then(
                    Text('receiver').
                    suggests(self.manager.get_players).
                    runs(lambda src, ctx: self.manager.post_item(src, ctx['receiver'])).
                    then(
                        GreedyText('comment').
                        runs(lambda src, ctx: self.manager.post_item(src, ctx['receiver'], ctx['comment']))
                    )
                )
            ).
            then(
                Literal('post').
                requires(lambda src: src.is_player).
                on_error(RequirementNotMet, lambda src: required_errmsg(src, 1), handled=True).
                runs(lambda src: src.reply(tr('no_input_receiver'))).
                then(
                    Text('receiver').
                    suggests(self.manager.get_players).
                    runs(lambda src, ctx: self.manager.post_item(src, ctx['receiver'])).
                    then(
                        GreedyText('comment').
                        runs(lambda src, ctx: self.manager.post_item(src, ctx['receiver'], ctx['comment']))
                    )
                )
            ).
            then(
                Literal('pl').
                requires(lambda src: src.is_player).
                on_error(RequirementNotMet, lambda src: required_errmsg(src, 1), handled=True).
                runs(self.output_post_list)
            ).
            then(
                Literal('post_list').
                requires(lambda src: src.is_player).
                on_error(RequirementNotMet, lambda src: required_errmsg(src, 1), handled=True).
                runs(self.output_post_list)
            ).
            then(
                Literal('r').
                requires(lambda src: src.is_player).
                on_error(RequirementNotMet, lambda src: required_errmsg(src, 1), handled=True).
                runs(lambda src: src.reply(tr('no_input_receive_orderid'))).
                then(
                    Integer('orderid').
                    suggests(lambda src: self.manager.orders.get_orderid_by_receiver(src.get_info().player)).
                    runs(
                        lambda src, ctx: (
                            self.manager.receive_item(src, ctx['orderid']),
                            src.reply(tr('receive_success', ctx['orderid']))
                        )
                    )
                )
            ).
            then(
                Literal('receive').
                requires(lambda src: src.is_player).
                on_error(RequirementNotMet, lambda src: required_errmsg(src, 1), handled=True).
                runs(lambda src: src.reply(tr('no_input_receive_orderid'))).
                then(
                    Integer('orderid').
                    suggests(lambda src: self.manager.orders.get_orderid_by_receiver(src.get_info().player)).
                    runs(
                        lambda src, ctx: (
                            self.manager.receive_item(src, ctx['orderid']),
                            src.reply(tr('receive_success', ctx['orderid']))
                        )
                    )
                )
            ).
            then(
                Literal('rl').
                requires(lambda src: src.is_player).
                on_error(RequirementNotMet, lambda src: required_errmsg(src, 1), handled=True).
                runs(self.output_receive_list)
            ).
            then(
                Literal('receive_list').
                requires(lambda src: src.is_player).
                on_error(RequirementNotMet, lambda src: required_errmsg(src, 1), handled=True).
                runs(self.output_receive_list)
            ).
            then(
                Literal('c').
                requires(lambda src: src.is_player).
                on_error(RequirementNotMet, lambda src: required_errmsg(src, 1), handled=True).
                runs(lambda src: src.reply(tr('no_input_cancel_orderid'))).
                then(
                    Integer('orderid').
                    suggests(lambda src: self.manager.orders.get_orderid_by_sender(src.get_info().player)).
                    runs(
                        lambda src, ctx: (
                            self.manager.receive_item(src, ctx['orderid']),
                            src.reply(tr('cancel_success', ctx['orderid']))
                        )
                    )
                )
            ).
            then(
                Literal('cancel').
                requires(lambda src: src.is_player).
                on_error(RequirementNotMet, lambda src: required_errmsg(src, 1), handled=True).
                runs(lambda src: src.reply(tr('no_input_cancel_orderid'))).
                then(
                    Integer('orderid').
                    suggests(lambda src: self.manager.orders.get_orderid_by_sender(src.get_info().player)).
                    runs(
                        lambda src, ctx: (
                            self.manager.receive_item(src, ctx['orderid']),
                            src.reply(tr('cancel_success', ctx['orderid']))
                        )
                    )
                )
            ).
            then(
                Literal('ls').
                requires(lambda src: src.has_permission_higher_than(0)).
                on_error(RequirementNotMet, lambda src: required_errmsg(src, 2), handled=True).
                runs(lambda src: src.reply(tr('command_incomplete'))).
                then(
                    Literal('players').
                    runs(lambda src: src.reply(
                        tr('list_player_title') + str(self.manager.get_players())
                    ))
                ).
                then(
                    Literal('orders').
                    requires(lambda src: src.has_permission_higher_than(1)).
                    on_error(RequirementNotMet, lambda src: required_errmsg(src, 2), handled=True).
                    runs(self.output_all_orders)
                ).
                then(
                    Literal('receive').
                    requires(lambda src: src.is_player).
                    on_error(RequirementNotMet, lambda src: required_errmsg(src, 1), handled=True).
                    runs(self.output_receive_list)
                ).then(
                    Literal('post').
                    requires(lambda src: src.is_player).
                    on_error(RequirementNotMet, lambda src: required_errmsg(src, 1), handled=True).
                    runs(self.output_post_list)
                )
            ).
            then(
                Literal('list').
                requires(lambda src: src.has_permission_higher_than(0)).
                on_error(RequirementNotMet, lambda src: required_errmsg(src, 2), handled=True).
                runs(lambda src: src.reply(tr('command_incomplete'))).
                then(
                    Literal('players').
                    runs(lambda src: src.reply(
                        tr('list_player_title') + str(self.manager.get_players())
                    ))
                ).
                then(
                    Literal('orders').
                    requires(lambda src: src.has_permission_higher_than(1)).
                    on_error(RequirementNotMet, lambda src: required_errmsg(src, 2), handled=True).
                    runs(self.output_all_orders)
                ).
                then(
                    Literal('receive').
                    requires(lambda src: src.is_player).
                    on_error(RequirementNotMet, lambda src: required_errmsg(src, 1), handled=True).
                    runs(self.output_receive_list)
                ).then(
                    Literal('post').
                    requires(lambda src: src.is_player).
                    on_error(RequirementNotMet, lambda src: required_errmsg(src, 1), handled=True).
                    runs(self.output_post_list)
                )
            ).
            then(
                Literal('player').
                requires(lambda src: src.has_permission_higher_than(2)).
                on_error(RequirementNotMet, lambda src: required_errmsg(src, 2), handled=True).
                runs(lambda src: src.reply(tr('command_incomplete'))).
                then(
                    Literal('add').
                    runs(lambda src: src.reply(tr('command_incomplete'))).
                    then(
                        Text('player_id').
                        runs(lambda src, ctx: self.manager.add_player(src, ctx['player_id']))
                    )
                ).
                then(
                    Literal('remove').
                    runs(lambda src: src.reply(tr('command_incomplete'))).
                    then(
                        Text('player_id').
                        suggests(self.manager.get_players).
                        runs(lambda src, ctx: self.manager.remove_player(src, ctx['player_id']))
                    )
                )
            )
        )
