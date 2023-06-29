
from typing import List
from loguru import logger
from nonebot.matcher import matchers
from nonebot.adapters.onebot.v11 import Bot, MessageSegment, Message
from nonebot.adapters.onebot.v11.event import MessageEvent
from nonebot.internal.matcher import Matcher, current_event
from nonebot.params import ArgPlainText, CommandArg
from bilireq.grpc.dynamic import grpc_get_user_dynamics
from bilireq.grpc.protos.bilibili.app.dynamic.v2.dynamic_pb2 import DynamicType

from ..utils import on_command, to_me, text_to_img
from ..utils.uid_extract import uid_extract
from ..utils.bilibili_request import get_b23_url
from ..utils import get_dynamic_screenshot, safe_send, scheduler

vive = on_command("查看动态", rule=to_me(), priority=5, block=True) # 数值越小优先级越高
vive.__doc__ = "查看动态"

@vive.handle()
async def _(
    matcher: Matcher, event: MessageEvent, bot:Bot, arg_msg: Message = CommandArg()
):
    if arg_msg.extract_plain_text().strip():
        matcher.set_arg("arg", arg_msg)

@vive.got("arg", "请发送UP名称")
async def _(
    matcher: Matcher, event: MessageEvent, bot:Bot, arg: str = ArgPlainText("arg")
):
    vive_texts = arg.strip().split(' ')
    logger.info(f"接收到查询数据:{vive_texts}")
    name = vive_texts[0]
    if not (uid := await uid_extract(name)):
        return await vive.send(MessageSegment.at(event.user_id) + "未找到该 UP，请输入正确的UP 名、UP UID或 UP 首页链接")

    if int(uid) == 0:
        return await vive.send(MessageSegment.at(event.user_id) + "UP 主不存在")

    try:
        res = await grpc_get_user_dynamics(int(uid))
    except Exception as e:
        return await vive.send(MessageSegment.at(event.user_id) + f"获取动态失败：{e}")

    offset_num = int(vive_texts[1]) if len(vive_texts) > 1 else 0

    if res.list:
        if len(res.list) > 1:
            try:
                if res.list[0].modules[0].module_author.is_top:
                    dyn = res.list[1 + offset_num]
                else:
                    dyn = res.list[0 + offset_num]
            except IndexError:
                return await vive.send(MessageSegment.at(event.user_id) + "你输入的数字过大，该 UP 的最后一页动态没有这么多条")
        else:
            dyn = res.list[0]
        dynamic_id = int(dyn.extend.dyn_id_str)
        shot_image = await get_dynamic_screenshot(dynamic_id)
        if shot_image is None:
            return await vive.send(MessageSegment.at(event.user_id) + f"获取{name}动态失败")
        type_msg = {
                0: "动态",
                DynamicType.forward: "转发动态",
                DynamicType.word: "文字动态",
                DynamicType.draw: "图文动态",
                DynamicType.av: "投稿",
                DynamicType.article: "专栏",
                DynamicType.music: "音频",
            }
        message = (
            MessageSegment.at(event.user_id)
            + f"{name} 发布了{type_msg.get(dyn.card_type, type_msg[0])}：\n"
            + MessageSegment.image(shot_image)
            + f"\n"
            + await get_b23_url(f"https://t.bilibili.com/{dyn.extend.dyn_id_str}")
        )
        return await vive.send(message)
        
    return await vive.send("该 UP 未发布任何动态")
