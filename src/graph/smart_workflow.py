"""
智能工作流 - 根据用户意图动态执行
"""
from typing import Dict, Any, List
from loguru import logger
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage

from src.models.schemas import AgentState, MarketData, OnchainData, SentimentData, AnalysisReport, AnomalyInfo
from src.agents.market_agent import MarketAgent
from src.agents.onchain_agent import OnchainAgent
from src.agents.sentiment_agent import SentimentAgent
from src.agents.smart_router import SmartRouter
from src.tools.deepseek_analyzer import DeepSeekAnalyzer


# 初始化
router = SmartRouter()
market_agent = MarketAgent()
onchain_agent = OnchainAgent()
sentiment_agent = SentimentAgent()
deepseek = DeepSeekAnalyzer()


class SmartAgentState(AgentState):
    """增强版Agent状态"""
    # 路由相关
    intent: Dict[str, Any] = {}
    actions_to_execute: List[str] = []
    completed_actions: List[str] = []
    all_symbols: List[str] = []
    current_symbol_index: int = 0
    is_comparison: bool = False
    specific_question: str = ""  # 设置默认空字符串


def router_node(state: SmartAgentState) -> SmartAgentState:
    """
    智能路由节点 - 分析用户意图
    """
    logger.info("=" * 60)
    logger.info(f"🧠 智能路由分析用户意图: {state.query}")
    
    # 分析意图
    intent = router.analyze_intent(state.query)
    
    state.intent = intent
    state.actions_to_execute = intent.get("actions", ["market", "onchain", "sentiment"])
    state.all_symbols = intent.get("symbols", ["ETH"])
    state.is_comparison = intent.get("is_comparison", False)
    # 修复：确保 specific_question 不为 None
    state.specific_question = intent.get("specific_question") or state.query
    state.symbol = state.all_symbols[0]
    state.current_symbol_index = 0
    state.completed_actions = []
    
    logger.info(f"意图: 分析{state.all_symbols}, 操作:{state.actions_to_execute}")
    logger.info(f"对比模式: {state.is_comparison}, 问题: {state.specific_question}")
    
    return state


def dynamic_market_node(state: SmartAgentState) -> SmartAgentState:
    """动态市场数据节点"""
    if "market" not in state.actions_to_execute:
        logger.info("⏭️  跳过市场数据（用户不需要）")
        state.completed_actions.append("market")
        return state
    
    logger.info(f"📈 获取{state.symbol}市场数据")
    state = market_agent.execute(state)
    state.completed_actions.append("market")
    
    return state


def dynamic_onchain_node(state: SmartAgentState) -> SmartAgentState:
    """动态链上数据节点"""
    if "onchain" not in state.actions_to_execute:
        logger.info("⏭️  跳过链上数据（用户不需要）")
        state.completed_actions.append("onchain")
        return state
    
    logger.info(f"⛓️  获取{state.symbol}链上数据")
    state = onchain_agent.execute(state)
    state.completed_actions.append("onchain")
    
    return state


def dynamic_sentiment_node(state: SmartAgentState) -> SmartAgentState:
    """动态情绪数据节点"""
    if "sentiment" not in state.actions_to_execute:
        logger.info("⏭️  跳过情绪数据（用户不需要）")
        state.completed_actions.append("sentiment")
        return state
    
    logger.info(f"🎭 获取{state.symbol}情绪数据")
    state = sentiment_agent.execute(state)
    state.completed_actions.append("sentiment")
    
    return state


