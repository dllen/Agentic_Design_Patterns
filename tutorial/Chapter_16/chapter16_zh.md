# 第16章：资源感知优化 (Resource-Aware Optimization)

## 模式概述
资源感知优化（Resource-Aware Optimization）是智能代理系统中的一个关键设计模式，它使代理能够根据可用资源（如计算能力、内存、网络带宽、能源等）来调整其行为和决策。这种模式确保代理在资源受限的环境中高效运行，同时尽可能保持性能和功能。

资源感知优化模式的核心思想是创建能够：
1. 监测当前资源使用情况
2. 预测资源需求
3. 根据资源可用性调整策略
4. 在性能和资源使用之间做出智能权衡

通过实施资源感知优化，代理可以在各种环境中高效运行，从资源受限的边缘设备到资源丰富的云端环境。这种模式对于在移动设备、物联网设备或其他资源受限环境中部署的代理特别有价值。

## 核心概念
1. **资源监测**：实时跟踪系统资源使用情况
2. **自适应决策**：根据资源可用性调整行为
3. **性能权衡**：在性能和资源使用之间找到平衡
4. **预测性管理**：预测资源需求并提前调整

## 实际应用
资源感知优化模式广泛应用于各种场景，包括：
- 移动设备上的AI应用
- 物联网和边缘计算
- 云计算资源管理
- 实时系统优化
- 电池供电设备的能源管理

## 代码示例

### 示例1：资源感知代理

