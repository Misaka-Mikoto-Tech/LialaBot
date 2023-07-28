import asyncio
from bilireq.live import get_rooms_info_by_uids
# from nonebot.adapters.onebot.v11.message import MessageSegment
from nonebot.log import logger

#import haruka_bot.config
#from haruka_bot.database import DB as db
#from utils import PROXIES, safe_send, scheduler
    
from dataclasses import dataclass, astuple
import time
from typing import Any, Dict, Mapping, Union

import collections
import time

T_Auth = Union[Mapping[str, Any], "Auth", None]



class Auth(collections.UserDict):
    def __init__(self, auth: T_Auth = None):
        super().__init__()
        self.update({"token": {"tokens": {}}, "cookie": {"cookies": {}}})
        if auth:
            self.update(auth)
        # self.update(kwargs)

    @property
    def uid(self):
        return self["uid"]
    

auth = Auth()
print(auth.uid)