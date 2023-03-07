from nonebot.matcher import matchers
from nonebot.adapters.onebot.v11 import Bot
from nonebot.adapters.onebot.v11.event import MessageEvent

from ..utils import on_command, to_me
from ..version import __version__
from .. import config

help = on_command("帮助", rule=to_me(), priority=5, block=True) # 数值越小优先级越高


@help.handle()
async def _(event: MessageEvent, bot:Bot):
    bot_id = int(bot.self_id)
    if bot_id in config.bot_names:
        message = f"{config.bot_names[bot_id]}目前支持的功能：\n（请将UID替换为需要操作的B站UID）\n"
    else:
        message = "LialaBot目前支持的功能：\n（请将UID替换为需要操作的B站UID）\n"
    for matchers_list in matchers.values():
        for matcher in matchers_list:
            if (
                matcher.plugin_name
                and matcher.plugin_name.startswith("haruka_bot")
                and matcher.__doc__
            ):
                message += matcher.__doc__ + "\n"
    message += f"\n当前版本：v{__version__}\n" "https://github.com/Misaka-Mikoto-Tech"
    await help.finish(message)
