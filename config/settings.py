"""
全局配置管理 - 简化版
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """应用配置类 - 支持运行时动态更新"""
    
    def __init__(self):
        self._reload()
    
    def _reload(self):
        """重新加载配置（从环境变量读取，支持运行时更新）"""
        self.DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
        self.DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        self.BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
        self.BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
        self.BINANCE_BASE_URL = os.getenv("BINANCE_BASE_URL", "https://api.binance.com")
        self.ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "")
        self.ETHERSCAN_BASE_URL = os.getenv("ETHERSCAN_BASE_URL", "https://api.etherscan.io/v2/api")
        self.NEWS_API_KEY = os.getenv("NEWS_API_KEY")
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))
        self.REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
        self.MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
        self.LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
        self.LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "crypto-insight-agent")
    
    @property
    def is_deepseek_configured(self) -> bool:
        return bool(self.DEEPSEEK_API_KEY) and "your_" not in self.DEEPSEEK_API_KEY
    
    @property
    def is_etherscan_configured(self) -> bool:
        return bool(self.ETHERSCAN_API_KEY) and "your_" not in self.ETHERSCAN_API_KEY


settings = Settings()