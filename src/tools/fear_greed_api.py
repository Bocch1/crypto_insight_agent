"""
恐惧贪婪指数API封装
"""
from typing import Optional, Dict, Any, List
import requests
from loguru import logger
from config.settings import settings
from src.utils.retry import retry_with_backoff


class FearGreedAPI:
    """恐惧贪婪指数API客户端"""
    
    BASE_URL = "https://api.alternative.me/fng/"
    
    def __init__(self):
        self.timeout = settings.REQUEST_TIMEOUT
        logger.info("恐惧贪婪指数API客户端初始化完成")
    
    @retry_with_backoff(max_attempts=3)
    def get_current_index(self) -> Optional[Dict[str, Any]]:
        """
        获取当前恐惧贪婪指数
        
        Returns:
            包含指数值和标签的字典
            {
                "value": 65,
                "value_classification": "Greed",
                "timestamp": "1234567890"
            }
        """
        try:
            params = {"limit": 1}
            
            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("data") and len(data["data"]) > 0:
                current = data["data"][0]
                index_data = {
                    "value": int(current["value"]),
                    "value_classification": current["value_classification"],
                    "timestamp": current["timestamp"]
                }
                logger.info(f"恐惧贪婪指数: {index_data['value']} ({index_data['value_classification']})")
                return index_data
            
            logger.error("恐惧贪婪指数数据为空")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"获取恐惧贪婪指数失败: {e}")
            raise
    
    @retry_with_backoff(max_attempts=3)
    def get_historical_index(self, days: int = 7) -> Optional[List[Dict[str, Any]]]:
        """
        获取历史恐惧贪婪指数
        
        Args:
            days: 获取天数
            
        Returns:
            历史数据列表
        """
        try:
            params = {"limit": days}
            
            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("data"):
                historical_data = [
                    {
                        "value": int(item["value"]),
                        "value_classification": item["value_classification"],
                        "timestamp": item["timestamp"]
                    }
                    for item in data["data"]
                ]
                logger.debug(f"获取历史恐惧贪婪指数: {len(historical_data)}条记录")
                return historical_data
            
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"获取历史恐惧贪婪指数失败: {e}")
            raise
    
    def analyze_sentiment(self) -> Optional[Dict[str, Any]]:
        """
        分析当前市场情绪
        
        Returns:
            情绪分析结果
        """
        current = self.get_current_index()
        if not current:
            return None
        
        value = current["value"]
        
        # 分类
        if value <= 25:
            analysis = "极度恐惧 - 市场可能超卖，是潜在买入机会"
        elif value <= 45:
            analysis = "恐惧 - 市场情绪谨慎，投资者避险"
        elif value <= 55:
            analysis = "中性 - 市场情绪平稳"
        elif value <= 75:
            analysis = "贪婪 - 市场情绪乐观，注意风险"
        else:
            analysis = "极度贪婪 - 市场可能超买，存在回调风险"
        
        return {
            **current,
            "analysis": analysis
        }