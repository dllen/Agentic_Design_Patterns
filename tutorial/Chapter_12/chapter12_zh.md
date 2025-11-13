# 第12章：异常处理和恢复 (Exception Handling and Recovery)

## 模式概述
异常处理和恢复（Exception Handling and Recovery）是智能代理系统中的一个关键设计模式，它使代理能够优雅地处理错误、故障和意外情况，并在可能的情况下从中恢复。这种模式确保代理在面对各种异常情况时仍能提供有价值的响应或服务。

异常处理和恢复模式的核心思想是创建一个鲁棒的系统，能够：
1. 检测和识别异常情况
2. 在不完全失败的情况下处理异常
3. 尝试恢复到正常操作状态
4. 在无法恢复时提供适当的回退机制

通过实施异常处理和恢复，代理可以显著提高其可靠性和用户体验。当发生错误时，代理不是简单地失败，而是尝试提供替代解决方案或有意义的错误消息。这种模式对于在生产环境中运行、处理用户输入或依赖外部服务的代理特别重要。

## 核心概念
1. **异常检测**：识别操作中的错误、故障或意外情况
2. **错误隔离**：防止异常影响代理的其他功能
3. **恢复策略**：实现从错误中恢复的机制
4. **回退机制**：在无法恢复时提供替代方案

## 实际应用
异常处理和恢复模式广泛应用于各种场景，包括：
- 外部API调用失败时的处理
- 网络连接中断时的恢复
- 数据验证错误的处理
- 资源不可用时的备用方案
- 用户输入错误的处理

## 代码示例

### 示例1：使用ADK的代理回退机制

```python
from google.adk.agents import Agent, SequentialAgent

# 代理1：尝试主要工具。其关注点是窄而明确的。
primary_handler = Agent(
    name="primary_handler",
    model="gemini-2.0-flash-exp",
    instruction="""
您的工作是获取精确的位置信息。
使用用户提供的地址使用get_precise_location_info工具。
    """,
    tools=[get_precise_location_info]
)

# 代理2：作为回退处理器，检查状态以决定其操作。
fallback_handler = Agent(
    name="fallback_handler",
    model="gemini-2.0-flash-exp",
    instruction="""
检查通过查看state["primary_location_failed"]是否主位置查找失败。
- 如果为True，则从用户的原始查询中提取城市并使用get_general_area_info工具。
- 如果为False，则不执行任何操作。
    """,
    tools=[get_general_area_info]
)

# 代理3：呈现状态中的最终结果。
response_agent = Agent(
    name="response_agent",
    model="gemini-2.0-flash-exp",
    instruction="""
查看保存在state["location_result"]中的位置信息。
将此信息清晰简洁地呈现给用户。
如果state["location_result"]不存在或为空，则道歉无法检索位置。
    """,
    tools=[] # 此代理仅推理最终状态。
)


# SequentialAgent确保处理器按保证顺序运行。
robust_location_agent = SequentialAgent(
    name="robust_location_agent",
    sub_agents=[primary_handler, fallback_handler, response_agent]
)
```

### 实用的异常处理和恢复示例

