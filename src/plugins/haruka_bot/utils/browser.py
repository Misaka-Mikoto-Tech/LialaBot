import base64
import os
import sys
from typing import Optional

from nonebot import get_driver
from nonebot.log import logger
from playwright.__main__ import main
from playwright.async_api import Browser, async_playwright

from .. import config

_browser: Optional[Browser] = None


async def init_browser(proxy=config.haruka_proxy, **kwargs) -> Browser:
    if proxy:
        kwargs["proxy"] = {"server": proxy}
    global _browser
    p = await async_playwright().start()
    return await p.chromium.launch(**kwargs)


async def get_browser(**kwargs) -> Browser:
    return _browser or await init_browser(**kwargs)


async def get_dynamic_screenshot(url, style=config.haruka_screenshot_style):
    """获取动态截图"""
    if style == "mobile":
        return await get_dynamic_screenshot_mobile(url)
    else:
        return await get_dynamic_screenshot_pc(url)


async def get_dynamic_screenshot_mobile(url):
    """移动端动态截图"""
    browser = await get_browser()
    page = None
    try:
        page = await browser.new_page(
            device_scale_factor=2,
            user_agent=(
                "Mozilla/5.0 (Linux; Android 10; RMX1911) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/100.0.4896.127 Mobile Safari/537.36"
            ),
            viewport={"width": 360, "height": 780},
        )
        await page.goto(url, wait_until="networkidle", timeout=10000)
        content = await page.content()
        # 去掉关注按钮
        content = content.replace(
            '<div class="dyn-header__right">'
            '<div data-pos="follow" class="dyn-header__following">'
            '<span class="dyn-header__following__icon"></span>'
            '<span class="dyn-header__following__text">关注</span></div></div>',
            "",
        )
        # 1. 字体问题：.dyn-class里font-family是PingFangSC-Regular，使用行内CSS覆盖掉它
        # 2. 换行问题：遇到太长的内容（长单词、某些长链接等）允许强制换行，防止溢出
        content = content.replace(
            '<div class="dyn-card">',
            '<div class="dyn-card" '
            'style="font-family: sans-serif; overflow-wrap: break-word;">',
        )
        # 去掉打开APP的按钮，防止遮挡较长的动态
        content = content.replace(
            '<div class="launch-app-btn dynamic-float-openapp dynamic-float-btn">'
            '<div class="m-dynamic-float-openapp">'
            "<span>打开APP，查看更多精彩内容</span></div> <!----></div>",
            "",
        )
        await page.set_content(content)
        card = await page.query_selector(".dyn-card")
        assert card
        clip = await card.bounding_box()
        assert clip
        image = await page.screenshot(clip=clip, full_page=True)
        await page.close()
        return base64.b64encode(image).decode()
    except Exception:
        if page:
            await page.close()
        raise


async def get_dynamic_screenshot_pc(url):
    """电脑端动态截图"""
    browser = await get_browser()
    context = None
    try:
        context = await browser.new_context(
            viewport={"width": 2560, "height": 1080},
            device_scale_factor=2,
        )
        await context.add_cookies(
            [
                {
                    "name": "hit-dyn-v2",
                    "value": "1",
                    "domain": ".bilibili.com",
                    "path": "/",
                }
            ]
        )
        page = await context.new_page()
        await page.goto(url, wait_until="networkidle", timeout=10000)
        card = await page.query_selector(".card")
        assert card
        clip = await card.bounding_box()
        assert clip
        bar = await page.query_selector(".bili-dyn-action__icon")
        assert bar
        bar_bound = await bar.bounding_box()
        assert bar_bound
        clip["height"] = bar_bound["y"] - clip["y"]
        image = await page.screenshot(clip=clip, full_page=True)
        await context.close()
        return base64.b64encode(image).decode()
    except Exception:
        if context:
            await context.close()
        raise


def install():
    """自动安装、更新 Chromium"""

    def restore_env():
        del os.environ["PLAYWRIGHT_DOWNLOAD_HOST"]
        if config.haruka_proxy:
            del os.environ["HTTPS_PROXY"]
        if original_proxy is not None:
            os.environ["HTTPS_PROXY"] = original_proxy

    logger.info("检查 Chromium 更新")
    sys.argv = ["", "install", "chromium"]
    original_proxy = os.environ.get("HTTPS_PROXY")
    # TODO 检查 google 可访问性
    # TODO 检查个锤子，直接加个设置项让用户自己选择开关
    if config.haruka_proxy:
        os.environ["HTTPS_PROXY"] = config.haruka_proxy
    os.environ["PLAYWRIGHT_DOWNLOAD_HOST"] = "https://npmmirror.com/mirrors/playwright/"
    success = False
    try:
        main()
    except SystemExit as e:
        if e.code == 0:
            success = True
    if not success:
        logger.info("Chromium 更新失败，尝试从原始仓库下载，速度较慢")
        os.environ["PLAYWRIGHT_DOWNLOAD_HOST"] = ""
        try:
            main()
        except SystemExit as e:
            if e.code != 0:
                restore_env()
                raise RuntimeError("未知错误，Chromium 下载失败")
    restore_env()


async def check_playwright_env():
    """检查 Playwright 依赖"""
    logger.info("检查 Playwright 依赖")
    try:
        async with async_playwright() as p:
            await p.chromium.launch()
    except Exception:
        raise ImportError(
            "加载失败，Playwright 依赖不全，"
            "解决方法：https://haruka-bot.sk415.icu/faq.html#playwright-依赖不全"
        )


async def shutdown_browser():
    """关闭浏览器"""
    if _browser:
        await _browser.close()


get_driver().on_startup(init_browser)
get_driver().on_shutdown(shutdown_browser)
