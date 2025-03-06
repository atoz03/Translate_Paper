# 将图标保存为 icon.ico
import base64

# 这里是图标的 base64 编码，我选择了一个简单的翻译图标
ICON = '''
AAABAAEAICAAAAEAIACoEAAAFgAAACgAAAAgAAAAQAAAAAEAIAAAAAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
[此处省略base64编码，实际使用时我会提供完整的图标数据]
'''

def save_icon():
    """保存图标文件"""
    icon_data = base64.b64decode(ICON)
    with open('translator.ico', 'wb') as f:
        f.write(icon_data)

if __name__ == '__main__':
    save_icon() 