import base64

class Config:
    # 使用简单的 base64 编码存储 API 密钥
    # 实际项目中建议使用更安全的加密方式
    _ENCODED_API_KEY = "QUl6YVN5QkRXakkzMUZkT3lJNkpZaVM4d2FTb3Rma203d29xczRr"
    
    @staticmethod
    def get_api_key():
        """获取解密后的 API 密钥"""
        return base64.b64decode(Config._ENCODED_API_KEY).decode('utf-8') 