from typing import List, Union

from nonebot.params import CommandArg, Matcher, Event
from nonebot.adapters.onebot.v11 import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.permission import SUPERUSER
from nonebot_plugin_guild_patch import GuildMessageEvent
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, PrivateMessageEvent, GroupMessageEvent, MessageSegment, GroupIncreaseNoticeEvent

from .config import *

async def _identity_mofify_check(matcher:Matcher, event: MessageEvent, bot:Bot, cmd:str, type:str = 'cmd') -> bool:
    """默认权限检查函数"""
    if cmd is None:
        return True
    
    if event.sender.user_id == int(bot.self_id):
        return True

    args:List[str] = cmd.split(' ')
    if(len(args) == 0):
        return True
    elif(len(args) >= 1):
        if args[0] in ['admin', '设定','set', '更新','update','edit','添加','new', '删除','del','delete',
                       '锁定','lock','解锁','unlock','开启','on', '关闭','off','重置','reset','debug','会话','chats',
                       '记忆','memory']:
            return str(event.user_id) in config['ADMIN_USERID']
        return True
    else:
        return True
    
gpt_has_permission = _identity_mofify_check # 权限检查函数，自定义时允许被外部覆盖