```python
import psutil
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ResourceMetrics:
    """
    资源指标数据类
    """
    cpu_percent: float
    memory_percent: float
    available_memory_mb: float
    network_usage: float
    disk_usage: float
    timestamp: float

class ResourceAwareAgent:
    """
    资源感知代理
    """
    def __init__(self, max_memory_mb: int = 1024, cpu_threshold: float = 80.0):
        self.max_memory_mb = max_memory_mb
        self.cpu_threshold = cpu_threshold
        self.resource_history = []
        self.current_strategy = "high_performance"
    
    def get_resource_metrics(self) -> ResourceMetrics:
        """
        获取当前资源指标
        """
        # 获取CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 获取内存信息
        memory_info = psutil.virtual_memory()
        available_memory_mb = memory_info.available / (1024 * 1024)  # 转换为MB
        
        # 获取网络使用情况（简化的指标）
        network_info = psutil.net_io_counters()
        network_usage = (network_info.bytes_sent + network_info.bytes_recv) / (1024 * 1024)  # MB
        
        # 获取磁盘使用情况
        disk_usage = psutil.disk_usage('/').percent
        
        metrics = ResourceMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory_info.percent,
            available_memory_mb=available_memory_mb,
            network_usage=network_usage,
            disk_usage=disk_usage,
            timestamp=time.time()
        )
        
        # 保存到历史记录
        self.resource_history.append(metrics)
        
        # 限制历史记录大小
        if len(self.resource_history) > 100:
            self.resource_history = self.resource_history[-50:]
        
        return metrics
    
    def determine_optimization_strategy(self) -> str:
        """
        根据资源指标确定优化策略
        """
        if not self.resource_history:
            return "balanced"
        
        latest_metrics = self.resource_history[-1]
        
        # 检查CPU使用率
        if latest_metrics.cpu_percent > self.cpu_threshold:
            return "cpu_efficient"
        
        # 检查内存使用
        if latest_metrics.available_memory_mb < 256:  # 少于256MB可用
            return "memory_efficient"
        
        # 检查内存使用百分比
        if latest_metrics.memory_percent > 90:
            return "memory_efficient"
        
        # 如果资源充足，使用高性能模式
        if latest_metrics.available_memory_mb > 1024 and latest_metrics.cpu_percent < 50:
            return "high_performance"
        
        return "balanced"
    
    def adjust_behavior_for_resources(self, task_complexity: str = "medium") -> Dict[str, Any]:
        """
        根据资源情况调整行为
        """
        metrics = self.get_resource_metrics()
        strategy = self.determine_optimization_strategy()
        
        self.current_strategy = strategy
        
        # 基于策略和任务复杂度调整参数
        config = {
            "strategy": strategy,
            "max_parallel_tasks": 1,
            "model_precision": "full",
            "cache_size": 100,
            "timeout_ms": 5000
        }
        
        if strategy == "cpu_efficient":
            config.update({
                "max_parallel_tasks": 1,
                "timeout_ms": 10000,
                "model_precision": "reduced"
            })
        elif strategy == "memory_efficient":
            config.update({
                "cache_size": 10,
                "model_precision": "reduced",
                "max_parallel_tasks": 1
            })
        elif strategy == "high_performance":
            config.update({
                "max_parallel_tasks": 4,
                "cache_size": 1000,
                "timeout_ms": 2000
            })
        
        # 根据任务复杂度进一步调整
        if task_complexity == "high":
            if strategy != "high_performance":
                # 在资源受限时降低期望
                config["max_parallel_tasks"] = max(1, config["max_parallel_tasks"] // 2)
        elif task_complexity == "low":
            # 在低复杂度任务时可以更节省资源
            config["cache_size"] = max(5, config["cache_size"] // 2)
        
        return config
    
    def execute_resource_aware_task(self, task_func, *args, **kwargs):
        """
        使用资源感知配置执行任务
        """
        # 获取当前资源感知配置
        config = self.adjust_behavior_for_resources()
        
        print(f"🔧 执行任务，策略: {config['strategy']}")
        print(f"📊 当前资源状态 - CPU: {self.resource_history[-1].cpu_percent}%, "
              f"内存: {self.resource_history[-1].available_memory_mb:.1f}MB 可用")
        
        # 应用配置到任务执行
        try:
            result = task_func(*args, **kwargs)
            return {
                "result": result,
                "config_used": config,
                "resources_used": self.resource_history[-1]
            }
        except Exception as e:
            print(f"⚠️  任务执行失败: {str(e)}")
            # 尝试降级执行
            return self._fallback_execution(task_func, *args, **kwargs)
    
    def _fallback_execution(self, task_func, *args, **kwargs):
        """
        降级执行模式
        """
        print("🔄 切换到降级执行模式")
        # 应用最节省资源的配置
        # 这里可以实现降级逻辑
        try:
            return {
                "result": task_func(*args, **kwargs),
                "config_used": {"strategy": "fallback", "max_parallel_tasks": 1},
                "resources_used": self.resource_history[-1],
                "warning": "使用降级配置执行"
            }
        except Exception as e:
            return {
                "error": f"降级执行也失败: {str(e)}",
                "config_used": {"strategy": "fallback"},
                "resources_used": self.resource_history[-1]
            }

# 使用示例
def example_task(data_size: int):
    """
    示例任务：模拟不同数据量的处理
    """
    import time
    import random
    
    print(f"⚙️  执行任务，数据量: {data_size}")
    time.sleep(0.1 * min(data_size, 10))  # 模拟处理时间
    
    # 模拟一些计算
    result = sum(random.randint(1, 100) for _ in range(min(data_size * 100, 10000)))
    return f"处理了 {data_size} 单位数据，结果总和: {result}"

def resource_aware_example():
    agent = ResourceAwareAgent(max_memory_mb=512, cpu_threshold=75.0)
    
    # 执行不同复杂度的任务
    tasks = [
        ("小任务", 1),
        ("中等任务", 5),
        ("大任务", 10)
    ]
    
    for task_name, data_size in tasks:
        print(f"\n--- {task_name} ---")
        result = agent.execute_resource_aware_task(example_task, data_size)
        print(f"结果: {result['result']}")
        print(f"使用配置: {result['config_used']['strategy']}")
        print("-" * 50)

if __name__ == "__main__":
    resource_aware_example()
```

### 示例2：基于Open Information和Google搜索的资源优化

