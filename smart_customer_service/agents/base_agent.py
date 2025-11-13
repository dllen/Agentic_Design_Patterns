from abc import ABC, abstractmethod
import sys
import os
# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Message:
    """消息类，用于Agent间通信"""
    sender: str
    recipient: str
    content: str
    timestamp: datetime = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class BaseAgent(ABC):
    """基础Agent类"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.history: List[Message] = []
        self.tools: Dict[str, callable] = {}
        
    def add_tool(self, name: str, tool: callable):
        """添加工具到Agent"""
        self.tools[name] = tool
        
    def send_message(self, recipient: str, content: str, metadata: Dict[str, Any] = None) -> Message:
        """发送消息"""
        message = Message(
            sender=self.name,
            recipient=recipient,
            content=content,
            metadata=metadata or {}
        )
        self.history.append(message)
        return message
        
    def receive_message(self, message: Message):
        """接收消息"""
        self.history.append(message)
        
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理输入并返回结果"""
        pass
        
    def log(self, message: str):
        """日志记录"""
        print(f"[{self.name}] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")