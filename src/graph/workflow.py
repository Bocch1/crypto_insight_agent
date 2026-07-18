"""
LangGraph工作流定义 - 编排多Agent协作流程
"""
from typing import Dict, Any
from loguru import logger
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from src.models.schemas import AgentState, AnalysisReport
from src.agents.market_agent import MarketAgent
from src.agents.onchain_agent import OnchainAgent
from src.agents.sentiment_agent import SentimentAgent
import os
from config.settings import settings

# 初始化Agents
market_agent = MarketAgent()
onchain_agent = OnchainAgent()
sentiment_agent = SentimentAgent()


def planner_node(state: AgentState) -> AgentState:
    """
    规划节点：解析用户查询，确定要分析的币种
    
    Args:
        state: 当前状态
        
    Returns:
        更新后的状态
    """
    logger.info("=" * 50)
    logger.info("规划节点开始执行")
    logger.info(f"用户查询: {state.query}")
    
    # 简单的币种识别逻辑
    query_upper = state.query.upper()
    
    # 识别常见币种
    crypto_symbols = {
        "BTC": ["BTC", "BITCOIN", "比特币", "大饼"],
        "ETH": ["ETH", "ETHEREUM", "以太坊", "以太"],
        "BNB": ["BNB", "BINANCE COIN", "币安"],
        "SOL": ["SOL", "SOLANA"],
        "XRP": ["XRP", "RIPPLE", "瑞波"],
        "DOGE": ["DOGE", "DOGECOIN", "狗狗币"],
    }
    
    detected_symbol = None
    for symbol, keywords in crypto_symbols.items():
        if any(keyword in query_upper for keyword in keywords):
            detected_symbol = symbol
            break
    
    # 默认分析ETH
    if not detected_symbol:
        logger.info("未识别特定币种，默认分析ETH")
        detected_symbol = "ETH"
    
    state.symbol = detected_symbol
    state.plan = [
        "market_data_collection",    # 采集市场数据
        "onchain_data_collection",   # 采集链上数据
        "sentiment_data_collection", # 采集情绪数据
        "generate_report"            # 生成分析报告
    ]
    state.current_step = "planning_complete"
    state.status = "planned"
    
    logger.info(f"识别币种: {state.symbol}")
    logger.info(f"执行计划: {' -> '.join(state.plan)}")
    
    return state


def market_node(state: AgentState) -> AgentState:
    """
    市场数据采集节点
    
    Args:
        state: 当前状态
        
    Returns:
        更新后的状态
    """
    logger.info("-" * 50)
    logger.info("市场数据采集节点开始执行")
    state.current_step = "market_data_collection"
    
    # 执行市场Agent
    state = market_agent.execute(state)
    
    return state


def onchain_node(state: AgentState) -> AgentState:
    """
    链上数据采集节点
    
    Args:
        state: 当前状态
        
    Returns:
        更新后的状态
    """
    logger.info("-" * 50)
    logger.info("链上数据采集节点开始执行")
    state.current_step = "onchain_data_collection"
    
    # 执行链上Agent
    state = onchain_agent.execute(state)
    
    return state


def sentiment_node(state: AgentState) -> AgentState:
    """
    情绪数据采集节点
    
    Args:
        state: 当前状态
        
    Returns:
        更新后的状态
    """
    logger.info("-" * 50)
    logger.info("情绪数据采集节点开始执行")
    state.current_step = "sentiment_data_collection"
    
    # 执行情绪Agent
    state = sentiment_agent.execute(state)
    
    return state


