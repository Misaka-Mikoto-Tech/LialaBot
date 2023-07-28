import json
from typing import List
from pathlib import Path
from nonebot import logger
from nonebot.matcher import matchers
from nonebot.adapters.onebot.v11 import Bot, MessageSegment
from nonebot.adapters.onebot.v11.event import MessageEvent

from ..utils import on_command, to_me, text_to_img
from ..version import __version__
from .. import config
from ..utils import (
    PROXIES,
    get_type_id,
    handle_uid,
    on_command,
    permission_check,
    to_me,
    uid_check,
)

from . import Bili_Auth, bili_is_logined
from ..utils import get_dynamic_screenshot, safe_send, scheduler
from bilireq.login import Login
from bilireq.exceptions import ResponseCodeError

bili_login = on_command("bili_login", aliases={"B站登录"}, rule=to_me(), priority=5, block=True) # 数值越小优先级越高
bili_login.handle()(permission_check)

@bili_login.handle()
async def _(event: MessageEvent, bot:Bot):
    global bili_is_logined

    auth_data = None
    bilibili_login = Login()
    try:
        qr_url = await bilibili_login.get_qrcode_url()
        data = await bilibili_login.get_qrcode(qr_url)
        if isinstance(data, bytes):
            await bili_login.send(MessageSegment.image(data))
        auth_data = await bilibili_login.qrcode_login(interval=5)
        logger.success("[BiliBili推送] 二维码登录完成")
        await bili_login.send("[BiliBili推送] 二维码登录完成")
    except ResponseCodeError as e:
        bili_is_logined = False
        err_msg = f"[BiliBili推送] 二维码登录失败：{e.code}，{e.msg}"
        logger.error(err_msg)
        await bili_login.finish(err_msg)

    if auth_data:
        Bili_Auth.update(auth_data)
        bili_is_logined = True
        logger.debug(await Bili_Auth.get_info())

        login_cache_file = Path(config.haruka_login_cache_file)
        login_cache_file.write_text(
            json.dumps(dict(Bili_Auth), indent=2, ensure_ascii=False)
        )
        logger.info("[Bilibili推送] 登录完成")


async def _load_login_cache():
    """Bot启动时尝试自动登录"""

    logger.info("尝试自动登录B站")
    login_cache_file = Path(config.haruka_login_cache_file)
    if login_cache_file.exists():
        Bili_Auth.update(json.loads(login_cache_file.read_text()))
        try:
            auth_data = await Bili_Auth.refresh()
            login_cache_file.write_text(
                json.dumps(dict(Bili_Auth), indent=2, ensure_ascii=False)
            )
            
            logger.debug(auth_data)
            logger.success("[Bilibili推送] 缓存登录完成")
        except ResponseCodeError as e:
            logger.error(f"[Bilibili推送] 缓存登录失败, 请尝试手动登录")
    else:
        logger.error(f"[Bilibili推送] 不存在登录缓存文件, 请尝试手动登录")

scheduler.add_job(
        _load_login_cache, "interval", seconds=2, id="bili_login_sched"
    )