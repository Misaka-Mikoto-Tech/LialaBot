﻿import nonebot_plugin_naturel_gpt
from ... import utils

nonebot_plugin_naturel_gpt.set_permission_check_func(utils.permission_check_chatgpt)