```python
from typing import Dict, List, Optional
import asyncio
import aiohttp
import time

class ResourceOptimizedSearchAgent:
    """
    资源优化的搜索代理
    """
    def __init__(self, max_concurrent_requests: int = 2, timeout_seconds: int = 10):
        self.max_concurrent_requests = max_concurrent_requests
        self.timeout_seconds = timeout_seconds
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        self.cache = {}
        self.cache_ttl = 300  # 5分钟缓存
    
    def _get_cache_key(self, query: str, search_type: str) -> str:
        """
        生成缓存键
        """
        return f"{search_type}:{query.lower().strip()}"
    
    def _is_cache_valid(self, cached_item: Dict[str, Any]) -> bool:
        """
        检查缓存项是否有效
        """
        if 'timestamp' not in cached_item:
            return False
        return time.time() - cached_item['timestamp'] < self.cache_ttl
    
    async def search_with_resource_optimization(self, query: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        使用资源优化进行搜索
        """
        cache_key = self._get_cache_key(query, "search")
        
        # 检查缓存
        if use_cache and cache_key in self.cache:
            cached_result = self.cache[cache_key]
            if self._is_cache_valid(cached_result):
                print(f"⚡ 使用缓存结果: {query}")
                return cached_result['data']
        
        # 使用信号量限制并发
        async with self.semaphore:
            try:
                start_time = time.time()
                print(f"🔍 搜索查询: {query}")
                
                # 模拟搜索执行
                result = await self._perform_search(query)
                
                # 计算执行时间
                execution_time = time.time() - start_time
                
                # 保存到缓存
                if use_cache:
                    self.cache[cache_key] = {
                        'data': result,
                        'timestamp': time.time()
                    }
                
                result['execution_time'] = execution_time
                result['used_cache'] = False
                
                return result
            except Exception as e:
                return {
                    'error': str(e),
                    'query': query,
                    'execution_time': time.time() - start_time if 'start_time' in locals() else 0
                }
    
    async def _perform_search(self, query: str) -> Dict[str, Any]:
        """
        执行搜索操作
        """
        # 模拟API调用延迟
        await asyncio.sleep(0.5)
        
        # 模拟搜索结果
        search_results = {
            'query': query,
            'results': [
                {'title': f'关于 {query} 的资源1', 'url': f'http://example.com/{query}/1', 'snippet': '这是相关资源的摘要...'},
                {'title': f'关于 {query} 的资源2', 'url': f'http://example.com/{query}/2', 'snippet': '另一个相关的资源...'},
                {'title': f'关于 {query} 的资源3', 'url': f'http://example.com/{query}/3', 'snippet': '第三个相关资源...'}
            ],
            'total_results': 42,
            'search_performed_at': time.time()
        }
        
        return search_results
    
    async def batch_search_with_resource_management(self, queries: List[str], 
                                                    max_time_budget: float = 30.0) -> List[Dict[str, Any]]:
        """
        在时间预算内执行批量搜索
        """
        start_time = time.time()
        results = []
        
        for query in queries:
            # 检查时间预算
            elapsed_time = time.time() - start_time
            remaining_time = max_time_budget - elapsedTime
            
            if remaining_time <= 2.0:  # 保留2秒用于最终处理
                print(f"⏱️  时间预算不足，跳过剩余查询，已用时间: {elapsed_time:.2f}s")
                break
            
            result = await self.search_with_resource_optimization(query)
            results.append(result)
            
            # 更新已用时间
            elapsed_time = time.time() - start_time
            print(f"批次搜索进度: {len(results)}/{len(queries)}, 已用时间: {elapsed_time:.2f}s")
        
        return results
    
    def get_resource_usage_stats(self) -> Dict[str, Any]:
        """
        获取资源使用统计
        """
        return {
            'cache_size': len(self.cache),
            'max_concurrent_requests': self.max_concurrent_requests,
            'timeout_settings': self.timeout_seconds,
            'estimated_memory_usage_mb': len(str(self.cache)) / (1024 * 1024)  # 粗略估计
        }

# 使用示例
async def resource_optimized_search_example():
    agent = ResourceOptimizedSearchAgent(max_concurrent_requests=2, timeout_seconds=15)
    
    # 单个搜索示例
    print("=== 单个搜索示例 ===")
    result = await agent.search_with_resource_optimization("Python 机器学习")
    print(f"搜索结果: {result['results'][:2]}")  # 只显示前两个结果
    print(f"执行时间: {result['execution_time']:.2f}s\n")
    
    # 批量搜索示例
    print("=== 批量搜索示例 ===")
    queries = [
        "Python 机器学习",
        "机器学习算法",
        "深度学习框架",
        "自然语言处理",
        "计算机视觉应用"
    ]
    
    batch_results = await agent.batch_search_with_resource_management(queries, max_time_budget=20.0)
    print(f"完成 {len(batch_results)} 个查询")
    
    # 显示资源使用统计
    stats = agent.get_resource_usage_stats()
    print(f"\n📊 资源使用统计:")
    print(f"   缓存大小: {stats['cache_size']} 项")
    print(f"   最大并发请求数: {stats['max_concurrent_requests']}")
    print(f"   超时设置: {stats['timeout_settings']} 秒")

if __name__ == "__main__":
    asyncio.run(resource_optimized_search_example())
```

## 最佳实践
1. **资源监控**：持续监控关键资源指标
2. **自适应阈值**：根据环境动态调整资源阈值
3. **优雅降级**：在资源不足时提供降级功能
4. **缓存策略**：有效利用缓存减少资源消耗
5. **负载预测**：预测未来资源需求并提前调整

## 总结
资源感知优化是构建高效AI代理的关键技术，它使代理能够根据可用资源动态调整其行为。通过实施资源感知优化，代理可以在各种环境中高效运行，提供一致的用户体验，同时最小化资源消耗。这种模式对于在资源受限环境中部署的代理系统特别重要。