from typing import Any, List, Dict, Optional
from pydantic import BaseSettings
from bilireq.auth import Auth

class BiliAuth(BaseSettings):
    auth: Optional[Auth]
    is_logined:bool

    def set_auth(self, auth:Auth):
        self.auth = auth
        self.is_logined = True

    def remove_auth(self):
        self.auth = None
        self.is_logined = False

    def get_cookie_array(self) -> List[Any]:
        """获取数组类型的cookies数据"""
        if self.auth:
            return self.auth["origin"]["cookie_info"]["cookies"]
        else:
            return list()
        
    def get_cookie_dict(self) -> Dict[str, Any]:
        """获取Dict类型的cookies数据"""
        if self.auth:
            return self.auth.cookies
        else:
            return dict()

bili_auth = BiliAuth(auth=None, is_logined=False)