# 注：其他文件中出现的类似 from .. import config，均是从 __init__.py 导入的 Config 实例
from typing import Optional
from pydantic import BaseSettings


class Config(BaseSettings):
    
    haruka_dir: Optional[str] = None
    haruka_to_me: bool = True

    class Config:
        extra = "ignore"