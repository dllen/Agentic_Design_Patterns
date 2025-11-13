import asyncio
import sys
import os
# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from typing import Dict, Any
from agents.customer_service_agent import CustomerServiceAgent
from agents.specialized_agents.tech_support_agent import TechSupportAgent
from agents.specialized_agents.billing_agent import BillingAgent
from agents.specialized_agents.escalation_agent import EscalationAgent
from knowledge.rag_system import RAGSystem, KnowledgeBase
from core.goal_manager import GoalManager
from core.exception_handler import ExceptionHandler
from core.communication_hub import CommunicationHub


def main():
    """主函数：运行智能客服助手系统"""
    print("=== 智能客服助手系统启动 ===\n")
    
    # 1. 初始化核心组件
    print("1. 初始化核心组件...")
    knowledge_base = KnowledgeBase()
    rag_system = RAGSystem(knowledge_base)
    goal_manager = GoalManager()
    exception_handler = ExceptionHandler()
    communication_hub = CommunicationHub()
    
    # 2. 创建Agent实例
    print("2. 创建Agent实例...")
    customer_service_agent = CustomerServiceAgent(
        name="CustomerServiceAgent",
        rag_system=rag_system,
        goal_manager=goal_manager,
        exception_handler=exception_handler
    )
    
    tech_support_agent = TechSupportAgent()
    billing_agent = BillingAgent()
    escalation_agent = EscalationAgent()
    
    # 3. 注册Agent到通信中心
    print("3. 注册Agent到通信中心...")
    communication_hub.register_agent(customer_service_agent.name, customer_service_agent)
    communication_hub.register_agent(tech_support_agent.name, tech_support_agent)
    communication_hub.register_agent(billing_agent.name, billing_agent)
    communication_hub.register_agent(escalation_agent.name, escalation_agent)
    
    # 4. 运行简单测试
    print("\n4. 运行系统测试...")
    
    # 测试1: 简单查询
    print("\n--- 测试1: 简单查询 ---")
    test_input1 = {
        "query": "如何重置密码？",
        "customer_id": "CUST001"
    }
    result1 = customer_service_agent.process(test_input1)
    print(f"查询: {test_input1['query']}")
    print(f"响应: {result1['response']}")
    print(f"来源: {result1.get('source', 'unknown')}")
    
    # 测试2: 需要升级的问题
    print("\n--- 测试2: 需要升级的问题 ---")
    test_input2 = {
        "query": "我遇到了复杂的技术故障，需要紧急处理",
        "customer_id": "CUST002"
    }
    result2 = customer_service_agent.process(test_input2)
    print(f"查询: {test_input2['query']}")
    print(f"响应: {result2['response']}")
    if 'escalation_id' in result2:
        print(f"升级ID: {result2['escalation_id']}")
    
    # 测试3: 计费相关查询
    print("\n--- 测试3: 计费相关查询 ---")
    billing_query = {
        "query": "支持哪些支付方式？",
        "customer_id": "CUST003"
    }
    result3 = customer_service_agent.process(billing_query)
    print(f"查询: {billing_query['query']}")
    print(f"响应: {result3['response']}")
    
    # 5. 显示目标管理器状态
    print("\n5. 目标管理器状态:")
    goal_report = goal_manager.get_goal_report()
    print(f"总目标数: {goal_report['total_goals']}")
    print(f"活跃目标数: {goal_report['active_goals']}")
    print(f"已完成目标数: {goal_report['completed_goals']}")
    print(f"完成率: {goal_report['completion_rate']:.2%}")
    
    # 6. 显示通信历史
    print("\n6. 通信历史 (客服Agent):")
    history = communication_hub.get_message_history(customer_service_agent.name, limit=5)
    for i, msg in enumerate(history):
        print(f"  {i+1}. [{msg.timestamp.strftime('%H:%M:%S')}] {msg.sender} -> {msg.recipient}: {msg.content[:50]}...")
    
    print("\n=== 智能客服助手系统测试完成 ===")
    
    # 7. 持续运行演示
    print("\n7. 演示持续运行和监控...")
    
    # 创建一个持续监控任务
    async def monitor_continuously():
        while True:
            # 检查目标状态
            monitoring_result = goal_manager.monitor_goals()
            if monitoring_result:
                print(f"\n监控发现 {len(monitoring_result)} 个需要关注的目标:")
                for alert in monitoring_result:
                    print(f"  - {alert['message']}")
            
            # 等待一段时间
            await asyncio.sleep(10)  # 每10秒检查一次
    
    # 运行监控（在实际应用中，这将在后台运行）
    print("\n按 Ctrl+C 停止监控...")
    try:
        asyncio.run(monitor_continuously())
    except KeyboardInterrupt:
        print("\n系统已停止")


if __name__ == "__main__":
    main()