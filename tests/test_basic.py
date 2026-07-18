"""
基础功能测试
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from loguru import logger
from src.utils.logger import setup_logger

# 初始化日志
setup_logger("DEBUG")


def test_config():
    """测试配置加载"""
    from config.settings import settings
    
    logger.info("测试配置加载...")
    assert settings.REQUEST_TIMEOUT == 30
    assert settings.MAX_RETRIES == 3
    logger.success("配置加载测试通过")


def test_binance_api():
    """测试币安API"""
    from src.tools.binance_api import BinanceAPI
    
    logger.info("测试币安API...")
    api = BinanceAPI()
    
    # 测试获取24小时数据
    ticker = api.get_ticker_24h("ETHUSDT")
    assert ticker is not None
    assert "lastPrice" in ticker
    logger.success(f"ETH/USDT 价格: ${float(ticker['lastPrice']):.2f}")
    
    # 测试波动率计算
    volatility = api.calculate_volatility("ETHUSDT")
    assert volatility is not None
    logger.success(f"ETH波动率: {volatility:.4f}")
    
    logger.success("币安API测试通过")


def test_fear_greed_api():
    """测试恐惧贪婪指数API"""
    from src.tools.fear_greed_api import FearGreedAPI
    
    logger.info("测试恐惧贪婪指数API...")
    api = FearGreedAPI()
    
    # 测试获取当前指数
    current = api.get_current_index()
    assert current is not None
    assert "value" in current
    logger.success(f"当前恐惧贪婪指数: {current['value']} ({current['value_classification']})")
    
    # 测试分析
    analysis = api.analyze_sentiment()
    assert analysis is not None
    logger.success(f"情绪分析: {analysis['analysis']}")
    
    logger.success("恐惧贪婪指数API测试通过")


def test_market_agent():
    """测试市场Agent"""
    from src.models.schemas import AgentState
    from src.agents.market_agent import MarketAgent
    
    logger.info("测试市场Agent...")
    agent = MarketAgent()
    
    state = AgentState(query="分析ETH", symbol="ETH")
    result = agent.execute(state)
    
    assert result.market_data is not None
    logger.success(f"市场数据获取成功: {result.market_data.symbol}")
    logger.success("市场Agent测试通过")


def test_sentiment_agent():
    """测试情绪Agent"""
    from src.models.schemas import AgentState
    from src.agents.sentiment_agent import SentimentAgent
    
    logger.info("测试情绪Agent...")
    agent = SentimentAgent()
    
    state = AgentState(query="分析ETH", symbol="ETH")
    result = agent.execute(state)
    
    assert result.sentiment_data is not None
    logger.success(f"情绪数据获取成功: {result.sentiment_data.symbol}")
    logger.success("情绪Agent测试通过")


if __name__ == "__main__":
    logger.info("开始运行测试...")
    
    try:
        test_config()
        test_binance_api()
        test_fear_greed_api()
        test_market_agent()
        test_sentiment_agent()
        
        logger.success("所有测试通过！")
        
    except Exception as e:
        logger.error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()