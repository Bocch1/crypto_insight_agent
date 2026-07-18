"""
链上数据Agent
负责获取和分析区块链链上数据
"""
from typing import Optional, List
from loguru import logger
from src.models.schemas import AgentState, OnchainData, AnomalyInfo
from src.tools.etherscan_api import EtherscanAPI
from src.agents.base import BaseAgent


class OnchainAgent(BaseAgent):
    """链上数据分析Agent"""
    
    def __init__(self):
        super().__init__(name="OnchainAgent")
        self.etherscan = EtherscanAPI()
        
        # 已知的交易所地址标签
        self.exchange_addresses = {
            "Binance": [
                "0x28C6c06298d514Db089934071355E5743bf21d60",  # Binance 14
                "0x21a31Ee1afC51d94C2eFcCAa2092aD1028285549",  # Binance 15
            ],
            "Coinbase": [
                "0x71660c4005BA85c37ccec55d0C4493E3Fe3e0fC1",  # Coinbase 10
            ]
        }
    
    def execute(self, state: AgentState) -> AgentState:
        """
        获取链上数据并检测异常
        
        Args:
            state: 当前状态
            
        Returns:
            更新后的状态
        """
        logger.info(f"链上Agent开始分析: {state.symbol}")
        
        try:
            # 获取链上数据
            onchain_data = self._fetch_onchain_data(state.symbol)
            if onchain_data:
                state.onchain_data = onchain_data
                
                # 检测异常
                anomalies = self._detect_anomalies(onchain_data)
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
                
                state.status = "onchain_data_collected"
                logger.success(f"链上数据采集完成: {state.symbol}")
            else:
                logger.warning(f"链上数据采集失败，可能API Key未配置: {state.symbol}")
                # 即使失败也继续，设置为降级模式
                state.onchain_data = OnchainData(
                    symbol=state.symbol or "ETH",
                    network="ethereum"
                )
                
        except Exception as e:
            logger.error(f"链上Agent执行失败: {e}")
            state = self.handle_error(state, e)
        
        return state
    
    def _fetch_onchain_data(self, symbol: Optional[str]) -> Optional[OnchainData]:
        """
        获取链上数据
        
        Args:
            symbol: 币种
            
        Returns:
            链上数据对象
        """
        if not self.etherscan.api_key:
            logger.warning("Etherscan API Key未配置，跳过链上数据获取")
            return None
        
        if not symbol:
            symbol = "ETH"
        
        # 去除USDT后缀
        if symbol.endswith("USDT"):
            symbol = symbol[:-4]
        
        try:
            onchain_data = OnchainData(
                symbol=symbol,
                network="ethereum"
            )
            
            # 1. 获取Gas价格
            gas_info = self.etherscan.get_gas_oracle()
            if gas_info:
                onchain_data.average_gas_price = gas_info["propose_gas_price"]
            
            # 2. 检测交易所大额转账
            large_transactions = []
            total_inflow = 0
            total_outflow = 0
            
            # 只检查第一个交易所地址作为示例
            exchange_name = "Binance"
            exchange_address = self.exchange_addresses[exchange_name][0]
            
            transactions = self.etherscan.get_normal_transactions(
                address=exchange_address,
                offset=20  # 最近20笔交易
            )
            
            if transactions:
                for tx in transactions:
                    value_eth = int(tx["value"]) / 10**18
                    
                    # 记录大额交易 (>100 ETH)
                    if value_eth > 100:
                        large_transactions.append({
                            "hash": tx["hash"],
                            "value": value_eth,
                            "from": tx["from"],
                            "to": tx["to"],
                            "timestamp": tx["timeStamp"]
                        })
                        
                        # 判断是流入还是流出
                        if tx["to"].lower() == exchange_address.lower():
                            total_inflow += value_eth
                        else:
                            total_outflow += value_eth
            
            onchain_data.large_transactions = large_transactions
            onchain_data.exchange_inflow = total_inflow
            onchain_data.exchange_outflow = total_outflow
            
            logger.info(
                f"链上数据分析: {len(large_transactions)}笔大额交易, "
                f"流入{total_inflow:.2f}ETH, 流出{total_outflow:.2f}ETH"
            )
            
            return onchain_data
            
        except Exception as e:
            logger.error(f"获取链上数据失败: {e}")
            return None
    
    def _detect_anomalies(self, onchain_data: OnchainData) -> list:
        """
        检测链上异常
        
        Args:
            onchain_data: 链上数据
            
        Returns:
            异常列表
        """
        anomalies = []
        
        # 1. 大额交易检测
        if len(onchain_data.large_transactions) > 5:
            anomalies.append(AnomalyInfo(
                type="large_transactions",
                severity="high",
                description=f"检测到{len(onchain_data.large_transactions)}笔大额交易(>100 ETH)",
                data_point={"transaction_count": len(onchain_data.large_transactions)}
            ))
        elif len(onchain_data.large_transactions) > 2:
            anomalies.append(AnomalyInfo(
                type="large_transactions",
                severity="medium",
                description=f"检测到{len(onchain_data.large_transactions)}笔大额交易(>100 ETH)",
                data_point={"transaction_count": len(onchain_data.large_transactions)}
            ))
        
        # 2. 交易所资金流向异常
        if onchain_data.exchange_inflow and onchain_data.exchange_outflow:
            net_flow = onchain_data.exchange_inflow - onchain_data.exchange_outflow
            
            if net_flow > 5000:
                anomalies.append(AnomalyInfo(
                    type="exchange_inflow",
                    severity="high",
                    description=f"交易所净流入{net_flow:.2f} ETH，可能存在抛压风险",
                    data_point={
                        "net_flow": net_flow,
                        "inflow": onchain_data.exchange_inflow,
                        "outflow": onchain_data.exchange_outflow
                    }
                ))
            elif net_flow > 1000:
                anomalies.append(AnomalyInfo(
                    type="exchange_inflow",
                    severity="medium",
                    description=f"交易所净流入{net_flow:.2f} ETH，注意监控",
                    data_point={"net_flow": net_flow}
                ))
        
        # 3. Gas价格异常
        if onchain_data.average_gas_price:
            if onchain_data.average_gas_price > 100:
                anomalies.append(AnomalyInfo(
                    type="high_gas_price",
                    severity="medium",
                    description=f"Gas价格{onchain_data.average_gas_price:.0f} Gwei，网络可能拥堵",
                    data_point={"gas_price": onchain_data.average_gas_price}
                ))
        
        if anomalies:
            logger.info(f"链上检测到{len(anomalies)}个异常")
        
        return anomalies