"""
Etherscan API封装 V2
提供以太坊链上数据查询
"""
from typing import Optional, Dict, Any, List
import requests
from loguru import logger
from config.settings import settings
from src.utils.retry import retry_with_backoff


class EtherscanAPI:
    """Etherscan API V2 客户端"""
    
    # V2 API 端点
    BASE_URL = "https://api.etherscan.io/v2/api"
    
    def __init__(self):
        self.api_key = settings.ETHERSCAN_API_KEY
        self.timeout = settings.REQUEST_TIMEOUT
        
        if not self.api_key:
            logger.warning("Etherscan API Key未设置，链上数据查询将不可用")
        else:
            logger.info("Etherscan API V2 客户端初始化完成")
    
    def _make_request(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        发送API请求（V2格式）
        
        Args:
            params: 请求参数
            
        Returns:
            API响应数据
        """
        try:
            # V2 API 需要在URL中添加chain-id，参数中需要apikey
            url = f"{self.BASE_URL}?chainid=1"  # 1 = Ethereum Mainnet
            
            # 添加API Key
            params["apikey"] = self.api_key
            
            headers = {
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Etherscan API V2请求失败: {e}")
            raise
    
    @retry_with_backoff(max_attempts=3)
    def get_eth_balance(self, address: str) -> Optional[float]:
        """
        查询地址ETH余额
        
        Args:
            address: 以太坊地址
            
        Returns:
            ETH余额
        """
        params = {
            "module": "account",
            "action": "balance",
            "address": address,
            "tag": "latest"
        }
        
        data = self._make_request(params)
        if data and data.get("status") == "1":
            # 转换为ETH (1 ETH = 10^18 wei)
            balance_wei = int(data["result"])
            balance_eth = balance_wei / 10**18
            logger.debug(f"地址{address[:10]}...余额: {balance_eth:.4f} ETH")
            return balance_eth
        
        logger.warning(f"获取地址余额失败: {data.get('message', 'Unknown error') if data else 'No response'}")
        return None
    
    @retry_with_backoff(max_attempts=3)
    def get_normal_transactions(
        self, 
        address: str,
        start_block: int = 0,
        end_block: int = 99999999,
        page: int = 1,
        offset: int = 10,
        sort: str = "desc"
    ) -> Optional[List[Dict[str, Any]]]:
        """
        查询地址普通交易记录（V2）
        
        Args:
            address: 以太坊地址
            start_block: 起始区块
            end_block: 结束区块
            page: 页码
            offset: 每页数量
            sort: 排序方式
            
        Returns:
            交易记录列表
        """
        params = {
            "module": "account",
            "action": "txlist",
            "address": address,
            "startblock": start_block,
            "endblock": end_block,
            "page": page,
            "offset": offset,
            "sort": sort
        }
        
        data = self._make_request(params)
        if data and data.get("status") == "1":
            transactions = data.get("result", [])
            logger.debug(f"获取地址{address[:10]}...交易: {len(transactions)}笔")
            return transactions
        
        logger.warning(f"获取交易记录失败: {data.get('message', 'Unknown error') if data else 'No response'}")
        return None
    
    @retry_with_backoff(max_attempts=3)
    def get_latest_block(self) -> Optional[int]:
        """
        获取最新区块号
        
        Returns:
            最新区块号
        """
        params = {
            "module": "proxy",
            "action": "eth_blockNumber"
        }
        
        data = self._make_request(params)
        if data and data.get("result"):
            block_number = int(data["result"], 16)
            logger.debug(f"最新区块号: {block_number}")
            return block_number
        
        return None
    
    @retry_with_backoff(max_attempts=3)
    def get_gas_oracle(self) -> Optional[Dict[str, float]]:
        """
        获取Gas价格预言
        
        Returns:
            Gas价格信息
        """
        params = {
            "module": "gastracker",
            "action": "gasoracle"
        }
        
        data = self._make_request(params)
        if data and data.get("status") == "1":
            result = data["result"]
            gas_info = {
                "safe_gas_price": float(result.get("SafeGasPrice", 0)),
                "propose_gas_price": float(result.get("ProposeGasPrice", 0)),
                "fast_gas_price": float(result.get("FastGasPrice", 0)),
            }
            logger.debug(f"Gas价格: {gas_info}")
            return gas_info
        
        logger.warning(f"获取Gas价格失败: {data.get('message', 'Unknown error') if data else 'No response'}")
        return None
    
    @retry_with_backoff(max_attempts=3)
    def get_token_transactions(
        self,
        address: str,
        page: int = 1,
        offset: int = 10,
        sort: str = "desc"
    ) -> Optional[List[Dict[str, Any]]]:
        """
        查询地址ERC20代币交易记录
        
        Args:
            address: 以太坊地址
            page: 页码
            offset: 每页数量
            sort: 排序方式
            
        Returns:
            代币交易记录列表
        """
        params = {
            "module": "account",
            "action": "tokentx",
            "address": address,
            "page": page,
            "offset": offset,
            "sort": sort
        }
        
        data = self._make_request(params)
        if data and data.get("status") == "1":
            transactions = data.get("result", [])
            logger.debug(f"获取地址{address[:10]}...代币交易: {len(transactions)}笔")
            return transactions
        
        return None