```python
from typing import Any, Optional, Dict, Callable
import time
import random

class ExceptionHandlingAgent:
    """
    具有异常处理和恢复能力的代理示例
    """
    def __init__(self):
        self.fallback_strategies = {}
        self.error_history = []
        self.recovery_attempts = 0
        self.max_recovery_attempts = 3

    def execute_with_fallback(self, primary_action: Callable, fallback_action: Callable, *args, **kwargs):
        """
        使用回退机制执行主要操作
        """
        try:
            # 尝试主要操作
            result = primary_action(*args, **kwargs)
            return result
        except Exception as e:
            # 记录错误
            self._log_error(type(e).__name__, str(e), "primary_action")
            
            # 如果主要操作失败，尝试回退操作
            try:
                fallback_result = fallback_action(*args, **kwargs)
                return fallback_result
            except Exception as fallback_error:
                # 如果回退操作也失败，记录错误并抛出
                self._log_error(type(fallback_error).__name__, str(fallback_error), "fallback_action")
                raise Exception(f"主要和回退操作都失败了: {str(e)}, 回退错误: {str(fallback_error)}")

    def retry_with_backoff(self, operation: Callable, max_retries: int = 3, base_delay: float = 1.0):
        """
        带退避的重试操作
        """
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return operation()
            except Exception as e:
                last_exception = e
                self._log_error(type(e).__name__, str(e), f"retry_attempt_{attempt+1}")
                
                if attempt < max_retries - 1:  # 不在最后一次尝试后等待
                    delay = base_delay * (2 ** attempt)  # 指数退避
                    print(f"尝试 {attempt + 1} 失败，{delay}秒后重试...")
                    time.sleep(delay)
        
        raise last_exception

    def execute_with_circuit_breaker(self, operation: Callable, failure_threshold: int = 5):
        """
        使用断路器模式执行操作
        """
        if self.recovery_attempts >= self.max_recovery_attempts:
            raise Exception("断路器打开：太多连续失败，代理暂时不可用")
        
        try:
            result = operation()
            # 如果成功，重置失败计数器
            self.recovery_attempts = 0
            return result
        except Exception as e:
            # 如果失败，增加失败计数器
            self.recovery_attempts += 1
            self._log_error(type(e).__name__, str(e), "circuit_breaker_operation")
            
            if self.recovery_attempts >= failure_threshold:
                raise Exception(f"达到故障阈值 ({failure_threshold})，激活断路器")
            
            raise e

    def graceful_degradation(self, operations: list):
        """
        实现优雅降级的多个操作
        """
        results = []
        for i, operation in enumerate(operations):
            try:
                result = operation()
                results.append(result)
            except Exception as e:
                self._log_error(type(e).__name__, str(e), f"graceful_degradation_op_{i}")
                # 记录失败但继续执行其他操作
                results.append(None)
                print(f"操作 {i+1} 失败，但继续执行其他操作...")
        
        return results

    def _log_error(self, error_type: str, error_message: str, context: str):
        """
        记录错误信息用于分析和恢复
        """
        error_info = {
            'timestamp': time.time(),
            'error_type': error_type,
            'error_message': error_message,
            'context': context
        }
        self.error_history.append(error_info)

    def get_recovery_status(self) -> Dict[str, Any]:
        """
        获取恢复状态信息
        """
        return {
            'recovery_attempts': self.recovery_attempts,
            'total_errors': len(self.error_history),
            'recent_errors': self.error_history[-5:]  # 最近5个错误
        }

# 实际使用示例
def example_usage():
    agent = ExceptionHandlingAgent()
    
    # 模拟可能失败的操作
    def unreliable_api_call():
        # 模拟50%的失败率
        if random.random() < 0.5:
            raise ConnectionError("API连接超时")
        return "API调用成功结果"
    
    def fallback_api_call():
        # 模拟回退API调用
        print("使用回退API调用...")
        return "回退API结果"
    
    # 示例1：使用回退机制
    try:
        result = agent.execute_with_fallback(unreliable_api_call, fallback_api_call)
        print(f"结果: {result}")
    except Exception as e:
        print(f"所有尝试都失败了: {e}")
    
    # 示例2：使用带退避的重试
    try:
        result = agent.retry_with_backoff(unreliable_api_call, max_retries=3)
        print(f"重试结果: {result}")
    except Exception as e:
        print(f"重试失败: {e}")
    
    # 示例3：优雅降级
    def op1(): return "操作1成功"
    def op2(): 
        raise ValueError("操作2失败")
    def op3(): return "操作3成功"
    
    results = agent.graceful_degradation([op1, op2, op3])
    print(f"优雅降级结果: {results}")
    
    # 检查恢复状态
    status = agent.get_recovery_status()
    print(f"恢复状态: {status}")

if __name__ == "__main__":
    example_usage()
```

### 高级异常处理和恢复模式

