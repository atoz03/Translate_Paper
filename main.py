import sys
import os
# 修改代理设置为正确的端口
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7897'  # 改为你的Clash端口
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7897'   # 改为你的Clash端口

# 添加环境变量来抑制警告
os.environ['GRPC_ENABLE_FORK_SUPPORT'] = 'false'
# 添加日志配置
import logging
logging.basicConfig(level=logging.INFO)  # 改为INFO级别以便查看更多信息

from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QTextEdit, 
                            QVBoxLayout, QHBoxLayout, QWidget, QMessageBox,
                            QLabel, QStatusBar, QFileDialog, QDialog, QLineEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import google.generativeai as genai
from config import Config
import fitz  # PyMuPDF

class APIKeyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('输入API密钥')
        self.setFixedWidth(400)
        
        layout = QVBoxLayout(self)
        
        # 添加说明文本
        info_label = QLabel('请输入您的 Gemini API 密钥:')
        layout.addWidget(info_label)
        
        # 添加输入框
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText('在此输入API密钥...')
        layout.addWidget(self.key_input)
        
        # 添加按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton('确定')
        cancel_button = QPushButton('取消')
        
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
    def get_api_key(self):
        return self.key_input.text().strip()

class TranslatorThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, text, api_key, is_english_to_chinese):
        super().__init__()
        self.text = text
        self.api_key = api_key
        self.is_english_to_chinese = is_english_to_chinese

    def run(self):
        try:
            logging.info("开始配置API...")
            genai.configure(api_key=self.api_key)
            
            # 使用 Gemini 2.0 Flash 模型
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            logging.info("开始翻译...")
            chat = model.start_chat(history=[])
            
            if self.is_english_to_chinese:
                prompt = f"""
                Translate the following English text to Chinese. Requirements:
                1. Keep technical terms accurate
                2. Make the translation natural and fluent
                3. Only return the translated text without any explanation
                
                Text to translate:
                {self.text}
                """
            else:
                prompt = f"""
                Translate the following Chinese text to English. Requirements:
                1. Keep technical terms accurate
                2. Make the translation professional and natural
                3. Only return the translated text without any explanation
                
                Text to translate:
                {self.text}
                """
            
            response = chat.send_message(prompt)
            
            logging.info("翻译完成")
            self.finished.emit(response.text.strip())
        except Exception as e:
            logging.error(f"翻译错误: {str(e)}")
            self.error.emit(str(e))

class TranslatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # 先获取API密钥
        api_key = self.get_api_key_from_user()
        if not api_key:
            sys.exit(0)  # 如果用户取消，则退出程序
            
        self.api_key = api_key
        self.is_english_to_chinese = True
        self.pdf_doc = None
        self.current_page = 0
        self.initUI()
        
        # 测试网络连接
        self.test_connection()

    def get_api_key_from_user(self):
        """显示对话框获取API密钥"""
        dialog = APIKeyDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            api_key = dialog.get_api_key()
            if api_key:
                return api_key
            else:
                QMessageBox.warning(self, "错误", "API密钥不能为空")
                return self.get_api_key_from_user()
        return None

    def test_connection(self):
        try:
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content("Hello")
            logging.info("API连接测试成功")
        except Exception as e:
            logging.error(f"API连接测试失败: {str(e)}")
            reply = QMessageBox.warning(
                self, 
                "连接错误", 
                f"无法连接到Gemini API，可能是密钥无效。\n错误信息：{str(e)}\n\n是否重新输入API密钥？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                new_key = self.get_api_key_from_user()
                if new_key:
                    self.api_key = new_key
                    self.test_connection()
                else:
                    sys.exit(0)
            else:
                sys.exit(0)

    def initUI(self):
        # 主窗口设置
        self.setWindowTitle('文本翻译工具')
        self.setGeometry(100, 100, 1200, 600)

        # 创建中心部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)  # 改为垂直布局
        
        # 工具栏区域
        toolbar_layout = QHBoxLayout()
        
        # 添加清空按钮
        self.clear_btn = QPushButton('清空')
        self.clear_btn.clicked.connect(self.clear_text)
        toolbar_layout.addWidget(self.clear_btn)
        
        # 添加复制按钮
        self.copy_btn = QPushButton('复制译文')
        self.copy_btn.clicked.connect(self.copy_translation)
        toolbar_layout.addWidget(self.copy_btn)
        
        # 添加字数统计标签
        self.word_count_label = QLabel('字数: 0')
        toolbar_layout.addWidget(self.word_count_label)
        
        # 添加PDF上传按钮到工具栏
        self.upload_btn = QPushButton('上传PDF')
        self.upload_btn.clicked.connect(self.upload_pdf)
        toolbar_layout.addWidget(self.upload_btn)
        
        # 添加页码显示到工具栏
        self.page_label = QLabel('PDF页码: -')
        toolbar_layout.addWidget(self.page_label)
        
        # 添加PDF导航按钮
        self.prev_btn = QPushButton('上一页')
        self.next_btn = QPushButton('下一页')
        self.prev_btn.clicked.connect(self.prev_page)
        self.next_btn.clicked.connect(self.next_page)
        self.prev_btn.setEnabled(False)
        self.next_btn.setEnabled(False)
        toolbar_layout.addWidget(self.prev_btn)
        toolbar_layout.addWidget(self.next_btn)
        
        # 添加到主布局
        layout.addLayout(toolbar_layout)

        # 翻译区域
        translate_layout = QHBoxLayout()
        
        # 左侧输入区
        left_layout = QVBoxLayout()
        self.source_text = QTextEdit()
        self.update_source_placeholder()  # 更新占位符文本
        self.source_text.textChanged.connect(self.update_word_count)
        left_layout.addWidget(self.source_text)

        # 中间按钮区
        middle_layout = QVBoxLayout()
        self.translate_btn = QPushButton('翻译 →')
        self.translate_btn.setFixedWidth(100)
        self.translate_btn.clicked.connect(self.translate_text)
        middle_layout.addWidget(self.translate_btn)
        
        # 修改交换按钮
        self.swap_btn = QPushButton('⇄')
        self.swap_btn.setFixedWidth(100)
        self.swap_btn.clicked.connect(self.swap_languages)
        middle_layout.addWidget(self.swap_btn)
        
        middle_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 右侧输出区
        right_layout = QVBoxLayout()
        self.target_text = QTextEdit()
        self.update_target_placeholder()  # 更新占位符文本
        self.target_text.setReadOnly(True)
        right_layout.addWidget(self.target_text)

        # 添加到翻译布局
        translate_layout.addLayout(left_layout)
        translate_layout.addLayout(middle_layout)
        translate_layout.addLayout(right_layout)
        
        # 添加到主布局
        layout.addLayout(translate_layout)
        
        # 添加状态栏
        self.statusBar().showMessage('就绪')

    def clear_text(self):
        """清空所有文本"""
        self.source_text.clear()
        self.target_text.clear()
        self.update_word_count()
        if self.pdf_doc:
            self.pdf_doc.close()
            self.pdf_doc = None
            self.current_page = 0
            self.update_pdf_buttons()
        
    def copy_translation(self):
        """复制翻译结果到剪贴板"""
        text = self.target_text.toPlainText()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self.statusBar().showMessage('已复制到剪贴板', 2000)
            
    def update_word_count(self):
        """更新字数统计"""
        text = self.source_text.toPlainText()
        word_count = len(text.split())
        char_count = len(text)
        self.word_count_label.setText(f'单词数: {word_count} | 字符数: {char_count}')
        
    def update_source_placeholder(self):
        """更新源文本框的占位符"""
        if self.is_english_to_chinese:
            self.source_text.setPlaceholderText("在此输入英文文本...")
        else:
            self.source_text.setPlaceholderText("在此输入中文文本...")
            
    def update_target_placeholder(self):
        """更新目标文本框的占位符"""
        if self.is_english_to_chinese:
            self.target_text.setPlaceholderText("中文翻译将显示在这里...")
        else:
            self.target_text.setPlaceholderText("English translation will appear here...")

    def swap_languages(self):
        """交换源语言和目标语言"""
        self.is_english_to_chinese = not self.is_english_to_chinese
        source = self.source_text.toPlainText()
        target = self.target_text.toPlainText()
        self.source_text.setText(target)
        self.target_text.setText(source)
        self.update_source_placeholder()
        self.update_target_placeholder()
        self.update_word_count()
        self.statusBar().showMessage('已切换翻译方向', 2000)

    def translate_text(self):
        source = self.source_text.toPlainText().strip()
        if not source:
            return
            
        self.translate_btn.setEnabled(False)
        self.translate_btn.setText("翻译中...")
        
        # 创建翻译线程，传入翻译方向
        self.thread = TranslatorThread(source, self.api_key, self.is_english_to_chinese)
        self.thread.finished.connect(self.on_translation_finished)
        self.thread.error.connect(self.on_translation_error)
        self.thread.start()

    def on_translation_finished(self, result):
        self.target_text.setText(result)
        self.translate_btn.setEnabled(True)
        self.translate_btn.setText("翻译 →")
        self.statusBar().showMessage('翻译完成', 2000)

    def on_translation_error(self, error_msg):
        self.target_text.setText(f"翻译出错：{error_msg}")
        self.translate_btn.setEnabled(True)
        self.translate_btn.setText("翻译 →")
        self.statusBar().showMessage('翻译失败', 2000)

    def upload_pdf(self):
        """上传并处理PDF文件"""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "选择PDF文件",
            "",
            "PDF Files (*.pdf)"
        )
        
        if file_name:
            try:
                # 打开PDF文件
                self.pdf_doc = fitz.open(file_name)
                self.current_page = 0
                
                # 更新UI状态
                self.prev_btn.setEnabled(False)
                self.next_btn.setEnabled(self.pdf_doc.page_count > 1)
                self.page_label.setText(f'PDF页码: 1/{self.pdf_doc.page_count}')
                
                # 加载第一页内容
                self.load_pdf_page()
                
                self.statusBar().showMessage(f'已加载PDF文件: {file_name}', 2000)
            except Exception as e:
                QMessageBox.warning(self, "错误", f"无法打开PDF文件：{str(e)}")
                self.pdf_doc = None
                self.current_page = 0
                self.update_pdf_buttons()

    def load_pdf_page(self):
        """加载当前页面的内容"""
        if not self.pdf_doc:
            return
            
        try:
            page = self.pdf_doc[self.current_page]
            text = page.get_text()
            self.source_text.setText(text)
            self.page_label.setText(f'PDF页码: {self.current_page + 1}/{self.pdf_doc.page_count}')
            self.update_pdf_buttons()
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法读取PDF页面：{str(e)}")

    def update_pdf_buttons(self):
        """更新PDF导航按钮状态"""
        if not self.pdf_doc:
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
            self.page_label.setText('PDF页码: -')
            return
            
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page < self.pdf_doc.page_count - 1)

    def prev_page(self):
        """显示上一页"""
        if self.pdf_doc and self.current_page > 0:
            self.current_page -= 1
            self.load_pdf_page()

    def next_page(self):
        """显示下一页"""
        if self.pdf_doc and self.current_page < self.pdf_doc.page_count - 1:
            self.current_page += 1
            self.load_pdf_page()

def main():
    app = QApplication(sys.argv)
    translator = TranslatorApp()
    translator.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 