def report_node(state: AgentState) -> AgentState:
    """
    报告生成节点：使用DeepSeek综合分析并生成报告
    """
    logger.info("-" * 50)
    logger.info("报告生成节点开始执行")
    state.current_step = "generate_report"
    
    # 初始化DeepSeek分析器
    from src.tools.deepseek_analyzer import DeepSeekAnalyzer
    analyzer = DeepSeekAnalyzer()
    
    # 生成市场分析
    market_analysis = "暂无市场数据"
    if state.market_data:
        md = state.market_data
        # 先做规则基础分析
        basic_analysis = (
            f"{md.symbol}当前价格: ${md.current_price:.2f}\n"
            f"24小时涨跌幅: {md.price_change_24h:.2f}%\n"
            f"波动率: {md.volatility:.4f}\n"
            f"24小时成交量: {md.volume_24h:.2f}"
        )
        
        # 使用DeepSeek进行智能分析
        ai_analysis = analyzer.analyze_market_anomalies({
            "symbol": md.symbol,
            "current_price": md.current_price,
            "price_change_24h": md.price_change_24h,
            "high_24h": md.high_24h,
            "low_24h": md.low_24h,
            "volatility": md.volatility,
            "volume_24h": md.volume_24h
        })
        
        market_analysis = f"{basic_analysis}\n\n🤖 AI分析:\n{ai_analysis}"
    
    # 生成链上分析
    onchain_analysis = "暂无链上数据（请配置Etherscan API Key获取更全面的分析）"
    if state.onchain_data:
        od = state.onchain_data
        has_data = any([
            od.large_transactions,
            od.exchange_inflow is not None,
            od.average_gas_price is not None
        ])
        
        if has_data:
            basic_analysis = f"{od.symbol}链上数据:\n"
            if od.large_transactions:
                basic_analysis += f"大额交易: {len(od.large_transactions)}笔\n"
            if od.exchange_inflow is not None:
                net_flow = od.exchange_inflow - (od.exchange_outflow or 0)
                flow_direction = "净流入" if net_flow > 0 else "净流出"
                basic_analysis += f"交易所资金流向: {flow_direction} {abs(net_flow):.2f} ETH\n"
            
            ai_analysis = analyzer.analyze_onchain_anomalies({
                "network": od.network,
                "large_transactions": od.large_transactions,
                "exchange_inflow": od.exchange_inflow,
                "exchange_outflow": od.exchange_outflow,
                "average_gas_price": od.average_gas_price
            })
            
            onchain_analysis = f"{basic_analysis}\n\n🤖 AI分析:\n{ai_analysis}"
    
    # 生成情绪分析
    sentiment_analysis = "暂无情绪数据"
    if state.sentiment_data:
        sd = state.sentiment_data
        basic_analysis = f"{sd.symbol}市场情绪:\n"
        if sd.fear_greed_index is not None:
            basic_analysis += f"恐惧贪婪指数: {sd.fear_greed_index} ({sd.fear_greed_label})\n"
        
        ai_analysis = analyzer.analyze_sentiment({
            "fear_greed_index": sd.fear_greed_index,
            "fear_greed_label": sd.fear_greed_label,
            "social_volume_change": sd.social_volume_change
        })
        
        sentiment_analysis = f"{basic_analysis}\n\n🤖 AI分析:\n{ai_analysis}"
    
    # 使用DeepSeek生成综合报告
    ai_report = analyzer.generate_comprehensive_report(
        symbol=state.symbol or "ETH",
        market_analysis=market_analysis,
        onchain_analysis=onchain_analysis,
        sentiment_analysis=sentiment_analysis,
        anomalies=[a.model_dump() if hasattr(a, 'model_dump') else a for a in (state.report.anomalies if state.report else [])]
    )
    
    # 创建或更新报告
    if state.report:
        state.report.market_analysis = market_analysis
        state.report.onchain_analysis = onchain_analysis
        state.report.sentiment_analysis = sentiment_analysis
        state.report.summary = ai_report.get("summary", "分析完成")
        state.report.risk_score = ai_report.get("risk_score", 50)
    else:
        state.report = AnalysisReport(
            symbol=state.symbol or "ETH",
            summary=ai_report.get("summary", "分析完成"),
            market_analysis=market_analysis,
            onchain_analysis=onchain_analysis,
            sentiment_analysis=sentiment_analysis,
            risk_score=ai_report.get("risk_score", 50),
            anomalies=[]
        )
    
    state.status = "completed"
    logger.info("报告生成完成（含AI分析）")
    
    return state


