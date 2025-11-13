from typing import Dict, Any, Callable, Optional
from enum import Enum
import logging
import traceback
from datetime import datetime


class ExceptionType(Enum):
    """异常类型枚举"""
    CONNECTION_ERROR = "connection_error"
    TIMEOUT_ERROR = "timeout_error"
    VALIDATION_ERROR = "validation_error"
    BUSINESS_ERROR = "business_error"
    SYSTEM_ERROR = "system_error"
    UNKNOWN_ERROR = "unknown_error"


class RecoveryStrategy(Enum):
    """恢复策略枚举"""
    RETRY = "retry"
    FALLBACK = "fallback"
    ESCALATE = "escalate"
    IGNORE = "ignore"


class ExceptionInfo:
    """异常信息类"""
    
    def __init__(self, 
                 exception_type: ExceptionType, 
                 message: str, 
                 context: Dict[str, Any] = None,
                 recovery_strategy: RecoveryStrategy = RecoveryStrategy.IGNORE):
        self.exception_type = exception_type
        self.message = message
        self.context = context or {}
        self.recovery_strategy = recovery_strategy
        self.timestamp = datetime.now()
        self.traceback = traceback.format_stack()


class ExceptionHandler:
    """异常处理器"""
    
    def __init__(self):
        self.handlers: Dict[ExceptionType, Callable] = {}
        self.recovery_strategies: Dict[ExceptionType, RecoveryStrategy] = {}
        self.logger = logging.getLogger(__name__)
        self.setup_default_handlers()
    
    def setup_default_handlers(self):
        """设置默认异常处理器"""
        # 连接错误处理
        self.add_handler(
            ExceptionType.CONNECTION_ERROR,
            self._handle_connection_error
        )
        self.recovery_strategies[ExceptionType.CONNECTION_ERROR] = RecoveryStrategy.RETRY
        
        # 超时错误处理
        self.add_handler(
            ExceptionType.TIMEOUT_ERROR,
            self._handle_timeout_error
        )
        self.recovery_strategies[ExceptionType.TIMEOUT_ERROR] = RecoveryStrategy.RETRY
        
        # 验证错误处理
        self.add_handler(
            ExceptionType.VALIDATION_ERROR,
            self._handle_validation_error
        )
        self.recovery_strategies[ExceptionType.VALIDATION_ERROR] = RecoveryStrategy.IGNORE
        
        # 业务错误处理
        self.add_handler(
            ExceptionType.BUSINESS_ERROR,
            self._handle_business_error
        )
        self.recovery_strategies[ExceptionType.BUSINESS_ERROR] = RecoveryStrategy.ESCALATE
        
        # 系统错误处理
        self.add_handler(
            ExceptionType.SYSTEM_ERROR,
            self._handle_system_error
        )
        self.recovery_strategies[ExceptionType.SYSTEM_ERROR] = RecoveryStrategy.ESCALATE
    
    def add_handler(self, exception_type: ExceptionType, handler: Callable):
        """添加异常处理器"""
        self.handlers[exception_type] = handler
    
    def handle_exception(self, 
                        exception: Exception, 
                        context: Dict[str, Any] = None) -> ExceptionInfo:
        """处理异常并返回异常信息"""
        # 确定异常类型
        exception_type = self._classify_exception(exception)
        
        # 获取恢复策略
        recovery_strategy = self.recovery_strategies.get(
            exception_type, 
            RecoveryStrategy.IGNORE
        )
        
        # 创建异常信息
        exception_info = ExceptionInfo(
            exception_type=exception_type,
            message=str(exception),
            context=context or {},
            recovery_strategy=recovery_strategy
        )
        
        # 记录异常
        self.logger.error(
            f"Exception caught: {exception_type.value} - {exception}",
            extra={'context': context}
        )
        
        # 执行相应的处理器
        if exception_type in self.handlers:
            self.handlers[exception_type](exception_info)
        
        return exception_info
    
    def _classify_exception(self, exception: Exception) -> ExceptionType:
        """分类异常类型"""
        exception_str = str(type(exception).__name__).lower()
        
        if 'connection' in exception_str or 'connect' in exception_str:
            return ExceptionType.CONNECTION_ERROR
        elif 'timeout' in exception_str:
            return ExceptionType.TIMEOUT_ERROR
        elif 'validation' in exception_str or 'value' in exception_str:
            return ExceptionType.VALIDATION_ERROR
        elif 'business' in exception_str:
            return ExceptionType.BUSINESS_ERROR
        elif 'system' in exception_str:
            return ExceptionType.SYSTEM_ERROR
        else:
            return ExceptionType.UNKNOWN_ERROR
    
    def _handle_connection_error(self, exception_info: ExceptionInfo):
        """处理连接错误"""
        self.logger.warning("Handling connection error...")
        # 实现具体的连接错误处理逻辑
    
    def _handle_timeout_error(self, exception_info: ExceptionInfo):
        """处理超时错误"""
        self.logger.warning("Handling timeout error...")
        # 实现具体的超时错误处理逻辑
    
    def _handle_validation_error(self, exception_info: ExceptionInfo):
        """处理验证错误"""
        self.logger.warning("Handling validation error...")
        # 实现具体的验证错误处理逻辑
    
    def _handle_business_error(self, exception_info: ExceptionInfo):
        """处理业务错误"""
        self.logger.error("Handling business error...")
        # 实现具体的业务错误处理逻辑
    
    def _handle_system_error(self, exception_info: ExceptionInfo):
        """处理系统错误"""
        self.logger.critical("Handling system error...")
        # 实现具体的系统错误处理逻辑
    
    def apply_recovery_strategy(self, 
                              exception_info: ExceptionInfo, 
                              operation: Callable,
                              *args, 
                              **kwargs) -> Any:
        """应用恢复策略"""
        strategy = exception_info.recovery_strategy
        
        if strategy == RecoveryStrategy.RETRY:
            max_retries = kwargs.get('max_retries', 3)
            for i in range(max_retries):
                try:
                    return operation(*args, **kwargs)
                except Exception as e:
                    if i == max_retries - 1:  # 最后一次重试
                        raise e
                    # 等待一段时间后重试
                    import time
                    time.sleep(2 ** i)  # 指数退避
        elif strategy == RecoveryStrategy.FALLBACK:
            # 执行备用操作
            fallback_operation = kwargs.get('fallback_operation')
            if fallback_operation:
                return fallback_operation(*args, **kwargs)
        elif strategy == RecoveryStrategy.ESCALATE:
            # 抛出异常，让上级处理
            raise Exception(f"Escalating exception: {exception_info.message}")
        elif strategy == RecoveryStrategy.IGNORE:
            # 忽略异常，返回默认值
            return kwargs.get('default_return_value', None)
        
        # 默认返回None
        return None