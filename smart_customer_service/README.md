# 智能客服助手系统

## 项目概述

智能客服助手是一个基于Agentic设计模式的多Agent系统，旨在提供高效、智能的客户服务支持。系统集成了知识检索、目标管理、异常处理和人机协作等多种现代AI技术。

## 项目架构

### 整体架构

```
smart_customer_service/
├── agents/                      # Agent组件
│   ├── base_agent.py           # 基础Agent框架
│   ├── customer_service_agent.py # 主客服Agent
│   └── specialized_agents/     # 专业Agent
│       ├── tech_support_agent.py
│       ├── billing_agent.py
│       └── escalation_agent.py
├── core/                       # 核心功能模块
│   ├── goal_manager.py         # 目标管理器
│   ├── exception_handler.py    # 异常处理器
│   └── communication_hub.py    # 通信中心
├── knowledge/                  # 知识管理模块
│   ├── knowledge_base.py       # 知识库
│   └── rag_system.py           # RAG系统
├── tools/                      # 工具模块
├── requirements.txt            # 依赖包
├── main.py                     # 主程序入口
└── README.md                   # 项目说明文档
```

### 核心模块说明

#### 1. Agent模块
- **BaseAgent**: 所有Agent的基类，提供基础功能如消息传递、工具管理等
- **CustomerServiceAgent**: 主客服Agent，负责处理客户请求，集成所有功能
- **Specialized Agents**: 专业Agent，分别处理技术支持、计费问题和升级请求

#### 2. 核心模块
- **GoalManager**: 管理系统目标的生命周期，包括创建、跟踪、监控和完成
- **ExceptionHandler**: 处理系统异常，提供多种恢复策略
- **CommunicationHub**: 管理Agent间通信，支持消息传递和广播

#### 3. 知识管理模块
- **KnowledgeBase**: 存储FAQ等知识数据
- **RAGSystem**: 检索增强生成系统，提供智能问答能力

## 本地开发调试

### 环境要求

- Python 3.8+
- pip 包管理器

### 环境设置

1. 克隆项目到本地
2. 创建虚拟环境（推荐）：
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   # 或
   venv\Scripts\activate     # Windows
   ```

3. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```

### 运行系统

基本运行：
```bash
cd smart_customer_service
python main.py
```

### 调试指南

#### 1. 调试Agent行为
所有Agent都有内置的日志功能，可以通过查看控制台输出来跟踪Agent行为：

```python
# 在Agent中添加日志
self.log("处理客户请求: " + query)
```

#### 2. 调试目标管理
使用GoalManager的报告功能查看目标状态：
```python
report = goal_manager.get_goal_report()
print(f"完成率: {report['completion_rate']:.2%}")
```

#### 3. 调试异常处理
ExceptionHandler会记录所有异常，通过监控日志可以跟踪异常处理过程：
```python
exception_info = exception_handler.handle_exception(e, context)
print(f"异常类型: {exception_info.exception_type}")
print(f"恢复策略: {exception_info.recovery_strategy}")
```

#### 4. 调试通信系统
使用CommunicationHub的消息历史功能：
```python
history = communication_hub.get_message_history(agent_name, limit=10)
for msg in history:
    print(f"[{msg.timestamp}] {msg.sender} -> {msg.recipient}: {msg.content}")
```

### 扩展开发

#### 添加新的专业Agent
1. 在 `agents/specialized_agents/` 目录下创建新的Agent文件
2. 继承 `SpecializedAgent` 或 `BaseAgent`
3. 实现 `process` 方法
4. 在 `main.py` 中注册到通信中心

#### 扩展知识库
1. 修改 `knowledge_base.py` 中的 `_init_default_data` 方法添加新数据
2. 或者使用 `load_data` 方法从外部文件加载数据

#### 添加新工具
在Agent中使用 `add_tool` 方法添加新工具：
```python
def my_tool_function(param):
    return "result"

agent.add_tool("my_tool", my_tool_function)
```

### 测试用例

运行系统后，会自动执行以下测试：
1. 简单查询测试
2. 需要升级的问题测试
3. 计费相关查询测试

## 设计模式应用

### 1. 提示链 (Prompt Chaining)
- 在CustomerServiceAgent中实现多步骤处理逻辑

### 2. 模型上下文协议 (MCP)  
- 通过工具集成实现Agent与外部系统通信

### 3. 目标设定与监控
- GoalManager模块实现目标生命周期管理

### 4. 异常处理与恢复
- ExceptionHandler提供多种恢复策略

### 5. 人机协作
- 自动将复杂问题升级到人工客服

### 6. 知识检索 (RAG)
- RAGSystem提供智能问答能力

### 7. Agent间通信
- CommunicationHub管理Agent间消息传递

## 依赖说明

- `numpy`: 数值计算
- `scikit-learn`: 机器学习算法（相似度计算）
- `torch`: 深度学习框架（预留用于真实嵌入模型）
- `transformers`: 预训练模型（预留用于真实嵌入模型）

## 注意事项

1. 本项目中的嵌入模型使用随机向量模拟，在生产环境中应替换为真实的嵌入模型
2. 系统设计为可扩展，可以根据需要添加更多专业Agent
3. 异常处理策略可根据实际业务需求调整
4. 通信系统支持异步处理，可在高并发场景中使用

## 未来扩展

1. 集成真实的嵌入模型（如Sentence-BERT）
2. 添加更多的专业Agent类型
3. 增强目标管理的复杂任务分解能力
4. 添加更智能的路由机制
5. 集成更多外部服务和API