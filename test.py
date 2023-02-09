import asyncio
from bilireq.live import get_rooms_info_by_uids
from nonebot.adapters.onebot.v11.message import MessageSegment
from nonebot.log import logger

#import haruka_bot.config
#from haruka_bot.database import DB as db
#from utils import PROXIES, safe_send, scheduler
    

async def test_main():
    res = await get_rooms_info_by_uids([2075874], reqtype="web")
    # res = await get_rooms_info_by_uids([2051617240], reqtype="web")
    print(res)

if __name__ == "__main__":
    asyncio.run(test_main())