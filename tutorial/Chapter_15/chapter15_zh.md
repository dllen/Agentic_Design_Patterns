# 第15章：代理间通信 (Inter-Agent Communication)

## 模式概述
代理间通信（Inter-Agent Communication）是多代理系统中的一个关键设计模式，它使不同的智能代理能够相互通信、协作和共享信息。这种模式允许代理协同工作以解决复杂问题、共享知识和协调行动。

代理间通信模式的核心思想是创建一个通信基础设施，使代理能够：
1. 交换信息和状态
2. 请求彼此的帮助或服务
3. 协调复杂任务的执行
4. 共享知识和学习成果

通过实施代理间通信，多代理系统可以实现比单个代理更高级别的智能和能力。代理可以专业化处理特定任务，然后通过通信协作完成复杂目标。这种模式对于构建分布式智能系统、解决复杂问题和实现高级自动化特别有价值。

## 核心概念
1. **通信协议**：代理间通信的标准化方式
2. **消息传递**：代理间信息交换的机制
3. **协作协调**：同步多个代理行动的方法
4. **知识共享**：跨代理共享信息和学习成果

## 实际应用
代理间通信模式广泛应用于各种场景，包括：
- 多代理协作系统
- 供应链管理
- 自动化工作流
- 分布式问题解决
- 专家系统协作

## 代码示例

### 示例1：A2A（Agent-to-Agent）通信

根据笔记本中的信息，这里是一个A2A通信的示例：

