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
    def save_api_keys(gemini_key: str = None, zhipu_key: str = None) -> None:
        """保存API密钥到配置文件"""
        config_data = {}
        if gemini_key is not None:
            config_data['gemini_key'] = gemini_key
        if zhipu_key is not None:
            config_data['zhipu_key'] = zhipu_key
            
        try:
            # 如果文件已存在，先读取现有配置
            if os.path.exists(Config.get_config_path()):
                with open(Config.get_config_path(), 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    config_data = {**existing_data, **config_data}
                    
            with open(Config.get_config_path(), 'w', encoding='utf-8') as f:
                json.dump(config_data, f)
        except Exception as e:
            print(f"保存配置失败: {e}")

    @staticmethod
    def load_api_keys() -> tuple:
        """从配置文件加载API密钥"""
        try:
            config_path = Config.get_config_path()
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    return (
                        config_data.get('gemini_key', ''),
                        config_data.get('zhipu_key', '')
                    )
        except Exception as e:
            print(f"加载配置失败: {e}")
        return '', ''

    @staticmethod
    def delete_api_key() -> None:
        """删除保存的API密钥"""
        try:
            if os.path.exists(Config.get_config_path()):
                os.remove(Config.get_config_path())
        except Exception as e:
            print(f"删除配置失败: {e}") 