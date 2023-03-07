from typing import List, Union
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Bot
from nonebot.adapters.onebot.v11.event import MessageEvent, GroupMessageEvent, PrivateMessageEvent
from nonebot_plugin_guild_patch import GuildMessageEvent
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.permission import SUPERUSER, Permission
import nonebot_plugin_naturel_gpt

from ...utils import GUILD_ADMIN
from ...database import DB

async def permission_check_chatgpt(matcher:Matcher, event: MessageEvent, bot:Bot, cmd:str, type:str = 'cmd') -> bool:
    """chatgpt相关的操作权限检查"""

    bot_id = int(bot.self_id)
    enable_chatgpt:bool = False
    if isinstance(event, GroupMessageEvent):
        grp_event:GroupMessageEvent = event
        enable_chatgpt = await DB.get_group_chatgpt(group_id=grp_event.group_id,bot_id=bot.self_id)
    elif isinstance(event, GuildMessageEvent):
        gld_event:GuildMessageEvent = event
        enable_chatgpt = await DB.get_guild_chatgpt(guild_id=gld_event.guild_id,channel_id=gld_event.channel_id,bot_id=bot.self_id)

    if not enable_chatgpt:
        return False

    if not cmd: # None or ''
        return True
    
    if event.sender.user_id == int(bot.self_id):
        return True

    args:List[str] = cmd.split(' ')

    from haruka_bot import config
    def check_exclusive_bot() -> bool:
        return not ((bot_id in config.exclusive_bots) and (event.sender.user_id != bot_id))

    if event.sender.user_id == bot_id:
        # Bot 控制自己时永远有权限
        return
    from ...database import DB as db

    has_permission:bool = False
    if isinstance(event, PrivateMessageEvent):
        has_permission = False
    if isinstance(event, GroupMessageEvent):
        if not check_exclusive_bot():
            has_permission = False
        elif (await db.get_group_admin(event.group_id, bot.self_id)) or (await (GROUP_ADMIN | GROUP_OWNER | SUPERUSER)(bot, event)):
            has_permission = True
    elif isinstance(event, GuildMessageEvent):
        if not check_exclusive_bot():
            has_permission =  False
        elif (await db.get_guild_admin(event.guild_id, event.channel_id, bot.self_id)) or (await (GUILD_ADMIN | SUPERUSER)(bot, event)):
            has_permission = True
    else:
        has_permission = False

    if not has_permission:
        return False
    
    if args[0] in ['admin', '设定','set', '更新','update','edit','添加','new', '删除','del','delete',
                    '锁定','lock','解锁','unlock','开启','on', '关闭','off','重置','reset','debug','会话','chats',
                    '记忆','memory']:
        return await (SUPERUSER)(bot, event) # chgpt 设定必须是bot自身或者超级管理员
    
    return True

nonebot_plugin_naturel_gpt.utils.gpt_has_permission = permission_check_chatgpt