```python
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

class AgentCard:
    """
    代理卡片 - 用于描述和通信的代理标识符
    """
    def __init__(self, agent_id: str, name: str, capabilities: List[str], 
                 description: str = "", endpoint: str = ""):
        self.agent_id = agent_id
        self.name = name
        self.capabilities = capabilities
        self.description = description
        self.endpoint = endpoint
        self.last_seen = datetime.now()
    
    def to_json(self) -> str:
        """将代理卡片转换为JSON格式"""
        return json.dumps({
            'agent_id': self.agent_id,
            'name': self.name,
            'capabilities': self.capabilities,
            'description': self.description,
            'endpoint': self.endpoint,
            'last_seen': self.last_seen.isoformat()
        })
    
    @classmethod
    def from_json(cls, json_str: str):
        """从JSON格式创建代理卡片"""
        data = json.loads(json_str)
        card = cls(
            agent_id=data['agent_id'],
            name=data['name'],
            capabilities=data['capabilities'],
            description=data['description'],
            endpoint=data['endpoint']
        )
        card.last_seen = datetime.fromisoformat(data['last_seen'])
        return card

class Message:
    """
    代理间消息
    """
    def __init__(self, sender_id: str, receiver_id: str, content: Any, 
                 message_type: str = "request", correlation_id: Optional[str] = None):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.content = content
        self.message_type = message_type
        self.timestamp = datetime.now()
        self.correlation_id = correlation_id or f"msg_{int(datetime.now().timestamp())}"
        self.response_to = None
    
    def to_dict(self) -> Dict[str, Any]:
        """将消息转换为字典格式"""
        return {
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'content': self.content,
            'message_type': self.message_type,
            'timestamp': self.timestamp.isoformat(),
            'correlation_id': self.correlation_id,
            'response_to': self.response_to
        }

class Agent:
    """
    可通信的智能代理基类
    """
    def __init__(self, agent_id: str, name: str, capabilities: List[str]):
        self.agent_id = agent_id
        self.name = name
        self.capabilities = capabilities
        self.agent_card = AgentCard(agent_id, name, capabilities)
        self.message_queue = []
        self.known_agents = {}  # agent_id -> AgentCard
    
    def send_message(self, receiver_id: str, content: Any, message_type: str = "request"):
        """发送消息到另一个代理"""
        message = Message(self.agent_id, receiver_id, content, message_type)
        self.message_queue.append(message)
        print(f"📤 {self.name} 发送消息到 {receiver_id}: {content}")
        return message
    
    def receive_message(self, message: Message):
        """接收来自另一个代理的消息"""
        print(f"📥 {self.name} 收到消息来自 {message.sender_id}: {message.content}")
        self.message_queue.append(message)
        return self.process_message(message)
    
    def process_message(self, message: Message) -> Any:
        """处理收到的消息"""
        # 默认消息处理逻辑
        if message.message_type == "request":
            # 处理请求消息
            return self.handle_request(message.content)
        elif message.message_type == "response":
            # 处理响应消息
            return self.handle_response(message.content, message.correlation_id)
        else:
            return f"未知消息类型: {message.message_type}"
    
    def handle_request(self, content: Any) -> Any:
        """处理请求"""
        # 子类应重写此方法
        return f"{self.name} 处理请求: {content}"
    
    def handle_response(self, content: Any, correlation_id: str) -> Any:
        """处理响应"""
        # 子类应重写此方法
        return f"{self.name} 处理响应: {content}"
    
    def register_agent(self, agent_card: AgentCard):
        """注册另一个代理"""
        self.known_agents[agent_card.agent_id] = agent_card
        print(f"📋 {self.name} 注册代理: {agent_card.name}")

# 示例：天气代理
class WeatherAgent(Agent):
    def __init__(self):
        super().__init__("weather_agent", "天气服务代理", ["get_weather", "forecast"])
        self.weather_data = {
            "北京": {"temperature": 22, "condition": "晴", "humidity": 45},
            "上海": {"temperature": 25, "condition": "多云", "humidity": 60},
            "广州": {"temperature": 28, "condition": "雨", "humidity": 80}
        }
    
    def handle_request(self, content: Any) -> Any:
        """处理天气请求"""
        if isinstance(content, dict) and "location" in content:
            location = content["location"]
            if location in self.weather_data:
                return {
                    "status": "success",
                    "data": self.weather_data[location],
                    "location": location
                }
            else:
                return {
                    "status": "error",
                    "message": f"未找到位置 {location} 的天气数据"
                }
        return {"status": "error", "message": "无效的天气请求"}

# 示例：日历代理
class CalendarAgent(Agent):
    def __init__(self):
        super().__init__("calendar_agent", "日历服务代理", ["get_schedule", "create_event"])
        self.schedule = {
            "2023-12-01": ["会议A", "电话B"],
            "2023-12-02": ["培训C"],
            "2023-12-03": ["会议A", "晚餐D"]
        }
    
    def handle_request(self, content: Any) -> Any:
        """处理日历请求"""
        if isinstance(content, dict) and "date" in content:
            date = content["date"]
            if date in self.schedule:
                return {
                    "status": "success",
                    "events": self.schedule[date],
                    "date": date
                }
            else:
                return {
                    "status": "error", 
                    "message": f"未找到日期 {date} 的日程安排"
                }
        return {"status": "error", "message": "无效的日历请求"}

# 示例：协调代理
class CoordinatorAgent(Agent):
    def __init__(self):
        super().__init__("coordinator_agent", "协调代理", ["coordinate_tasks", "aggregate_info"])
        self.registered_agents = {}
    
    def register_agent(self, agent: Agent):
        """注册可协调的代理"""
        self.registered_agents[agent.agent_id] = agent
        super().register_agent(agent.agent_card)
    
    def coordinate_weather_and_schedule(self, location: str, date: str):
        """协调天气和日程信息"""
        results = {}
        
        # 向天气代理请求天气信息
        if "weather_agent" in self.registered_agents:
            weather_request = {"location": location}
            weather_msg = self.send_message("weather_agent", weather_request, "request")
            weather_result = self.registered_agents["weather_agent"].receive_message(weather_msg)
            results["weather"] = weather_result
        
        # 向日历代理请求日程信息
        if "calendar_agent" in self.registered_agents:
            calendar_request = {"date": date}
            calendar_msg = self.send_message("calendar_agent", calendar_request, "request")
            calendar_result = self.registered_agents["calendar_agent"].receive_message(calendar_msg)
            results["calendar"] = calendar_result
        
        # 聚合结果
        return {
            "location": location,
            "date": date,
            "combined_info": results,
            "recommendation": self._generate_recommendation(results)
        }
    
    def _generate_recommendation(self, results: Dict[str, Any]) -> str:
        """基于天气和日程生成建议"""
        weather = results.get("weather", {}).get("data", {})
        calendar = results.get("calendar", {}).get("events", [])
        
        if weather and calendar:
            temp = weather.get("temperature", 0)
            condition = weather.get("condition", "未知")
            
            if temp > 25 and condition in ["雨", "雪"]:
                return "由于天气原因，建议调整户外活动安排"
            elif calendar:
                return f"日程安排正常，当前天气: {condition}, 温度: {temp}°C"
        
        return "无法生成具体建议，信息不足"

# 使用示例
def example_usage():
    # 创建代理
    weather_agent = WeatherAgent()
    calendar_agent = CalendarAgent()
    coordinator = CoordinatorAgent()
    
    # 注册代理到协调器
    coordinator.register_agent(weather_agent)
    coordinator.register_agent(calendar_agent)
    
    # 协调天气和日程信息
    result = coordinator.coordinate_weather_and_schedule("北京", "2023-12-01")
    
    print("协调结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    example_usage()
```

### 示例2：同步和流式请求

