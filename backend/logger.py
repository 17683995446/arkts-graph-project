
import logging
import sys
from datetime import datetime
import os
from typing import Any

# 全局日志追踪器
LOG_TRACKER = {
    "functions_calls": 0,
    "errors": 0,
    "warnings": 0,
    "branches": {}
}

# 日志格式
LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)-15s | %(funcName)-30s | %(message)s"
)

# 创建 logger
def setup_logger(name: str = "arkts-graph", level: int = logging.DEBUG) -> logging.Logger:
    """设置详细日志系统"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False  # 防止重复打印

    if not logger.handlers:
        # 控制台 handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(console_handler)

    return logger


# 装饰器：追踪函数执行
def log_execution(func):
    """装饰器，详细追踪函数执行"""
    def wrapper(*args, **kwargs):
        global LOG_TRACKER
        logger = logging.getLogger("arkts-graph")
        
        func_name = f"{func.__module__}.{func.__name__}"
        
        LOG_TRACKER["functions_calls"] += 1
        if func_name not in LOG_TRACKER["branches"]:
            LOG_TRACKER["branches"][func_name] = {"called": 0, "errors": 0}
        
        LOG_TRACKER["branches"][func_name]["called"] += 1
        
        logger.debug(f"▶️  开始执行 [参数: args={len(args)}, kwargs={list(kwargs.keys())}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"✅  执行成功")
            return result
        except Exception as e:
            LOG_TRACKER["errors"] += 1
            LOG_TRACKER["branches"][func_name]["errors"] += 1
            logger.error(f"❌ 执行异常: {type(e).__name__}: {str(e)}")
            import traceback
            logger.error(f"📋 堆栈:\n{traceback.format_exc()}")
            raise
    return wrapper


def log_branch(branch_name: str, condition: Any = None):
    """记录分支执行"""
    global LOG_TRACKER
    logger = logging.getLogger("arkts-graph")
    
    if condition is not None:
        logger.debug(f"🔀  分支 [{branch_name}], 条件: {condition}")
    else:
        logger.debug(f"🔀  分支 [{branch_name}]")


def log_warning(message: str):
    """记录警告"""
    global LOG_TRACKER
    LOG_TRACKER["warnings"] += 1
    logger = logging.getLogger("arkts-graph")
    logger.warning(f"⚠️  {message}")


def print_execution_summary():
    """打印执行统计汇总"""
    global LOG_TRACKER
    logger = logging.getLogger("arkts-graph")
    logger.info("=" * 80)
    logger.info("📊  执行统计汇总")
    logger.info("=" * 80)
    logger.info(f"  函数调用数: {LOG_TRACKER['functions_calls']}")
    logger.info(f"  错误数: {LOG_TRACKER['errors']}")
    logger.info(f"  警告数: {LOG_TRACKER['warnings']}")
    logger.info(f"  分支统计:")
    for func_name, stats in LOG_TRACKER['branches'].items():
        logger.info(f"    - {func_name}: called={stats['called']}, errors={stats['errors']}")
    logger.info("=" * 80)