```python
from typing import List, Tuple
from enum import Enum
import asyncio

class RecoveryStrategy(Enum):
    """
    恢复策略枚举
    """
    RETRY = "retry"
    FALLBACK = "fallback"
    CIRCUIT_BREAKER = "circuit_breaker"
    TIMEOUT = "timeout"
    COMPENSATION = "compensation"

class AdvancedExceptionHandlingAgent:
    """
    具有高级异常处理和恢复功能的代理
    """
    def __init__(self, max_retries: int = 3, timeout_seconds: int = 30):
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds
        self.recovery_strategies = []
        self.compensation_actions = []

    async def execute_with_timeout(self, operation, *args, timeout_seconds: Optional[int] = None, **kwargs):
        """
        带超时的异步操作执行
        """
        timeout = timeout_seconds or self.timeout_seconds
        
        try:
            result = await asyncio.wait_for(operation(*args, **kwargs), timeout=timeout)
            return result
        except asyncio.TimeoutError:
            raise TimeoutError(f"操作在{timeout}秒内未完成")

    def execute_with_compensation(self, operations: List[Tuple[Callable, Callable]]):
        """
        执行带补偿操作的任务列表
        每个任务包含（执行函数，补偿函数）
        """
        executed_operations = []
        results = []
        
        try:
            for i, (operation, compensation) in enumerate(operations):
                try:
                    result = operation()
                    results.append(result)
                    executed_operations.append((operation, compensation))
                except Exception as e:
                    # 如果操作失败，执行之前所有成功的操作的补偿
                    for exec_op, comp_func in reversed(executed_operations):
                        try:
                            comp_func()
                            print(f"执行补偿操作以撤消 {exec_op.__name__}")
                        except Exception as comp_error:
                            print(f"补偿操作失败: {comp_error}")
                    
                    raise e  # 重新抛出原始异常
        except Exception as e:
            raise e
        
        return results

    def execute_with_multiple_fallbacks(self, primary_ops: List[Callable]):
        """
        执行带多个回退选项的操作
        """
        for i, operation in enumerate(primary_ops):
            try:
                result = operation()
                print(f"在尝试 {i+1} 中成功")
                return result
            except Exception as e:
                print(f"尝试 {i+1} 失败: {e}")
                if i == len(primary_ops) - 1:  # 所有尝试都失败了
                    raise Exception(f"所有操作都失败了: {[str(e) for e in primary_ops]}")
        
        raise Exception("不应到达此点")

# 使用示例
async def advanced_example():
    agent = AdvancedExceptionHandlingAgent(max_retries=3, timeout_seconds=10)
    
    # 示例1：带超时的操作
    async def slow_operation():
        await asyncio.sleep(5)  # 模拟耗时操作
        return "操作完成"
    
    try:
        result = await agent.execute_with_timeout(slow_operation, timeout_seconds=3)
        print(f"超时操作结果: {result}")
    except TimeoutError as e:
        print(f"超时错误: {e}")
    
    # 示例2：带补偿的操作
    account_balances = {"user1": 100, "user2": 50}
    
    def transfer_money(from_acc, to_acc, amount):
        if account_balances[from_acc] < amount:
            raise ValueError(f"账户 {from_acc} 余额不足")
        account_balances[from_acc] -= amount
        account_balances[to_acc] += amount
        return f"转账 {amount} 从 {from_acc} 到 {to_acc}"
    
    def compensation_transfer(from_acc, to_acc, amount):
        # 补偿操作：撤消转账
        account_balances[from_acc] += amount
        account_balances[to_acc] -= amount
        print(f"补偿操作：撤消从 {from_acc} 到 {to_acc} 的 {amount} 转账")
    
    # 尝试一系列转账，其中一个会失败
    try:
        operations = [
            (lambda: transfer_money("user1", "user2", 30), lambda: compensation_transfer("user1", "user2", 30)),
            (lambda: transfer_money("user2", "user1", 10), lambda: compensation_transfer("user2", "user1", 10)),
            (lambda: transfer_money("user2", "user1", 100), lambda: compensation_transfer("user2", "user1", 100)),  # 这会失败
        ]
        
        results = agent.execute_with_compensation(operations)
        print("转账结果:", results)
    except Exception as e:
        print(f"转账操作失败（预期）: {e}")
        print(f"账户余额在补偿后: {account_balances}")

if __name__ == "__main__":
    # 运行异步示例
    asyncio.run(advanced_example())
```

## 最佳实践
1. **防御性编程**：始终预期可能出现的错误
2. **分级恢复**：实现多级恢复策略（重试、回退、人工干预等）
3. **错误隔离**：防止错误在系统中传播
4. **有意义的错误消息**：提供对用户有用的错误信息
5. **监控和日志**：记录错误和恢复尝试以进行分析

## 总结
异常处理和恢复是构建可靠AI代理的关键技术。通过实施有效的异常处理和恢复机制，代理可以在面对错误和故障时保持可用性，提供更好的用户体验，并在可能的情况下自主恢复。这种模式对于任何需要在现实世界条件下可靠运行的代理系统都至关重要。