
import logging
import sys
import inspect
import time
from datetime import datetime
from typing import Any, Callable

# 全局计数器
LOG_STATS = {
    "total_lines": 0,
    "functions_called": 0,
    "branches_taken": {},
    "errors_occurred": 0,
    "start_time": time.time()
}

def setup_detailed_logger(name="arkts_detailed", level=logging.DEBUG):
    """设置超级详细的日志系统"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False
    
    if not logger.handlers:
        # 详细格式
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)-20s | %(lineno)-4d | %(message)s"
        )
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger

# 全局logger实例
DETAILED_LOGGER = setup_detailed_logger()


def log_line(msg: str = ""):
    """记录一行代码的执行"""
    LOG_STATS["total_lines"] += 1
    caller_frame = inspect.currentframe().f_back
    caller_info = inspect.getframeinfo(caller_frame)
    func_name = caller_info.function
    line_num = caller_info.lineno
    filename = caller_info.filename.split("/")[-1]
    
    DETAILED_LOGGER.debug(f"[{filename}:{func_name}:{line_num}] {msg}")


def log_func_entry(func_name: str, *args, **kwargs):
    """记录函数入口"""
    LOG_STATS["functions_called"] += 1
    LOG_STATS["branches_taken"][func_name] = LOG_STATS["branches_taken"].get(func_name, 0) + 1
    DETAILED_LOGGER.info(f"=== ENTER {func_name} ===")
    DETAILED_LOGGER.debug(f"  Args: {len(args)}, Kwargs: {list(kwargs.keys())}")


def log_func_exit(func_name: str, result=None):
    """记录函数出口"""
    DETAILED_LOGGER.info(f"=== EXIT {func_name} ===")


def log_branch(branch_name: str, condition: Any = None):
    """记录分支执行"""
    if branch_name not in LOG_STATS["branches_taken"]:
        LOG_STATS["branches_taken"][branch_name] = 0
    LOG_STATS["branches_taken"][branch_name] += 1
    
    if condition is not None:
        DETAILED_LOGGER.debug(f"  分支: {branch_name}, 条件: {condition}")
    else:
        DETAILED_LOGGER.debug(f"  分支: {branch_name}")


def log_warning(msg: str):
    """记录警告"""
    LOG_STATS["errors_occurred"] += 1
    DETAILED_LOGGER.warning(f"⚠️  WARNING: {msg}")


def log_error(msg: str, exc: Exception = None):
    """记录错误"""
    LOG_STATS["errors_occurred"] += 1
    DETAILED_LOGGER.error(f"❌ ERROR: {msg}")
    if exc:
        import traceback
        DETAILED_LOGGER.error(f"  Stack: {traceback.format_exc()}")


def print_stats_summary():
    """打印详细统计"""
    elapsed = time.time() - LOG_STATS["start_time"]
    print("\n" + "="*100)
    print("📊  DETAILED EXECUTION STATS")
    print("="*100)
    print(f"  总执行行数: {LOG_STATS['total_lines']}")
    print(f"  函数调用数: {LOG_STATS['functions_called']}")
    print(f"  总耗时: {elapsed:.2f}秒")
    print(f"  错误/警告数: {LOG_STATS['errors_occurred']}")
    print("\n  分支覆盖:")
    for branch, count in sorted(LOG_STATS["branches_taken"].items(), key=lambda x: -x[1]):
        print(f"    - {branch}: {count}次")
    print("="*100)


def trace(func):
    """装饰器：完整追踪函数执行"""
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        log_func_entry(func_name, *args, **kwargs)
        
        try:
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            DETAILED_LOGGER.debug(f"  耗时: {elapsed:.4f}秒")
            log_func_exit(func_name, result)
            return result
        except Exception as e:
            log_error(f"{func_name} 异常", e)
            raise
    return wrapper

