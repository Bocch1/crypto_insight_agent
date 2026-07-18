"""
终端显示工具
提供流式输出和格式化显示功能
"""
import sys
import time
from typing import Optional
from loguru import logger


class StreamDisplay:
    """流式输出显示"""
    
    def __init__(self, delay: float = 0.02):
        """
        初始化流式显示
        
        Args:
            delay: 每个字符的延迟时间（秒）
        """
        self.delay = delay
    
    def type_text(self, text: str, end: str = "\n"):
        """
        逐字打印文本（打字机效果）
        
        Args:
            text: 要显示的文本
            end: 结束符
        """
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            if char not in [' ', '\n', '\t']:
                time.sleep(self.delay)
        sys.stdout.write(end)
        sys.stdout.flush()
    
    def print_section(self, title: str, content: str, emoji: str = "📌"):
        """
        打印格式化的报告章节
        
        Args:
            title: 章节标题
            content: 章节内容
            emoji: 标题前的emoji
        """
        print(f"\n{emoji} {title}")
        print("-" * 50)
        self.type_text(content)
    
    def print_progress(self, message: str):
        """
        打印进度信息
        
        Args:
            message: 进度消息
        """
        print(f"⏳ {message}...", end=" ")
        sys.stdout.flush()
    
    def print_done(self, status: str = "✅"):
        """
        打印完成状态
        
        Args:
            status: 状态符号
        """
        print(status)
    
    def print_error(self, message: str):
        """
        打印错误信息
        
        Args:
            message: 错误消息
        """
        print(f"❌ {message}")
    
    def print_warning(self, message: str):
        """
        打印警告信息
        
        Args:
            message: 警告消息
        """
        print(f"⚠️  {message}")


# 全局实例
display = StreamDisplay(delay=0.015)