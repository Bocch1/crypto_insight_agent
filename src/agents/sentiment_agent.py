"""
市场情绪Agent
负责获取和分析市场情绪数据
"""
from typing import Optional
from loguru import logger
from src.models.schemas import AgentState, SentimentData, AnomalyInfo
from src.tools.fear_greed_api import FearGreedAPI
from src.agents.base import BaseAgent


class SentimentAgent(BaseAgent):
    """市场情绪分析Agent"""
    
    def __init__(self):
        super().__init__(name="SentimentAgent")
        self.fear_greed = FearGreedAPI()
    
    def execute(self, state: AgentState) -> AgentState:
        """
        获取情绪数据并检测异常
        
        Args:
            state: 当前状态
            
        Returns:
            更新后的状态
        """
        logger.info(f"情绪Agent开始分析: {state.symbol}")
        
        try:
            # 获取情绪数据
            sentiment_data = self._fetch_sentiment_data(state.symbol)
            if sentiment_data:
                state.sentiment_data = sentiment_data
                
                # 检测异常
                anomalies = self._detect_anomalies(sentiment_data)
                if state.report is None:
                    from src.models.schemas import AnalysisReport
                    state.report = AnalysisReport(
                        symbol=state.symbol or "ETH",
                        summary="",
                        market_analysis="",
                        onchain_analysis="",
                        sentiment_analysis=""
                    )
                state.report.anomalies.extend(anomalies)
                
                state.status = "sentiment_data_collected"
                logger.success(f"情绪数据采集完成: {state.symbol}")
            else:
                logger.warning(f"情绪数据采集失败: {state.symbol}")
                
        except Exception as e:
            logger.error(f"情绪Agent执行失败: {e}")
            state = self.handle_error(state, e)
        
        return state
    
    def _fetch_sentiment_data(self, symbol: Optional[str]) -> Optional[SentimentData]:
        """
        获取情绪数据
        
        Args:
            symbol: 币种
            
        Returns:
            情绪数据对象
        """
        if not symbol:
            symbol = "ETH"
        
        # 去除USDT后缀
        if symbol.endswith("USDT"):
            symbol = symbol[:-4]
        
        try:
            sentiment_data = SentimentData(symbol=symbol)
            
            # 1. 获取恐惧贪婪指数
            fear_greed_data = self.fear_greed.analyze_sentiment()
            if fear_greed_data:
                sentiment_data.fear_greed_index = fear_greed_data["value"]
                sentiment_data.fear_greed_label = fear_greed_data["value_classification"]
                
                logger.info(
                    f"恐惧贪婪指数: {sentiment_data.fear_greed_index} "
                    f"({sentiment_data.fear_greed_label})"
                )
            
            # 2. 获取历史数据进行趋势分析
            historical = self.fear_greed.get_historical_index(days=7)
            if historical:
                # 计算7天变化
                if len(historical) >= 2:
                    oldest = historical[-1]["value"]
                    newest = historical[0]["value"]
                    sentiment_data.social_volume_change = newest - oldest
                    
                    logger.debug(f"7天情绪变化: {sentiment_data.social_volume_change}")
            
            return sentiment_data
            
        except Exception as e:
            logger.error(f"获取情绪数据失败: {e}")
            return None
    
    def _detect_anomalies(self, sentiment_data: SentimentData) -> list:
        """
        检测情绪异常
        
        Args:
            sentiment_data: 情绪数据
            
        Returns:
            异常列表
        """
        anomalies = []
        
        # 1. 极度恐惧/贪婪
        if sentiment_data.fear_greed_index is not None:
            if sentiment_data.fear_greed_index <= 25:
                anomalies.append(AnomalyInfo(
                    type="extreme_fear",
                    severity="medium",
                    description=f"恐惧贪婪指数{sentiment_data.fear_greed_index}，处于极度恐惧区域",
                    data_point={
                        "fear_greed_index": sentiment_data.fear_greed_index,
                        "label": sentiment_data.fear_greed_label
                    }
                ))
            elif sentiment_data.fear_greed_index >= 75:
                anomalies.append(AnomalyInfo(
                    type="extreme_greed",
                    severity="medium",
                    description=f"恐惧贪婪指数{sentiment_data.fear_greed_index}，处于极度贪婪区域",
                    data_point={
                        "fear_greed_index": sentiment_data.fear_greed_index,
                        "label": sentiment_data.fear_greed_label
                    }
                ))
        
        # 2. 情绪剧烈变化
        if sentiment_data.social_volume_change is not None:
            if abs(sentiment_data.social_volume_change) > 20:
                direction = "上升" if sentiment_data.social_volume_change > 0 else "下降"
                anomalies.append(AnomalyInfo(
                    type="sentiment_change",
                    severity="medium",
                    description=f"市场情绪7天内大幅{direction} ({sentiment_data.social_volume_change}点)",
                    data_point={"change": sentiment_data.social_volume_change}
                ))
        
        if anomalies:
            logger.info(f"情绪检测到{len(anomalies)}个异常")
        
        return anomalies