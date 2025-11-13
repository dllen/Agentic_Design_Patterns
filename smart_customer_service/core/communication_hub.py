from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import json
import asyncio
from .agents.base_agent import Message


@dataclass
class CommunicationResult:
    """通信结果类"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class CommunicationHub:
    """通信中心，管理Agent间通信"""
    
    def __init__(self):
        self.agents: Dict[str, Any] = {}  # Agent注册表
        self.message_queue: List[Message] = []
        self.message_handlers: Dict[str, Callable] = {}
        
    def register_agent(self, agent_name: str, agent_instance: Any):
        """注册Agent"""
        self.agents[agent_name] = agent_instance
        print(f"Agent '{agent_name}' registered with communication hub")
    
    def unregister_agent(self, agent_name: str):
        """注销Agent"""
        if agent_name in self.agents:
            del self.agents[agent_name]
            print(f"Agent '{agent_name}' unregistered from communication hub")
    
    def send_message(self, 
                    sender: str, 
                    recipient: str, 
                    content: str, 
                    metadata: Optional[Dict[str, Any]] = None) -> CommunicationResult:
        """发送消息到指定Agent"""
        if recipient not in self.agents:
            return CommunicationResult(
                success=False,
                message=f"Recipient agent '{recipient}' not found",
                error=f"Agent '{recipient}' is not registered"
            )
        
        try:
            # 创建消息对象
            message = Message(
                sender=sender,
                recipient=recipient,
                content=content,
                metadata=metadata or {}
            )
            
            # 将消息添加到队列
            self.message_queue.append(message)
            
            # 直接发送给接收者
            recipient_agent = self.agents[recipient]
            recipient_agent.receive_message(message)
            
            return CommunicationResult(
                success=True,
                message=f"Message sent to '{recipient}' successfully",
                data={"message_id": str(hash(content + str(datetime.now())))}
            )
        except Exception as e:
            return CommunicationResult(
                success=False,
                message=f"Failed to send message to '{recipient}'",
                error=str(e)
            )
    
    def broadcast_message(self, 
                         sender: str, 
                         content: str, 
                         metadata: Optional[Dict[str, Any]] = None,
                         exclude: Optional[List[str]] = None) -> List[CommunicationResult]:
        """广播消息给所有Agent"""
        exclude = exclude or []
        results = []
        
        for agent_name in self.agents:
            if agent_name not in exclude:
                result = self.send_message(sender, agent_name, content, metadata)
                results.append(result)
        
        return results
    
    def subscribe_to_topic(self, agent_name: str, topic: str, handler: Callable):
        """订阅特定主题的消息"""
        topic_key = f"{agent_name}:{topic}"
        self.message_handlers[topic_key] = handler
    
    def publish_to_topic(self, 
                        sender: str, 
                        topic: str, 
                        content: str, 
                        metadata: Optional[Dict[str, Any]] = None) -> List[CommunicationResult]:
        """发布消息到特定主题"""
        results = []
        
        # 找到订阅该主题的所有Agent
        for handler_key, handler in self.message_handlers.items():
            if topic in handler_key:
                agent_name = handler_key.split(':')[0]
                try:
                    result = handler(content, metadata)
                    results.append(CommunicationResult(
                        success=True,
                        message=f"Published to topic '{topic}' for agent '{agent_name}'",
                        data=result
                    ))
                except Exception as e:
                    results.append(CommunicationResult(
                        success=False,
                        message=f"Failed to publish to topic '{topic}' for agent '{agent_name}'",
                        error=str(e)
                    ))
        
        return results
    
    def get_message_history(self, 
                           agent_name: str, 
                           limit: int = 10) -> List[Message]:
        """获取特定Agent的消息历史"""
        agent = self.agents.get(agent_name)
        if agent and hasattr(agent, 'history'):
            return agent.history[-limit:] if len(agent.history) >= limit else agent.history
        return []
    
    async def process_message_queue(self):
        """异步处理消息队列"""
        while self.message_queue:
            message = self.message_queue.pop(0)
            
            # 如果有专门的处理器，则使用它
            handler_key = f"{message.recipient}:{message.metadata.get('topic', 'default') if message.metadata else 'default'}"
            if handler_key in self.message_handlers:
                handler = self.message_handlers[handler_key]
                try:
                    await handler(message)
                except Exception as e:
                    print(f"Error processing message with handler {handler_key}: {e}")
            else:
                # 否则直接传递给接收者
                recipient_agent = self.agents.get(message.recipient)
                if recipient_agent:
                    recipient_agent.receive_message(message)
            
            await asyncio.sleep(0.01)  # 给其他任务一些时间