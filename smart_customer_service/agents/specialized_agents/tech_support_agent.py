import sys
import os
# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any
from agents.base_agent import BaseAgent


class SpecializedAgent(BaseAgent):
    """专业Agent基类"""
    
    def __init__(self, name: str, specialization: str, description: str = ""):
        super().__init__(name, description)
        self.specialization = specialization


class TechSupportAgent(SpecializedAgent):
    """技术支持Agent"""
    
    def __init__(self):
        super().__init__(
            name="TechSupportAgent", 
            specialization="technical_support",
            description="处理技术问题和支持请求"
        )
        self.knowledge_base = {
            "connection_issues": "请检查网络连接，重启路由器，或联系网络服务提供商。",
            "software_bugs": "请提供详细错误信息，我们会尽快修复。",
            "hardware_problems": "建议联系硬件供应商或查看保修政策。"
        }
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        self.log("处理技术支持请求")
        
        query = input_data.get("query", "").lower()
        
        if "连接" in query or "网络" in query or "connection" in query:
            return {
                "response": self.knowledge_base["connection_issues"],
                "specialization": self.specialization,
                "confidence": 0.9
            }
        elif "错误" in query or "bug" in query or "crash" in query:
            return {
                "response": self.knowledge_base["software_bugs"],
                "specialization": self.specialization,
                "confidence": 0.85
            }
        elif "硬件" in query or "设备" in query or "hardware" in query:
            return {
                "response": self.knowledge_base["hardware_problems"],
                "specialization": self.specialization,
                "confidence": 0.8
            }
        else:
            return {
                "response": "我是技术支持专家，可以帮您解决技术问题，请详细描述您遇到的问题。",
                "specialization": self.specialization,
                "confidence": 0.7
            }


class BillingAgent(SpecializedAgent):
    """计费Agent"""
    
    def __init__(self):
        super().__init__(
            name="BillingAgent", 
            specialization="billing",
            description="处理计费和支付相关问题"
        )
        self.knowledge_base = {
            "payment_methods": "支持支付宝、微信、银行卡等多种支付方式。",
            "refund_policy": "支持7天无理由退款，需在订单完成后7天内申请。",
            "invoice": "可在账户页面下载电子发票。"
        }
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        self.log("处理计费请求")
        
        query = input_data.get("query", "").lower()
        
        if "支付" in query or "付款" in query or "payment" in query:
            return {
                "response": self.knowledge_base["payment_methods"],
                "specialization": self.specialization,
                "confidence": 0.9
            }
        elif "退款" in query or "refund" in query:
            return {
                "response": self.knowledge_base["refund_policy"],
                "specialization": self.specialization,
                "confidence": 0.85
            }
        elif "发票" in query or "invoice" in query:
            return {
                "response": self.knowledge_base["invoice"],
                "specialization": self.specialization,
                "confidence": 0.8
            }
        else:
            return {
                "response": "我是计费专家，可以帮您解决支付和发票相关问题。",
                "specialization": self.specialization,
                "confidence": 0.7
            }


class EscalationAgent(SpecializedAgent):
    """升级Agent"""
    
    def __init__(self):
        super().__init__(
            name="EscalationAgent", 
            specialization="escalation",
            description="处理需要人工介入的复杂问题"
        )
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        self.log("处理升级请求")
        
        query = input_data.get("query", "")
        customer_id = input_data.get("customer_id", "unknown")
        
        # 创建工单
        ticket_id = f"TICKET-{hash(query + customer_id)}"
        
        return {
            "response": f"已为您创建工单 {ticket_id}，专业客服将尽快与您联系处理此问题。",
            "ticket_id": ticket_id,
            "specialization": self.specialization,
            "escalation": True
        }