"""
交互式命令行界面
支持多轮对话、历史记录、命令系统
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv()

from loguru import logger
from config.settings import settings
from src.utils.logger import setup_logger
from src.utils.display import StreamDisplay
from src.graph.smart_workflow import create_smart_workflow, SmartAgentState
from src.models.schemas import AgentState


class CryptoInsightCLI:
    """加密货币情报分析交互式CLI"""
    
    def __init__(self):
        """初始化CLI"""
        setup_logger(settings.LOG_LEVEL)
        self.display = StreamDisplay(delay=0.01)
        self.workflow = create_smart_workflow()
        self.history: List[Dict[str, Any]] = []
        self.current_symbol = "ETH"
        
    def clear_screen(self):
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_banner(self):
        """打印启动横幅"""
        self.clear_screen()
        print("""
╔══════════════════════════════════════════════════════════╗
║                                                         ║
║  🚀  Crypto Insight Agent  v1.0                        ║
║  基于 LangGraph + DeepSeek 的加密货币情报分析系统       ║
║                                                         ║
║  数据源: 币安 | Etherscan | 恐惧贪婪指数                 ║
║  AI引擎: DeepSeek                                      ║
║                                                         ║
╚══════════════════════════════════════════════════════════╝
""")
        
        # 显示API状态
        print("📡 API 状态检查")
        checks = [
            ("DeepSeek", settings.DEEPSEEK_API_KEY),
            ("币安", True),  # 公开API
            ("Etherscan", settings.ETHERSCAN_API_KEY),
            ("LangSmith", settings.LANGCHAIN_API_KEY),
        ]
        for name, configured in checks:
            status = "✅" if configured else "⚠️ 未配置"
            print(f"   {status}  {name}")
        
        print("\n💡 提示: 输入 'help' 查看所有命令")
        print("-" * 60)
    
    def print_help(self):
        """打印帮助信息"""
        print("""
📖 命令列表:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 分析命令:
   analyze <币种>      - 全面分析指定币种 (例: analyze ETH)
   price <币种>         - 快速查询价格 (例: price BTC)
   onchain <币种>       - 查看链上活动 (例: onchain ETH)
   sentiment            - 查看市场情绪
   compare <币种1> <币种2> - 对比两个币种 (例: compare ETH BTC)

📊 快捷命令:
   eth                  - 快速分析ETH
   btc                  - 快速分析BTC
   fear                 - 查看恐惧贪婪指数
   gas                  - 查看Gas价格

🛠️ 系统命令:
   help                 - 显示此帮助
   history              - 查看分析历史
   clear                - 清屏
   quit / exit / q      - 退出程序

💬 你也可以直接输入自然语言:
   "ETH最近怎么样？"
   "比特币有大额转账吗？"
   "现在市场恐慌吗？"
   "ETH和SOL哪个更值得投资？"
