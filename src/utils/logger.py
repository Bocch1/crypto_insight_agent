"""
日志工具 - 配置 loguru
"""
import sys
from pathlib import Path
from loguru import logger


def setup_logger(level: str = "INFO", log_dir: str = "logs"):
    """
    配置日志系统
    
    Args:
        level: 日志级别 (DEBUG/INFO/WARNING/ERROR)
        log_dir: 日志目录
    """
    # 移除默认的 handler
    logger.remove()
    
    # 创建日志目录
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # 控制台输出
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=level,
        colorize=True
    )
    
    # 文件输出 (按日期轮转)
    logger.add(
        log_path / "crypto_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=level,
        rotation="1 day",
        retention="30 days",
        encoding="utf-8"
    )
    
    logger.info(f"日志系统初始化完成，日志级别: {level}")
    return logger