"""
智能路由Agent - 用DeepSeek理解用户意图并动态决策
"""
import json
from typing import Dict, Any, List
from langchain_deepseek import ChatDeepSeek
from langchain.schema import HumanMessage, SystemMessage
from loguru import logger
from config.settings import settings


class SmartRouter:
    """智能路由器 - 根据用户输入决定执行什么操作"""
    
    def __init__(self):
        if not settings.DEEPSEEK_API_KEY:
            logger.warning("DeepSeek未配置，使用默认路由")
            self.llm = None
            return
            
        self.llm = ChatDeepSeek(
            model="deepseek-chat",
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
            temperature=0.1  # 低温度，保证路由决策稳定
        )
        logger.info("智能路由器初始化完成")
    
    def analyze_intent(self, query: str) -> Dict[str, Any]:
        """
        分析用户意图，返回需要执行的操作
        """
        if not self.llm:
            return self._default_route(query)
        
        prompt = f"""你是一个加密货币分析助手，请分析用户意图，返回JSON格式的操作指令。

    用户输入: "{query}"

    请返回JSON（只返回JSON，不要其他内容）:
    {{
        "symbols": ["币种1", "币种2"],
        "actions": ["操作1", "操作2"],
        "focus": "关注点",
        "is_comparison": false,
        "specific_question": "具体问题",
        "needs_deep_analysis": false
    }}

    重要规则:
    - symbols 必须从用户输入中提取，如果用户明确提到了币种名称或代号，请识别出来
    - 币种映射: BTC=比特币/Bitcoin, ETH=以太坊/Ethereum, SOL=Solana, BNB=Binance Coin, DOGE=狗狗币, XRP=瑞波, ADA=Cardano, AVAX=Avalanche, DOT=Polkadot, MATIC=Polygon
    - 如果用户没有提到任何币种，默认用 ["ETH"]
    - 如果用户问"现在买XX怎么样"，symbols应该是该币种

    操作说明:
    - market: 价格、涨跌幅、成交量
    - onchain: 大额转账、交易所资金流、Gas费
    - sentiment: 恐惧贪婪指数、市场情绪
    """
        
        try:
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            intent = json.loads(content.strip())
            logger.info(f"用户意图分析: {intent}")
            return intent
            
        except Exception as e:
            logger.error(f"意图分析失败: {e}")
            return self._default_route(query)


def _default_route(self, query: str) -> Dict[str, Any]:
    """默认路由（规则基础）"""
    query_upper = query.upper()
    
    # 更完整的币种关键词映射
    symbol_keywords = {
        "BTC": ["BTC", "BITCOIN", "比特币", "大饼", "比特"],
        "ETH": ["ETH", "ETHEREUM", "以太坊", "以太", "ETHEREUM"],
        "BNB": ["BNB", "BINANCE", "币安币", "币安"],
        "SOL": ["SOL", "SOLANA", "索拉纳"],
        "XRP": ["XRP", "RIPPLE", "瑞波"],
        "DOGE": ["DOGE", "DOGECOIN", "狗狗币", "狗币", "马斯克"],
        "ADA": ["ADA", "CARDANO", "艾达"],
        "AVAX": ["AVAX", "AVALANCHE"],
        "DOT": ["DOT", "POLKADOT", "波卡"],
        "MATIC": ["MATIC", "POLYGON"],
        "LINK": ["LINK", "CHAINLINK"],
        "UNI": ["UNI", "UNISWAP"],
    }
    
    # 按优先级识别（更具体的关键词优先）
    symbols = []
    for symbol, keywords in symbol_keywords.items():
        if any(kw in query_upper for kw in keywords):
            symbols.append(symbol)
    
    # 去重并保持顺序
    symbols = list(dict.fromkeys(symbols))
    
    if not symbols:
        symbols = ["ETH"]
    
    # 判断操作
    actions = []
    query_lower = query.lower()
    
    if any(w in query_lower for w in ["价格", "多少钱", "涨", "跌", "行情", "走势", "现在", "多少", "价"]):
        actions.append("market")
    if any(w in query_lower for w in ["转账", "链上", "巨鲸", "大户", "gas", "手续费", "大额"]):
        actions.append("onchain")
    if any(w in query_lower for w in ["情绪", "恐慌", "贪婪", "恐惧", "害怕", "疯狂"]):
        actions.append("sentiment")
    if any(w in query_lower for w in ["买", "卖", "投资", "建仓", "抄底", "入手", "怎么样", "如何", "能不能"]):
        actions.extend(["market", "sentiment"])  # 买/卖问题需要市场和情绪
    if any(w in query_lower for w in ["分析", "评估", "报告", "全面", "综合"]):
        actions = ["market", "onchain", "sentiment"]  # 全面分析
    
    # 去重
    actions = list(dict.fromkeys(actions))
    
    if not actions:
        actions = ["market", "onchain", "sentiment"]
    
    return {
        "symbols": symbols,
        "actions": actions,
        "focus": "general",
        "is_comparison": len(symbols) > 1,
        "specific_question": query,
        "needs_deep_analysis": len(actions) >= 2
    }
    def decide_next_action(self, current_state: Dict[str, Any]) -> str:
        """
        根据当前状态决定下一步操作
        
        Args:
            current_state: 当前状态
            
        Returns:
            下一步操作: "market"/"onchain"/"sentiment"/"done"
        """
        actions = current_state.get("actions", [])
        completed = current_state.get("completed_actions", [])
        
        for action in actions:
            if action not in completed:
                return action
        
        return "done"