""")
    
    def print_history(self):
        """打印分析历史"""
        if not self.history:
            print("📝 暂无分析历史")
            return
        
        print(f"\n📝 分析历史 (最近{len(self.history)}条):")
        print("-" * 60)
        for i, record in enumerate(self.history[-10:], 1):
            timestamp = record.get('timestamp', '')
            query = record.get('query', '')
            symbol = record.get('symbol', '')
            risk = record.get('risk_score', 'N/A')
            print(f"  {i}. [{timestamp}] {query}")
            if symbol:
                print(f"     🪙 {symbol} 风险评分: {risk}")
    
    def extract_symbol(self, text: str) -> Optional[str]:
        """从文本中提取币种"""
        text_upper = text.upper()
        symbols_map = {
            "ETH": ["ETH", "ETHEREUM", "以太坊", "以太"],
            "BTC": ["BTC", "BITCOIN", "比特币", "大饼"],
            "BNB": ["BNB", "BINANCE", "币安"],
            "SOL": ["SOL", "SOLANA", "索拉纳"],
            "XRP": ["XRP", "RIPPLE", "瑞波"],
            "DOGE": ["DOGE", "DOGECOIN", "狗狗币"],
            "ADA": ["ADA", "CARDANO"],
            "AVAX": ["AVAX", "AVALANCHE"],
            "DOT": ["DOT", "POLKADOT"],
            "MATIC": ["MATIC", "POLYGON"],
        }
        
        for symbol, keywords in symbols_map.items():
            if any(kw in text_upper for kw in keywords):
                return symbol
        return None
    
    def run_analysis(self, query: str, symbol: str = None):
        """运行分析"""
        # 推断币种
        if not symbol:
            symbol = self.extract_symbol(query) or self.current_symbol
        
        self.current_symbol = symbol
        
        print(f"\n🔍 分析: {query}")
        print(f"🎯 目标币种: {symbol}")
        print("-" * 60)
        
        try:
            # 创建状态
            initial_state = SmartAgentState(
                query=query,
                symbol=symbol
            )
            
            config = {"configurable": {"thread_id": f"cli-{datetime.now().timestamp()}"}}
            
            # 执行工作流
            print("⏳ 正在分析...")
            result = self.workflow.invoke(initial_state, config)
            final_state = SmartAgentState(**result) if isinstance(result, dict) else result
            
            # 打印报告
            self.print_smart_report(final_state)
            
            # 保存历史
            self.history.append({
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "query": query,
                "symbol": symbol,
                "risk_score": final_state.report.risk_score if final_state.report else None,
                "summary": final_state.report.summary[:100] if final_state.report else ""
            })
            
        except Exception as e:
            self.display.print_error(f"分析失败: {e}")
            logger.error(f"分析失败: {e}")
    
    def print_smart_report(self, state: SmartAgentState):
        """打印智能报告"""
        if not state.report:
            print("❌ 报告生成失败")
            return
        
        report = state.report
        
        print("\n" + "=" * 60)
        
        # 风险评分带颜色
        risk_score = report.risk_score or 50
        if risk_score <= 30:
            risk_color = "🟢 低风险"
        elif risk_score <= 60:
            risk_color = "🟡 中等风险"
        else:
            risk_color = "🔴 高风险"
        
        print(f"📊 {report.symbol} 分析报告  {risk_color} ({risk_score:.0f}/100)")
        print("=" * 60)
        
        # 摘要
        print(f"\n📝 {report.summary}")
        
        # 根据执行的操作显示不同内容
        if "market" in state.actions_to_execute:
            print(f"\n📈 市场数据:")
            print(f"   {report.market_analysis}")
        
        if "onchain" in state.actions_to_execute:
            print(f"\n⛓️  链上数据:")
            print(f"   {report.onchain_analysis}")
        
        if "sentiment" in state.actions_to_execute:
            print(f"\n🎭 市场情绪:")
            print(f"   {report.sentiment_analysis}")
        
        print("\n" + "=" * 60)
    
    def quick_price(self, symbol: str):
        """快速查询价格"""
        query = f"{symbol}现在价格多少"
        state = SmartAgentState(query=query, symbol=symbol, actions_to_execute=["market"])
        # 只执行市场Agent
        from src.agents.market_agent import MarketAgent
        agent = MarketAgent()
        state = agent.execute(state)
        
        if state.market_data:
            md = state.market_data
            change_emoji = "📈" if md.price_change_24h > 0 else "📉"
            print(f"\n{change_emoji} {md.symbol}: ${md.current_price:.2f}")
            print(f"   24h涨跌: {md.price_change_24h:+.2f}%")
            print(f"   24h最高/最低: ${md.high_24h:.2f} / ${md.low_24h:.2f}")
            print(f"   24h成交量: {md.volume_24h:.2f}")
    
    def quick_sentiment(self):
        """快速查看情绪指数"""
        from src.tools.fear_greed_api import FearGreedAPI
        api = FearGreedAPI()
        data = api.analyze_sentiment()
        
        if data:
            value = data['value']
            label = data['value_classification']
            analysis = data['analysis']
            
            # 情绪颜色
            if value <= 25:
                emoji = "🔴"
            elif value <= 45:
                emoji = "🟠"
            elif value <= 55:
                emoji = "🟡"
            else:
                emoji = "🟢"
            
            print(f"\n{emoji} 恐惧贪婪指数: {value}/100 ({label})")
            print(f"   {analysis}")
    
    def quick_gas(self):
        """快速查看Gas价格"""
        from src.tools.etherscan_api import EtherscanAPI
        api = EtherscanAPI()
        gas = api.get_gas_oracle()
        
        if gas:
            print(f"\n⛽ ETH Gas 价格:")
            print(f"   慢速: {gas['safe_gas_price']} Gwei")
            print(f"   普通: {gas['propose_gas_price']} Gwei")
            print(f"   快速: {gas['fast_gas_price']} Gwei")
        else:
            print("\n⚠️  无法获取Gas价格")
    
    def run(self):
        """主循环"""
        self.print_banner()
        
        while True:
            try:
                # 获取用户输入
                user_input = input("\n💬 > ").strip()
                
                if not user_input:
                    continue
                
                # 处理命令
                cmd_lower = user_input.lower()
                
                # 退出命令
                if cmd_lower in ['quit', 'exit', 'q']:
                    print("\n👋 再见啦~")
                    break
                
                # 帮助
                elif cmd_lower == 'help':
                    self.print_help()
                
                # 历史
                elif cmd_lower == 'history':
                    self.print_history()
                
                # 清屏
                elif cmd_lower == 'clear':
                    self.clear_screen()
                    self.print_banner()
                
                # 快捷命令
                elif cmd_lower == 'eth':
                    self.run_analysis("全面分析ETH最近情况", "ETH")
                elif cmd_lower == 'btc':
                    self.run_analysis("全面分析BTC最近情况", "BTC")
                elif cmd_lower == 'fear':
                    self.quick_sentiment()
                elif cmd_lower == 'gas':
                    self.quick_gas()
                
                # 结构化命令
                elif cmd_lower.startswith('analyze '):
                    symbol = self.extract_symbol(cmd_lower) or cmd_lower.split()[-1].upper()
                    self.run_analysis(f"全面分析{symbol}", symbol)
                
                elif cmd_lower.startswith('price '):
                    symbol = cmd_lower.split()[-1].upper()
                    self.quick_price(symbol)
                
                elif cmd_lower.startswith('onchain '):
                    symbol = cmd_lower.split()[-1].upper()
                    self.run_analysis(f"查看{symbol}链上活动和大额转账", symbol)
                
                elif cmd_lower == 'sentiment':
                    self.quick_sentiment()
                
                elif cmd_lower.startswith('compare '):
                    parts = cmd_lower.split()
                    if len(parts) >= 3:
                        sym1, sym2 = parts[1].upper(), parts[2].upper()
                        self.run_analysis(f"对比分析{sym1}和{sym2}", sym1)
                
                # 自然语言查询
                else:
                    symbol = self.extract_symbol(user_input)
                    self.run_analysis(user_input, symbol)
                
            except KeyboardInterrupt:
                print("\n\n👋 再见啦~")
                break
            except Exception as e:
                self.display.print_error(f"错误: {e}")
                logger.error(f"CLI错误: {e}")


def main():
    """入口函数"""
    cli = CryptoInsightCLI()
    cli.run()


if __name__ == "__main__":
    main()