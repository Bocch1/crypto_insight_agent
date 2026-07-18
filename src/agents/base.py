"""
Agent基类
"""
from typing import Optional
from loguru import logger
from src.models.schemas import AgentState


class BaseAgent:
    """所有Agent的基类"""
    
    def __init__(self, name: str = "BaseAgent"):
        self.name = name
        logger.info(f"初始化Agent: {name}")
    
    def execute(self, state: AgentState) -> AgentState:
        """
        执行Agent逻辑
        
        Args:
            state: 当前工作流状态
            
        Returns:
            更新后的状态
        """
        logger.info(f"{self.name} 开始执行")
        return state
    
    def handle_error(self, state: AgentState, error: Exception) -> AgentState:
        """
        错误处理
        
        Args:
            state: 当前状态
            error: 异常信息
            
        Returns:
            更新后的状态
        """
        logger.error(f"{self.name} 执行出错: {error}")
        state.error_count += 1
        state.status = f"error: {str(error)}"
        return state