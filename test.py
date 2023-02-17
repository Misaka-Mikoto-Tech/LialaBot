import asyncio
from bilireq.live import get_rooms_info_by_uids
# from nonebot.adapters.onebot.v11.message import MessageSegment
from nonebot.log import logger

#import haruka_bot.config
#from haruka_bot.database import DB as db
#from utils import PROXIES, safe_send, scheduler
    
from dataclasses import dataclass, astuple
import time
from typing import Dict

@dataclass
class LiveStatusData:
    """直播间状态数据"""
    status_code:int
    online_time:float = 0
    offline_time:float = 0

all_status:Dict[int,LiveStatusData] = {} # [uid, LiveStatus]

async def get_live_info():
    # res = await get_rooms_info_by_uids([2075874], reqtype="web")
    res = await get_rooms_info_by_uids([1616391510], reqtype="web")

    # res = await get_rooms_info_by_uids([2051617240], reqtype="web")
    print(res)

def format_time_span(seconds:float)->str:
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{int(h)}小时{int(m)}分"

if __name__ == "__main__":
    span = format_time_span(12505.123)
    print(span)


    # asyncio.run(get_live_info())




# Matcher 的参数列表
# await handler(
#     matcher=self,
#     bot=bot,
#     event=event,
#     state=self.state,
#     stack=stack,
#     dependency_cache=dependency_cache,
# )