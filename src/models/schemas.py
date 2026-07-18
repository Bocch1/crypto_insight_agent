"""
核心数据模型定义
使用Pydantic确保类型安全
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class MarketData(BaseModel):
    """市场数据结构"""
    symbol: str = Field(..., description="交易对，如ETHUSDT")
    current_price: float = Field(..., description="当前价格")
    price_change_24h: float = Field(..., description="24小时价格变化百分比")
    high_24h: float = Field(..., description="24小时最高价")
    low_24h: float = Field(..., description="24小时最低价")
    volume_24h: float = Field(..., description="24小时成交量")
    
    # 衍生指标
    volatility: Optional[float] = Field(None, description="波动率")
    bid_ask_spread: Optional[float] = Field(None, description="买卖价差")
    funding_rate: Optional[float] = Field(None, description="永续合约资金费率")
    
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "ETHUSDT",
                "current_price": 3500.5,
                "price_change_24h": 2.5,
                "high_24h": 3550.0,
                "low_24h": 3400.0,
                "volume_24h": 1234567.89,
                "volatility": 0.023,
                "funding_rate": 0.0001
            }
        }


class OnchainData(BaseModel):
    """链上数据结构"""
    symbol: str = Field(..., description="币种")
    network: str = Field(default="ethereum", description="网络")
    
    # 转账相关
    large_transactions: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="大额交易列表"
    )
    exchange_inflow: Optional[float] = Field(None, description="交易所净流入")
    exchange_outflow: Optional[float] = Field(None, description="交易所净流出")
    
    # 地址相关
    active_addresses_24h: Optional[int] = Field(None, description="24小时活跃地址数")
    new_addresses_24h: Optional[int] = Field(None, description="24小时新增地址数")
    
    # Gas相关
    average_gas_price: Optional[float] = Field(None, description="平均Gas价格(Gwei)")
    gas_price_change: Optional[float] = Field(None, description="Gas价格变化百分比")
    
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "ETH",
                "network": "ethereum",
                "large_transactions": [
                    {"hash": "0x123...", "value": 1000.5, "from": "0xabc...", "to": "0xdef..."}
                ],
                "exchange_inflow": 5000.5,
                "exchange_outflow": 3000.2,
                "active_addresses_24h": 450000,
                "average_gas_price": 25.5
            }
        }


class SentimentData(BaseModel):
    """市场情绪数据结构"""
    symbol: str = Field(..., description="币种")
    
    # 情绪指数
    fear_greed_index: Optional[int] = Field(
        None, 
        description="恐惧贪婪指数(0-100)，0=极度恐惧，100=极度贪婪"
    )
    fear_greed_label: Optional[str] = Field(None, description="情绪标签")
    
    # 新闻分析
    news_sentiment_score: Optional[float] = Field(
        None, 
        description="新闻情感得分(-1到1)"
    )
    news_count_24h: Optional[int] = Field(None, description="24小时新闻数量")
    top_headlines: List[str] = Field(default_factory=list, description="重要新闻标题")
    
    # 社交情绪
    social_volume_change: Optional[float] = Field(None, description="社交媒体讨论量变化")
    
    timestamp: datetime = Field(default_factory=datetime.now)


class AnomalyInfo(BaseModel):
    """异常信息"""
    type: str = Field(..., description="异常类型")
    severity: str = Field(..., description="严重程度: low/medium/high")
    description: str = Field(..., description="异常描述")
    data_point: Dict[str, Any] = Field(default_factory=dict, description="相关数据")


class AnalysisReport(BaseModel):
    """综合分析报告"""
    symbol: str = Field(..., description="分析币种")
    summary: str = Field(..., description="总结")
    
    # 异常检测
    anomalies: List[AnomalyInfo] = Field(default_factory=list, description="检测到的异常")
    risk_score: Optional[float] = Field(None, description="风险评分(0-100)")
    
    # 详细分析
    market_analysis: str = Field(..., description="市场分析")
    onchain_analysis: str = Field(..., description="链上分析")
    sentiment_analysis: str = Field(..., description="情绪分析")
    
    # 时间
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "ETH",
                "summary": "ETH当前市场表现稳定，链上活动正常，情绪中性偏积极",
                "risk_score": 35.0,
                "market_analysis": "24小时价格小幅上涨2.5%，成交量正常",
                "onchain_analysis": "未发现大额异常转账，交易所资金流出正常",
                "sentiment_analysis": "恐惧贪婪指数65(贪婪)，新闻情绪偏正面"
            }
        }


class AgentState(BaseModel):
    """Agent工作流状态"""
    # 用户输入
    query: str = Field(default="", description="用户原始查询")
    symbol: Optional[str] = Field(None, description="识别的币种")
    
    # 各Agent数据
    market_data: Optional[MarketData] = None
    onchain_data: Optional[OnchainData] = None
    sentiment_data: Optional[SentimentData] = None
    
    # 分析结果
    report: Optional[AnalysisReport] = None
    
    # 控制
    error_count: int = Field(default=0, description="错误计数")
    status: str = Field(default="initialized", description="当前状态")
    
    # 中间结果
    plan: List[str] = Field(default_factory=list, description="执行计划")
    current_step: str = Field(default="", description="当前步骤")