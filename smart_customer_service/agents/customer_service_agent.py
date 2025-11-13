import sys
import os
# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent
from knowledge.rag_system import RAGSystem
from core.goal_manager import GoalManager, GoalStatus
from core.exception_handler import ExceptionHandler, ExceptionType, RecoveryStrategy


class CustomerServiceAgent(BaseAgent):
    """客服Agent，集成所有功能"""
    
    def __init__(self, 
                 name: str, 
                 rag_system: RAGSystem,
                 goal_manager: GoalManager,
                 exception_handler: ExceptionHandler):
        super().__init__(name, "智能客服Agent")
        self.rag_system = rag_system
        self.goal_manager = goal_manager
        self.exception_handler = exception_handler
        
        # 注册内部工具
        self.add_tool("search_knowledge_base", self._search_knowledge_base)
        self.add_tool("create_goal", self._create_goal)
        self.add_tool("escalate_to_human", self._escalate_to_human)
    
    def _search_knowledge_base(self, query: str) -> Dict[str, Any]:
        """搜索知识库"""
        try:
            result = self.rag_system.get_answer(query)
            if result:
                return {
                    "success": True,
                    "answer": result["answer"],
                    "confidence": result.get("similarity", 0.0),
                    "source": "knowledge_base"
                }
            else:
                return {
                    "success": False,
                    "answer": "抱歉，我没有在知识库中找到相关信息。",
                    "confidence": 0.0,
                    "source": "knowledge_base"
                }
        except Exception as e:
            exception_info = self.exception_handler.handle_exception(
                e, 
                {"query": query, "operation": "search_knowledge_base"}
            )
            return {
                "success": False,
                "answer": "知识库搜索出现错误",
                "error": str(e),
                "recovery_strategy": exception_info.recovery_strategy.value
            }
    
    def _create_goal(self, goal_id: str, description: str) -> Dict[str, Any]:
        """创建目标"""
        try:
            goal = self.goal_manager.create_goal(goal_id, description)
            return {
                "success": True,
                "goal_id": goal.id,
                "description": goal.description,
                "status": goal.status.value
            }
        except Exception as e:
            exception_info = self.exception_handler.handle_exception(
                e, 
                {"goal_id": goal_id, "description": description, "operation": "create_goal"}
            )
            return {
                "success": False,
                "error": str(e),
                "recovery_strategy": exception_info.recovery_strategy.value
            }
    
    def _escalate_to_human(self, issue_description: str) -> Dict[str, Any]:
        """升级到人工客服"""
        self.log(f"正在将问题转人工: {issue_description}")
        return {
            "success": True,
            "message": "已将您的问题转给人工客服，他们将尽快与您联系。",
            "escalation_id": f"ESC-{hash(issue_description)}",
            "status": "escalated"
        }
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理客户请求"""
        try:
            customer_query = input_data.get("query", "")
            customer_id = input_data.get("customer_id", "unknown")
            
            self.log(f"收到客户 {customer_id} 的请求: {customer_query}")
            
            # 创建处理目标
            goal_id = f"process_{hash(customer_query)}"
            self.goal_manager.create_goal(
                goal_id=goal_id,
                description=f"处理客户 {customer_id} 的请求: {customer_query}"
            )
            
            # 尝试从知识库获取答案
            kb_result = self.tools["search_knowledge_base"](customer_query)
            
            if kb_result["success"] and kb_result["confidence"] > 0.7:
                # 高置信度答案，直接返回
                self.goal_manager.update_goal_status(goal_id, GoalStatus.COMPLETED)
                return {
                    "response": kb_result["answer"],
                    "source": kb_result["source"],
                    "confidence": kb_result["confidence"],
                    "goal_status": "completed"
                }
            else:
                # 低置信度或无答案，考虑升级到人工
                self.log("知识库中未找到高置信度答案，考虑升级到人工客服")
                
                # 尝试理解客户意图
                if self._needs_human_assistance(customer_query):
                    escalation_result = self.tools["escalate_to_human"](customer_query)
                    self.goal_manager.update_goal_status(goal_id, GoalStatus.COMPLETED)
                    
                    return {
                        "response": escalation_result["message"],
                        "escalation_id": escalation_result["escalation_id"],
                        "source": "human_agent",
                        "goal_status": "escalated"
                    }
                else:
                    # 尝试提供更多帮助
                    self.goal_manager.update_goal_status(goal_id, GoalStatus.COMPLETED)
                    fallback_response = kb_result.get("answer", "抱歉，我暂时无法解决这个问题。")
                    return {
                        "response": fallback_response,
                        "source": kb_result.get("source", "fallback"),
                        "confidence": kb_result.get("confidence", 0.0),
                        "goal_status": "completed_with_limitations"
                    }
                    
        except Exception as e:
            exception_info = self.exception_handler.handle_exception(
                e, 
                {"input_data": input_data, "operation": "process_customer_request"}
            )
            
            # 尝试恢复
            recovery_result = self.exception_handler.apply_recovery_strategy(
                exception_info,
                self._handle_process_exception,
                input_data
            )
            
            if recovery_result:
                return recovery_result
            else:
                return {
                    "response": "处理请求时出现错误，请稍后重试或联系人工客服。",
                    "error": str(e),
                    "recovery_strategy": exception_info.recovery_strategy.value
                }
    
    def _needs_human_assistance(self, query: str) -> bool:
        """判断是否需要人工协助"""
        # 简单的规则：如果查询包含以下关键词，可能需要人工协助
        human_assist_keywords = [
            "投诉", "紧急", "复杂", "特殊", "定制", "故障", "异常", "无法解决"
        ]
        
        query_lower = query.lower()
        for keyword in human_assist_keywords:
            if keyword in query_lower:
                return True
        
        # 如果查询长度超过一定限制，也考虑人工协助
        if len(query) > 200:
            return True
            
        return False
    
    def _handle_process_exception(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理处理过程中的异常"""
        return {
            "response": "处理过程中出现临时问题，正在尝试其他解决方案...",
            "source": "system_recovery",
            "recovery_attempt": True
        }