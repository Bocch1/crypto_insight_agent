"""
DeepSeek AI 分析器 - 用AI替代规则引擎进行智能分析和报告生成
"""
from typing import Optional, Dict, Any
from langchain_openai import ChatOpenAI  # 改用 ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from loguru import logger
from config.settings import settings


class DeepSeekAnalyzer:
    """DeepSeek 智能分析器"""
    
    def __init__(self):
        if not settings.DEEPSEEK_API_KEY:
            logger.warning("DeepSeek API Key未配置，将使用基础规则分析")
            self.llm = None
            return
            
        self.llm = ChatOpenAI(
            model="deepseek-chat",
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL or "https://api.deepseek.com/v1",
            temperature=0.3,
            max_tokens=2000
        )
        logger.info("DeepSeek 分析器初始化完成")
    
    # ... 其余方法保持不变
    
    def analyze_market_anomalies(self, market_data: Dict[str, Any]) -> str:
        """
        AI分析市场数据异常
        
        Args:
            market_data: 市场数据字典
            
        Returns:
            AI分析结果
        """
        if not self.llm:
            return self._rule_based_market_analysis(market_data)
        
        prompt = f"""你是一个专业的加密货币分析师。请分析以下市场数据，识别异常信号并给出专业见解。

市场数据:
- 交易对: {market_data.get('symbol')}
- 当前价格: ${market_data.get('current_price', 0):.2f}
- 24小时涨跌: {market_data.get('price_change_24h', 0):.2f}%
- 24小时最高: ${market_data.get('high_24h', 0):.2f}
- 24小时最低: ${market_data.get('low_24h', 0):.2f}
- 波动率: {market_data.get('volatility', 0):.4f}
- 24小时成交量: {market_data.get('volume_24h', 0):.2f}

请分析：
1. 价格走势是否异常？
2. 波动率是否处于危险水平？
3. 成交量是否配合价格走势？
4. 综合风险评估（低/中/高）

请用中文回答，简洁专业。"""
        
        try:
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"DeepSeek市场分析失败: {e}")
            return self._rule_based_market_analysis(market_data)
    
    def analyze_onchain_anomalies(self, onchain_data: Dict[str, Any]) -> str:
        """
        AI分析链上数据异常
        
        Args:
            onchain_data: 链上数据字典
            
        Returns:
            AI分析结果
        """
        if not self.llm:
            return self._rule_based_onchain_analysis(onchain_data)
        
        prompt = f"""你是一个区块链数据分析专家。请分析以下链上数据，识别潜在风险。

链上数据:
- 网络: {onchain_data.get('network', 'ethereum')}
- 大额交易笔数: {len(onchain_data.get('large_transactions', []))}
- 交易所净流入: {onchain_data.get('exchange_inflow', 0):.2f} ETH
- 交易所净流出: {onchain_data.get('exchange_outflow', 0):.2f} ETH
- Gas价格: {onchain_data.get('average_gas_price', 'N/A')} Gwei

请分析：
1. 大额交易是否异常？
2. 交易所资金流向是否暗示抛压/吸筹？
3. Gas价格是否反映网络拥堵？
4. 综合链上风险评估

请用中文回答，简洁专业。"""
        
        try:
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"DeepSeek链上分析失败: {e}")
            return self._rule_based_onchain_analysis(onchain_data)
    
    def analyze_sentiment(self, sentiment_data: Dict[str, Any]) -> str:
        """
        AI分析市场情绪
        
        Args:
            sentiment_data: 情绪数据字典
            
        Returns:
            AI分析结果
        """
        if not self.llm:
            return self._rule_based_sentiment_analysis(sentiment_data)
        
        prompt = f"""你是一个市场心理学专家。请分析当前加密货币市场情绪。

情绪数据:
- 恐惧贪婪指数: {sentiment_data.get('fear_greed_index', 'N/A')} 
- 情绪标签: {sentiment_data.get('fear_greed_label', 'N/A')}
- 7天情绪变化: {sentiment_data.get('social_volume_change', 0):.1f}%

请分析：
1. 当前市场情绪处于什么阶段？
2. 情绪变化趋势是否值得关注？
3. 对投资者的建议

请用中文回答，简洁专业。"""
        
        try:
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"DeepSeek情绪分析失败: {e}")
            return self._rule_based_sentiment_analysis(sentiment_data)
    
    def generate_comprehensive_report(
        self,
        symbol: str,
        market_analysis: str,
        onchain_analysis: str,
        sentiment_analysis: str,
        anomalies: list
    ) -> Dict[str, Any]:
        """
        AI生成综合分析报告
        """
        if not self.llm:
            return self._rule_based_report(symbol, anomalies)
        
        # 格式化异常信息
        anomaly_text = "无异常"
        if anomalies:
            anomaly_items = []
            for a in anomalies:
                if isinstance(a, dict):
                    severity = a.get('severity', 'low')
                    description = a.get('description', '未知异常')
                else:
                    severity = a.severity
                    description = a.description
                
                severity_map = {"high": "🔴高", "medium": "🟡中", "low": "🟢低"}
                severity_str = severity_map.get(severity, "⚪未知")
                anomaly_items.append(f"- [{severity_str}] {description}")
            anomaly_text = "\n".join(anomaly_items)
        
        prompt = f"""你是一个资深加密货币投资顾问。请基于以下多维数据生成一份专业的投资分析报告。

分析币种: {symbol}

【市场数据分析】
{market_analysis}

【链上数据分析】
{onchain_analysis}

【市场情绪分析】
{sentiment_analysis}

【检测到的异常信号】
{anomaly_text}

请生成一份简洁专业的报告，包含：
1. 综合总结（2-3句话）
2. 风险评分（0-100的整数）
3. 风险等级（低风险/中等风险/高风险）
4. 关键发现
5. 操作建议

请用JSON格式返回，包含字段: summary, risk_score, risk_level, key_findings, advice"""

        try:
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            
            import json
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            result = json.loads(content.strip())
            logger.success("DeepSeek报告生成完成")
            return result
            
        except Exception as e:
            logger.error(f"DeepSeek报告生成失败: {e}")
            return self._rule_based_report(symbol, anomalies)
    
    # === 规则基础的备用方案 ===
    
    def _rule_based_market_analysis(self, data: Dict[str, Any]) -> str:
        """规则基础的市场分析"""
        change = data.get('price_change_24h', 0)
        volatility = data.get('volatility', 0)
        
        analysis = []
        if abs(change) > 10:
            analysis.append(f"24小时价格剧烈波动{change:.2f}%，属于异常行为")
        elif abs(change) > 5:
            analysis.append(f"24小时价格波动{change:.2f}%，波动较大")
        else:
            analysis.append(f"24小时价格变化{change:.2f}%，走势平稳")
        
        if volatility and volatility > 0.05:
            analysis.append(f"当前波动率{volatility:.4f}处于较高水平")
        
        return "。".join(analysis) if analysis else "市场数据正常"
    
    def _rule_based_onchain_analysis(self, data: Dict[str, Any]) -> str:
        """规则基础的链上分析"""
        tx_count = len(data.get('large_transactions', []))
        net_flow = data.get('exchange_inflow', 0) - data.get('exchange_outflow', 0)
        
        analysis = []
        if tx_count > 5:
            analysis.append(f"检测到{tx_count}笔大额交易，链上活动频繁")
        elif tx_count > 0:
            analysis.append(f"检测到{tx_count}笔大额交易")
        else:
            analysis.append("未检测到显著大额交易")
        
        if net_flow > 1000:
            analysis.append(f"交易所净流入{net_flow:.2f} ETH，可能存在抛压")
        
        return "。".join(analysis) if analysis else "链上数据正常"
    
    def _rule_based_sentiment_analysis(self, data: Dict[str, Any]) -> str:
        """规则基础的情绪分析"""
        index = data.get('fear_greed_index', 50)
        
        if index <= 25:
            return "市场处于极度恐惧状态，可能超卖"
        elif index <= 45:
            return "市场情绪偏谨慎，投资者避险情绪较浓"
        elif index <= 55:
            return "市场情绪中性"
        elif index <= 75:
            return "市场情绪偏乐观，贪婪情绪上升"
        else:
            return "市场处于极度贪婪状态，注意回调风险"
    
    def _rule_based_report(self, symbol: str, anomalies: list) -> Dict[str, Any]:
        """规则基础的报告生成"""
        risk_score = 50
        for a in anomalies:
            if isinstance(a, dict):
                severity = a.get('severity', 'low')
            else:
                severity = a.severity
                
            if severity == "high":
                risk_score += 15
            elif severity == "medium":
                risk_score += 8
        
        risk_score = min(100, risk_score)
        
        if risk_score <= 30:
            risk_level = "低风险"
        elif risk_score <= 60:
            risk_level = "中等风险"
        else:
            risk_level = "高风险"
        
        return {
            "summary": f"{symbol}当前{risk_level}，风险评分{risk_score}/100",
            "risk_score": risk_score,
            "risk_level": risk_level,
            "key_findings": f"检测到{len(anomalies)}个异常信号",
            "advice": "建议根据个人风险承受能力决策"
        }