import logging
import google.generativeai as genai
import requests
import json
from abc import ABC, abstractmethod

class BaseTranslator(ABC):
    @abstractmethod
    def translate(self, text: str, to_chinese: bool) -> str:
        pass

class GeminiTranslator(BaseTranslator):
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def translate(self, text: str, to_chinese: bool) -> str:
        if to_chinese:
            prompt = f"""
            Translate the following English text to Chinese. Requirements:
            1. Keep technical terms accurate
            2. Make the translation natural and fluent
            3. Only return the translated text without any explanation
            
            Text to translate:
            {text}
            """
        else:
            prompt = f"""
            Translate the following Chinese text to English. Requirements:
            1. Keep technical terms accurate
            2. Make the translation professional and natural
            3. Only return the translated text without any explanation
            
            Text to translate:
            {text}
            """
            
        chat = self.model.start_chat(history=[])
        response = chat.send_message(prompt)
        return response.text.strip()

class ZhipuAITranslator(BaseTranslator):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        
    def translate(self, text: str, to_chinese: bool) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        if to_chinese:
            prompt = f"Translate this English text to Chinese, keep it accurate and natural: {text}"
        else:
            prompt = f"Translate this Chinese text to English, keep it accurate and professional: {text}"
            
        data = {
            "model": "glm-4-flash",
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }
        
        try:
            response = requests.post(self.url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        except Exception as e:
            logging.error(f"智谱AI翻译错误: {str(e)}")
            raise 