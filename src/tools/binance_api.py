
"""
币安API封装
提供市场数据查询功能
"""
from typing import Optional, Dict, Any
import requests
from loguru import logger
from config.settings import settings
from src.utils.retry import retry_with_backoff


class BinanceAPI:
    """币安API客户端"""
    
    def __init__(self):
        self.base_url = settings.BINANCE_BASE_URL
        self.fapi_base_url = "https://fapi.binance.com"  # 合约API
        self.api_key = settings.BINANCE_API_KEY
        self.api_secret = settings.BINANCE_API_SECRET
        self.timeout = settings.REQUEST_TIMEOUT
        
        # 如果是公开接口，不需要headers
        self.headers = {}
        if self.api_key:
            self.headers["X-MBX-APIKEY"] = self.api_key
        
        logger.info("币安API客户端初始化完成")
    
    @retry_with_backoff(max_attempts=3)
    def get_ticker_24h(self, symbol: str = "ETHUSDT") -> Optional[Dict[str, Any]]:
        """
        获取24小时价格统计
        
        Args:
            symbol: 交易对，如ETHUSDT
            
        Returns:
            24小时价格统计数据
        """
        try:
            url = f"{self.base_url}/api/v3/ticker/24hr"
            params = {"symbol": symbol}
            
            response = requests.get(
                url, 
                params=params, 
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"成功获取{symbol} 24小时数据: 价格={data.get('lastPrice')}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"获取{symbol} 24小时数据失败: {e}")
            raise
    
    @retry_with_backoff(max_attempts=3)
    def get_order_book(self, symbol: str = "ETHUSDT", limit: int = 20) -> Optional[Dict[str, Any]]:
        """
        获取订单簿深度数据
        
        Args:
            symbol: 交易对
            limit: 深度档位(5/10/20/50/100)
            
        Returns:
            订单簿数据，包含bids和asks
        """
        try:
            url = f"{self.base_url}/api/v3/depth"
            params = {"symbol": symbol, "limit": limit}
            
            response = requests.get(
                url, 
                params=params, 
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            logger.debug(f"获取{symbol}订单簿数据 买一={data['bids'][0][0]}, 卖一={data['asks'][0][0]}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"获取{symbol}订单簿失败: {e}")
            raise
    
    def get_funding_rate(self, symbol: str = "ETHUSDT") -> Optional[float]:
        """
        获取永续合约资金费率
        
        Args:
            symbol: 交易对
            
        Returns:
            最新资金费率，失败时返回None
        """
        try:
            # 使用合约API (fapi.binance.com)
            url = f"{self.fapi_base_url}/fapi/v1/fundingRate"
            params = {"symbol": symbol, "limit": 1}
            
            response = requests.get(
                url, 
                params=params,
                timeout=self.timeout
            )
            
            # 如果404，说明交易对不存在或API路径不对
            if response.status_code == 404:
                logger.debug(f"{symbol}合约交易对不存在，跳过资金费率")
                return None
            
            response.raise_for_status()
            
            data = response.json()
            if data and len(data) > 0:
                funding_rate = float(data[0]["fundingRate"])
                logger.debug(f"获取{symbol}资金费率: {funding_rate}")
                return funding_rate
            
            return None
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"获取{symbol}资金费率失败（非关键数据）: {e}")
            return None
    
    def calculate_volatility(self, symbol: str = "ETHUSDT") -> Optional[float]:
        """
        计算波动率(基于24小时高低价差)
        
        Args:
            symbol: 交易对
            
        Returns:
            波动率百分比
        """
        ticker = self.get_ticker_24h(symbol)
        if ticker:
            high = float(ticker["highPrice"])
            low = float(ticker["lowPrice"])
            current = float(ticker["lastPrice"])
            
            # 波动率 = (最高价 - 最低价) / 当前价格
            volatility = (high - low) / current if current > 0 else 0
            logger.debug(f"{symbol}波动率: {volatility:.4f}")
            return volatility
        return None
    
    def get_24h_price_change(self, symbol: str = "ETHUSDT") -> Optional[Dict[str, float]]:
        """
        获取24小时价格变化统计
        
        Returns:
            包含价格变化和百分比的字典
        """
        ticker = self.get_ticker_24h(symbol)
        if ticker:
            return {
                "price": float(ticker["lastPrice"]),
                "change": float(ticker["priceChange"]),
                "change_percent": float(ticker["priceChangePercent"]),
                "high": float(ticker["highPrice"]),
                "low": float(ticker["lowPrice"]),
                "volume": float(ticker["volume"])
            }
        return None