```python
import asyncio
from typing import Dict, Any, AsyncGenerator
import time

class AsyncAgent:
    """
    支持异步通信的代理
    """
    def __init__(self, agent_id: str, name: str):
        self.agent_id = agent_id
        self.name = name
        self.response_handlers = {}
    
    async def send_request_sync(self, receiver: 'AsyncAgent', request: Any) -> Any:
        """同步发送请求并等待响应"""
        print(f"⏳ {self.name} 同步发送请求到 {receiver.name}")
        start_time = time.time()
        
        # 模拟网络延迟
        await asyncio.sleep(0.5)
        
        # 直接调用接收方处理方法
        response = await receiver.handle_request_async(request)
        
        end_time = time.time()
        print(f"✅ {self.name} 收到同步响应 (耗时: {end_time - start_time:.2f}s)")
        return response
    
    async def send_request_streaming(self, receiver: 'AsyncAgent', request: Any) -> AsyncGenerator[Any, None]:
        """流式发送请求，接收分块响应"""
        print(f"🌊 {self.name} 流式发送请求到 {receiver.name}")
        
        # 模拟流式数据
        items = ["数据块1", "数据块2", "数据块3", "数据块4", "完成"]
        
        for item in items:
            await asyncio.sleep(0.3)  # 模拟处理时间
            yield f"[{self.name}->{receiver.name}] {item}"
    
    async def handle_request_async(self, request: Any) -> Any:
        """异步处理请求"""
        print(f"⚙️  {self.name} 异步处理请求: {request}")
        await asyncio.sleep(1)  # 模拟处理时间
        return f"{self.name} 处理结果: {request}"

class DataProcessingAgent(AsyncAgent):
    """
    数据处理代理
    """
    def __init__(self, agent_id: str):
        super().__init__(agent_id, "数据处理代理")
    
    async def process_large_dataset(self, dataset: list) -> AsyncGenerator[Dict[str, Any], None]:
        """
        处理大数据集并流式返回结果
        """
        total_items = len(dataset)
        
        for i, item in enumerate(dataset):
            # 模拟处理时间
            await asyncio.sleep(0.2)
            
            processed_item = {
                "original": item,
                "processed": f"processed_{item}",
                "progress": f"{i+1}/{total_items}",
                "status": "processing"
            }
            
            yield processed_item
        
        yield {
            "status": "completed",
            "message": f"处理完成，共处理 {total_items} 个项目"
        }

class AnalysisAgent(AsyncAgent):
    """
    分析代理
    """
    def __init__(self, agent_id: str):
        super().__init__(agent_id, "分析代理")
    
    async def analyze_data_stream(self, data_stream: AsyncGenerator[Dict[str, Any], None]) -> Dict[str, Any]:
        """
        分析数据流
        """
        results = []
        async for data_chunk in data_stream:
            results.append(data_chunk)
            print(f"📊 分析中: {data_chunk.get('progress', 'unknown')}")
        
        # 生成分析报告
        processed_count = sum(1 for r in results if 'processed' in r)
        
        return {
            "status": "analysis_complete",
            "processed_items": processed_count,
            "total_items": len(results),
            "summary": f"分析完成，处理了 {processed_count} 个项目"
        }

# 使用示例
async def async_communication_example():
    data_agent = DataProcessingAgent("data_agent_001")
    analysis_agent = AnalysisAgent("analysis_agent_001")
    
    # 准备数据集
    dataset = ["item_1", "item_2", "item_3", "item_4", "item_5"]
    
    print("=== 同步代理通信 ===")
    sync_result = await data_agent.send_request_sync(analysis_agent, "同步分析请求")
    print(f"同步结果: {sync_result}\n")
    
    print("=== 流式代理通信 ===")
    # 获取数据处理流
    data_stream = data_agent.process_large_dataset(dataset)
    
    # 分析数据流
    analysis_result = await analysis_agent.analyze_data_stream(data_stream)
    print(f"分析结果: {json.dumps(analysis_result, ensure_ascii=False, indent=2)}\n")
    
    print("=== 代理间流式通信 ===")
    # 数据代理处理数据并通过流式通信发送到分析代理
    data_stream = data_agent.process_large_dataset(dataset)
    final_analysis = await analysis_agent.analyze_data_stream(data_stream)
    print(f"最终分析: {json.dumps(final_analysis, ensure_ascii=False, indent=2)}")

if __name__ == "__main__":
    asyncio.run(async_communication_example())
```

## 最佳实践
1. **标准化协议**：使用标准化的消息格式和通信协议
2. **错误处理**：实现代理间通信的错误处理和重试机制
3. **负载管理**：管理代理间通信的负载和频率
4. **安全性**：确保代理间通信的安全性
5. **可扩展性**：设计可扩展的通信架构

## 总结
代理间通信是构建多代理系统的关键技术，它使代理能够协作、共享信息和协调行动。通过实施有效的通信机制，多代理系统可以解决单个代理无法处理的复杂问题，实现更高级别的智能和自动化。这种模式对于构建分布式智能系统和实现高级协作至关重要。