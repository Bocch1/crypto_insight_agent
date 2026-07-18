"""
市场数据Agent
负责获取和分析交易所市场数据
"""
from typing import Optional
from loguru import logger
from src.models.schemas import AgentState, MarketData, AnomalyInfo
from src.tools.binance_api import BinanceAPI
from src.agents.base import BaseAgent


class MarketAgent(BaseAgent):
    """市场数据分析Agent"""
    
    def __init__(self):
        super().__init__(name="MarketAgent")
        self.binance = BinanceAPI()
    
    def execute(self, state: AgentState) -> AgentState:
        """
        获取市场数据并检测异常
        
        Args:
            state: 当前状态
            
        Returns:
            更新后的状态
        """
        logger.info(f"市场Agent开始分析 {state.symbol}")
        
        try:
            # 获取市场数据
            market_data = self._fetch_market_data(state.symbol)
            if market_data:
                state.market_data = market_data
                
                # 检测异常
                anomalies = self._detect_anomalies(market_data)
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
                
                state.status = "market_data_collected"
                logger.success(f"市场数据采集完成: {state.symbol}")
            else:
                logger.warning(f"市场数据采集失败: {state.symbol}")
                
        except Exception as e:
            logger.error(f"市场Agent执行失败: {e}")
            state = self.handle_error(state, e)
        
        return state
    
    def _fetch_market_data(self, symbol: Optional[str]) -> Optional[MarketData]:
        """
        获取市场数据
        
        Args:
            symbol: 币种
            
        Returns:
            市场数据对象
        """
        if not symbol:
            symbol = "ETH"
        
        # 确保是USDT交易对
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"
        
        try:
            # 获取24小时数据
            ticker = self.binance.get_ticker_24h(symbol)
            if not ticker:
                return None
            
            # 获取波动率
            volatility = self.binance.calculate_volatility(symbol)
            
            # 获取资金费率
            funding_rate = None
            try:
                funding_rate = self.binance.get_funding_rate(symbol)
            except Exception as e:
                logger.warning(f"获取资金费率失败: {e}")
            
            # 构建市场数据
            market_data = MarketData(
                symbol=symbol,
                current_price=float(ticker["lastPrice"]),
                price_change_24h=float(ticker["priceChangePercent"]),
                high_24h=float(ticker["highPrice"]),
                low_24h=float(ticker["lowPrice"]),
                volume_24h=float(ticker["volume"]),
                volatility=volatility,
                funding_rate=funding_rate
            )
            
            return market_data
            
        except Exception as e:
            logger.error(f"获取市场数据失败: {e}")
            return None
    
    def _detect_anomalies(self, market_data: MarketData) -> list:
        """
        检测市场异常
        
        Args:
            market_data: 市场数据
            
        Returns:
            异常列表
        """
        anomalies = []
        
        # 1. 价格波动异常
        if abs(market_data.price_change_24h) > 10:
            anomalies.append(AnomalyInfo(
                type="price_volatility",
                severity="high",
                description=f"24小时价格波动{market_data.price_change_24h:.2f}%，超过10%阈值",
                data_point={"price_change": market_data.price_change_24h}
            ))
        elif abs(market_data.price_change_24h) > 5:
            anomalies.append(AnomalyInfo(
                type="price_volatility",
                severity="medium",
                description=f"24小时价格波动{market_data.price_change_24h:.2f}%，超过5%阈值",
                data_point={"price_change": market_data.price_change_24h}
            ))
        
        # 2. 高波动率
        if market_data.volatility and market_data.volatility > 0.05:
            anomalies.append(AnomalyInfo(
                type="high_volatility",
                severity="medium",
                description=f"当前波动率{market_data.volatility:.4f}，处于较高水平",
                data_point={"volatility": market_data.volatility}
            ))
        
        # 3. 资金费率异常
        if market_data.funding_rate is not None:
            if abs(market_data.funding_rate) > 0.001:
                direction = "多头" if market_data.funding_rate > 0 else "空头"
                anomalies.append(AnomalyInfo(
                    type="funding_rate",
                    severity="medium",
                    description=f"资金费率{market_data.funding_rate:.4f}，{direction}成本较高",
                    data_point={"funding_rate": market_data.funding_rate}
                ))
        
        if anomalies:
            logger.info(f"市场检测到{len(anomalies)}个异常")
        
        return anomalies