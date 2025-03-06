import PyInstaller.__main__
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # 确保源文件存在
    if not os.path.exists('src/main.py'):
        raise FileNotFoundError("找不到 main.py 文件")

    logger.info("开始打包程序...")
    
    # 打包参数
    PyInstaller.__main__.run([
        'src/main.py',                      # 主程序文件
        '--name=PDF翻译工具',                # 程序名称
        '--windowed',                       # 使用 GUI 模式
        '--onefile',                        # 打包成单个文件
        '--clean',                          # 清理临时文件
        '--noconfirm',                      # 不确认覆盖
        '--log-level=INFO',                 # 设置日志级别
    ])
    
    logger.info("打包完成！")
    logger.info(f"可执行文件位置: {os.path.abspath('dist/PDF翻译工具.exe')}")

except Exception as e:
    logger.error(f"打包过程出错: {str(e)}")
    raise