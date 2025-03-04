import json
import os
from pathlib import Path

class Config:
    CONFIG_FILE = 'translator_config.json'
    
    @staticmethod
    def save_api_key(api_key: str) -> None:
        """保存API密钥到配置文件"""
        config_data = {'api_key': api_key}
        try:
            with open(Config.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config_data, f)
        except Exception as e:
            print(f"保存配置失败: {e}")

    @staticmethod
    def load_api_key() -> str:
        """从配置文件加载API密钥"""
        try:
            if os.path.exists(Config.CONFIG_FILE):
                with open(Config.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    return config_data.get('api_key', '')
        except Exception as e:
            print(f"加载配置失败: {e}")
        return ''

    @staticmethod
    def delete_api_key() -> None:
        """删除保存的API密钥"""
        try:
            if os.path.exists(Config.CONFIG_FILE):
                os.remove(Config.CONFIG_FILE)
        except Exception as e:
            print(f"删除配置失败: {e}") 