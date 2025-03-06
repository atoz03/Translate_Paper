import json
import os
import sys
from pathlib import Path

class Config:
    @staticmethod
    def get_config_path():
        """获取配置文件路径"""
        if getattr(sys, 'frozen', False):
            # 如果是打包后的程序
            return os.path.join(os.path.dirname(sys.executable), 'translator_config.json')
        else:
            # 如果是开发环境
            return 'translator_config.json'
    
    @staticmethod
    def save_api_key(api_key: str) -> None:
        """保存API密钥到配置文件"""
        config_data = {'api_key': api_key}
        try:
            with open(Config.get_config_path(), 'w', encoding='utf-8') as f:
                json.dump(config_data, f)
        except Exception as e:
            print(f"保存配置失败: {e}")

    @staticmethod
    def load_api_key() -> str:
        """从配置文件加载API密钥"""
        try:
            config_path = Config.get_config_path()
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    return config_data.get('api_key', '')
        except Exception as e:
            print(f"加载配置失败: {e}")
        return ''

    @staticmethod
    def delete_api_key() -> None:
        """删除保存的API密钥"""
        try:
            if os.path.exists(Config.get_config_path()):
                os.remove(Config.get_config_path())
        except Exception as e:
            print(f"删除配置失败: {e}") 