def _calculate_risk_score(state: AgentState) -> float:
    """
    计算风险评分
    
    Args:
        state: 当前状态
        
    Returns:
        风险评分 (0-100)
    """
    base_score = 50.0  # 基础分
    
    # 根据异常数量和严重程度调整
    if state.report and state.report.anomalies:
        for anomaly in state.report.anomalies:
            if anomaly.severity == "high":
                base_score += 15
            elif anomaly.severity == "medium":
                base_score += 8
            elif anomaly.severity == "low":
                base_score += 3
    
    # 限制在0-100之间
    return max(0, min(100, base_score))


def _generate_summary(state: AgentState, risk_score: float) -> str:
    """
    生成综合摘要
    
    Args:
        state: 当前状态
        risk_score: 风险评分
        
    Returns:
        摘要文本
    """
    symbol = state.symbol or "ETH"
    
    if risk_score <= 30:
        risk_level = "低风险"
        advice = "市场整体稳定，适合观望或小额参与"
    elif risk_score <= 60:
        risk_level = "中等风险"
        advice = "存在一定风险因素，建议谨慎操作"
    else:
        risk_level = "高风险"
        advice = "多个风险指标触发，建议减少操作或等待信号明确"
    
    # 统计异常
    anomaly_count = 0
    if state.report and state.report.anomalies:
        anomaly_count = len(state.report.anomalies)
    
    summary = (
        f"{symbol}当前{risk_level}（评分 {risk_score:.0f}/100）。"
        f"检测到{anomaly_count}个异常信号。{advice}。"
        f"数据来源：币安市场数据、Etherscan链上数据、恐惧贪婪指数。"
    )
    
    return summary


def should_continue(state: AgentState) -> str:
    """
    判断是否需要继续执行
    
    Args:
        state: 当前状态
        
    Returns:
        下一个节点名称或END
    """
    # 如果错误太多，提前结束
    if state.error_count > 3:
        logger.warning(f"错误次数过多({state.error_count})，提前结束")
        return "generate_report"
    
    # 检查是否所有数据都已采集完成
    if state.market_data and state.onchain_data and state.sentiment_data:
        logger.info("所有数据采集完成，进入报告生成阶段")
        return "generate_report"
    
    # 按照计划继续执行
    if state.current_step == "planning_complete":
        return "market"
    elif state.current_step == "market_data_collected":
        return "onchain"
    elif state.current_step == "onchain_data_collected":
        return "sentiment"
    elif state.current_step == "sentiment_data_collected":
        return "generate_report"
    
    # 默认结束
    return END


def create_workflow():
    """
    创建LangGraph工作流
    
    Returns:
        编译后的工作流
    """
    
    # 激活LangSmith追踪
    if settings.LANGCHAIN_API_KEY:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
        os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT
        logger.info("LangSmith追踪已启用")
    
    logger.info("创建LangGraph工作流")
    
    # 创建状态图
    workflow = StateGraph(AgentState)
    
    # 添加节点（注意：节点名不能和状态字段名重复）
    workflow.add_node("planner", planner_node)
    workflow.add_node("market", market_node)
    workflow.add_node("onchain", onchain_node)
    workflow.add_node("sentiment", sentiment_node)
    workflow.add_node("generate_report", report_node)
    
    # 设置入口
    workflow.set_entry_point("planner")
    
    # 添加条件边
    workflow.add_conditional_edges(
        "planner",
        should_continue,
        {
            "market": "market",
            "onchain": "onchain",
            "sentiment": "sentiment",
            "generate_report": "generate_report",
            END: END
        }
    )
    
    # 各数据采集节点完成后进入下一步
    workflow.add_edge("market", "onchain")
    workflow.add_edge("onchain", "sentiment")
    workflow.add_edge("sentiment", "generate_report")
    
    # 报告生成后结束
    workflow.add_edge("generate_report", END)
    
    # 编译（带记忆功能）
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    logger.info("工作流创建完成")
    
    return app