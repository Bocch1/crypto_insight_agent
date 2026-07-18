"""
Crypto Insight Agent - 主程序入口
支持命令行模式和交互模式
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Crypto Insight Agent - 加密货币多维情报分析系统"
    )
    parser.add_argument(
        "--query", "-q",
        type=str,
        help="单次分析查询"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        default=True,
        help="进入交互模式（默认）"
    )
    parser.add_argument(
        "--symbol", "-s",
        type=str,
        default="ETH",
        help="分析的币种，默认ETH"
    )
    
    args = parser.parse_args()
    
    if args.query:
        # 单次查询模式
        from src.graph.smart_workflow import create_smart_workflow, SmartAgentState
        from src.utils.logger import setup_logger
        from config.settings import settings
        
        setup_logger(settings.LOG_LEVEL)
        
        workflow = create_smart_workflow()
        state = SmartAgentState(query=args.query, symbol=args.symbol)
        
        print(f"🔍 分析: {args.query}")
        result = workflow.invoke(state)
        
        if isinstance(result, dict):
            final_state = SmartAgentState(**result)
        else:
            final_state = result
            
        if final_state.report:
            print(f"\n📊 {final_state.report.symbol} 分析报告")
            print(f"风险评分: {final_state.report.risk_score:.0f}/100")
            print(f"\n{final_state.report.summary}")
    else:
        # 交互模式
        from src.interactive import CryptoInsightCLI
        cli = CryptoInsightCLI()
        cli.run()


if __name__ == "__main__":
    main()