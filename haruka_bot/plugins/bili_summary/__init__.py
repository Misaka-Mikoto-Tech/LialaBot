from typing import Optional, Tuple

from nonebot_plugin_guild_patch import GuildMessageEvent
from nonebot_modify.adapters.onebot.v11.event import GroupMessageEvent, MessageEvent
from nonebot.adapters.onebot.v11 import Bot

async def bili_summary_check_is_enable(event: MessageEvent, bot:Bot) -> Tuple[bool, Optional[str]]:
    """是否启用B站视频解析功能"""
    from ...database import DB as db

    bot_id = int(bot.self_id)
    enable_bili_summary:bool = True
    if isinstance(event, GroupMessageEvent):
        grp_event:GroupMessageEvent = event
        enable_bili_summary = await db.get_group_bili_summary(group_id=grp_event.group_id,bot_id=bot_id)
    elif isinstance(event, GuildMessageEvent):
        gld_event:GuildMessageEvent = event
        enable_bili_summary = await db.get_guild_bili_summary(guild_id=gld_event.guild_id,channel_id=gld_event.channel_id,bot_id=bot_id)

    if not enable_bili_summary:
        return (False, '本群没有开启B站视频解析功能，查询开启指令请输入 帮助')
    else:
        return (True, None)
    
try:
    import nonebot_plugin_bilichat
    nonebot_plugin_bilichat.check_is_enable = bili_summary_check_is_enable
except:
    pass