def smart_report_node(state: SmartAgentState) -> SmartAgentState:
    """智能报告节点"""
    logger.info("📝 生成针对性报告")
    
    # 构建上下文
    context = f"用户问题: {state.specific_question}\n\n"
    
    if state.market_data:
        md = state.market_data
        context += f"市场数据: {md.symbol}价格${md.current_price:.2f}, 24h涨跌{md.price_change_24h:.2f}%, 波动率{md.volatility:.4f}\n"
    
    if state.onchain_data:
        od = state.onchain_data
        context += f"链上数据: 大额交易{len(od.large_transactions)}笔, 交易所净流入{od.exchange_inflow or 0:.2f}ETH\n"
    
    if state.sentiment_data:
        sd = state.sentiment_data
        context += f"情绪数据: 恐惧贪婪指数{sd.fear_greed_index}({sd.fear_greed_label})\n"
    
    # 用DeepSeek生成回答
    try:
        if deepseek.llm:
            prompt = f"""根据以下数据回答用户问题。直接简洁回答，不需要格式化。
{context}

请回答用户的问题: {state.specific_question}"""
            
            messages = [HumanMessage(content=prompt)]
            response = deepseek.llm.invoke(messages)
            summary = response.content
        else:
            summary = f"{state.symbol}分析完成。"
    except Exception as e:
        logger.error(f"DeepSeek回答生成失败: {e}")
        summary = f"{state.symbol}分析完成。"
    
    # 生成各维度分析文本
    market_analysis = "未获取市场数据"
    if state.market_data:
        md = state.market_data
        market_analysis = f"价格: ${md.current_price:.2f}, 24h涨跌: {md.price_change_24h:.2f}%, 波动率: {md.volatility:.4f}"
    
    onchain_analysis = "未获取链上数据"
    if state.onchain_data:
        od = state.onchain_data
        onchain_analysis = f"大额交易: {len(od.large_transactions)}笔, Gas: {od.average_gas_price or 'N/A'} Gwei"
    
    sentiment_analysis = "未获取情绪数据"
    if state.sentiment_data:
        sd = state.sentiment_data
        sentiment_analysis = f"恐惧贪婪指数: {sd.fear_greed_index} ({sd.fear_greed_label})"
    
    # 计算风险评分
    risk_score = 50
    if state.report and state.report.anomalies:
        for a in state.report.anomalies:
            severity = a.get('severity', 'low') if isinstance(a, dict) else a.severity
            if severity == "high":
                risk_score += 15
            elif severity == "medium":
                risk_score += 8
    
    state.report = AnalysisReport(
        symbol=state.symbol or "ETH",
        summary=summary,
        market_analysis=market_analysis,
        onchain_analysis=onchain_analysis,
        sentiment_analysis=sentiment_analysis,
        risk_score=min(100, risk_score),
        anomalies=state.report.anomalies if state.report else []
    )
    
    state.status = "completed"
    logger.info("智能报告生成完成")
    
    return state


def route_next(state: SmartAgentState) -> str:
    """
    智能路由：决定下一步执行什么
    """
    # 按顺序检查需要执行的操作
    action_order = ["market", "onchain", "sentiment"]
    
    for action in action_order:
        if action in state.actions_to_execute and action not in state.completed_actions:
            return action
    
    # 所有操作完成
    return "generate_report"


def create_smart_workflow():
    """创建智能工作流"""
    logger.info("创建智能工作流")
    
    workflow = StateGraph(SmartAgentState)
    
    # 添加节点
    workflow.add_node("router", router_node)
    workflow.add_node("market", dynamic_market_node)
    workflow.add_node("onchain", dynamic_onchain_node)
    workflow.add_node("sentiment", dynamic_sentiment_node)
    workflow.add_node("generate_report", smart_report_node)
    
    # 设置入口
    workflow.set_entry_point("router")
    
    # 路由节点根据意图分发到第一个需要执行的操作
    workflow.add_conditional_edges(
        "router",
        route_next,
        {
            "market": "market",
            "onchain": "onchain",
            "sentiment": "sentiment",
            "generate_report": "generate_report"
        }
    )
    
    # 每个操作完成后回到路由判断
    workflow.add_conditional_edges("market", route_next, {
        "onchain": "onchain", "sentiment": "sentiment", "generate_report": "generate_report"
    })
    workflow.add_conditional_edges("onchain", route_next, {
        "sentiment": "sentiment", "generate_report": "generate_report"
    })
    workflow.add_conditional_edges("sentiment", route_next, {
        "generate_report": "generate_report"
    })
    
    # 报告节点结束
    workflow.add_edge("generate_report", END)
    
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    logger.info("智能工作流创建完成")
    return app
