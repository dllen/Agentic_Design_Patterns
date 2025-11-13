# 附录C：代理框架概述 (Overview of Agent Frameworks)

## 概述
代理框架为构建、部署和管理代理系统提供了基础结构和工具。本附录概述了当前流行的各种代理框架及其特点、优势和适用场景。

## 主要代理框架

### 1. LangGraph
LangGraph是专为构建状态化、多代理应用而设计的框架。

**特点**：
- 图形化代理结构
- 状态管理
- 支持人类参与
- 可中断工作流

**代码示例**：
```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, List

class AgentState(TypedDict):
    messages: List[str]
    current_step: str
    completed: bool

def agent_node(state):
    # 代理节点逻辑
    return {"current_step": "processing", "completed": False}

def decision_node(state):
    # 决策节点逻辑
    if state["current_step"] == "processing":
        return "next_agent"
    else:
        return END

# 构建图
workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("decision", decision_node)
workflow.set_entry_point("agent")
workflow.add_edge("agent", "decision")
workflow.add_conditional_edges(
    "decision",
    lambda x: x["current_step"],
    {"next_agent": "agent", END: END}
)

app = workflow.compile()
```

**优势**：
- 强大的状态管理
- 可视化调试
- 适合复杂多代理工作流

### 2. AutoGen
AutoGen由微软开发，专注于多代理协作。

**特点**：
- 群聊机制
- 人类参与者集成
- 代码执行能力
- 可定制代理

**代码示例**：
```python
import autogen

# 配置LLM
config_list = [
    {
        "model": "gpt-4",
        "api_key": "YOUR_API_KEY",
    }
]

# 创建代理
user_proxy = autogen.UserProxyAgent(
    name="Admin",
    system_message="A human admin.",
    code_execution_config=False,
    human_input_mode="TERMINATE",
)

assistant = autogen.AssistantAgent(
    name="Assistant",
    llm_config={"config_list": config_list},
)

# 开始对话
user_proxy.initiate_chat(
    assistant,
    message="如何使用Python实现快速排序算法？"
)
```

**优势**：
- 优秀的多代理通信
- 代码执行环境
- 灵活的对话管理

### 3. CrewAI
CrewAI专注于创建协作代理团队。

**特点**：
- 角色定义
- 任务分配
- 工具使用
- 协作工作流

**代码示例**：
```python
from crewai import Agent, Task, Crew

# 定义代理
researcher = Agent(
    role='资深研究员',
    goal='搜集关于AI的最新趋势',
    backstory='你是一个经验丰富的研究员，擅长分析科技趋势。',
    verbose=True
)

writer = Agent(
    role='内容作家',
    goal='根据研究结果撰写文章',
    backstory='你是一个专业作家，擅长将复杂概念简化为易懂的内容。',
    verbose=True
)

# 定义任务
research_task = Task(
    description='研究AI在2024年的最新趋势',
    agent=researcher
)

writing_task = Task(
    description='基于研究结果撰写一篇博客文章',
    agent=writer
)

# 创建Crew
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    verbose=2
)

# 执行
result = crew.kickoff()
print(result)
```

**优势**：
- 直观的团队协作模型
- 简单的任务定义
- 良好的可扩展性

### 4. LlamaIndex
LlamaIndex专注于数据索引和检索增强生成(RAG)。

**特点**：
- 强大的数据连接器
- 灵活的索引选项
- RAG管道
- 代理集成

**代码示例**：
```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.openai import OpenAI

# 加载文档
documents = SimpleDirectoryReader("data").load_data()

# 创建索引
index = VectorStoreIndex.from_documents(documents)

# 创建查询引擎
llm = OpenAI(model="gpt-3.5-turbo")
query_engine = index.as_query_engine(llm=llm)

# 查询
response = query_engine.query("文档中提到的关键点是什么？")
print(response)
```

**优势**：
- 优秀的信息检索能力
- 丰富的数据连接器
- 灵活的索引策略

### 5. Haystack
Haystack是一个开源框架，专注于NLP和搜索应用。

**特点**：
- 模块化管道
- 搜索和问答
- 文档存储
- 可扩展组件

**代码示例**：
```python
from haystack import Pipeline
from haystack.nodes import BM25Retriever, PromptNode
from haystack.document_stores import InMemoryDocumentStore

# 创建文档存储
document_store = InMemoryDocumentStore()
docs = [
    {"content": "自然语言处理是AI的重要分支"},
    {"content": "机器学习算法需要大量数据"},
    {"content": "深度学习在图像识别中表现优异"}
]
document_store.write_documents(docs)

# 创建检索器和生成器
retriever = BM25Retriever(document_store=document_store)
prompt_node = PromptNode(default_prompt_template="question-answering-with-retrieval")

# 创建管道
query_pipeline = Pipeline()
query_pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
query_pipeline.add_node(component=prompt_node, name="PromptNode", inputs=["Retriever"])

# 运行查询
result = query_pipeline.run(query="什么是自然语言处理？", params={"Retriever": {"top_k": 1}})
print(result["answers"][0].answer)
```

**优势**：
- 模块化设计
- 强大的检索能力
- 开源和可定制

### 6. Semantic Kernel
Microsoft的Semantic Kernel提供AI集成能力。

**特点**：
- 插件系统
- 内存管理
- 提示工程
- 多语言支持

**代码示例**：
```python
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

# 初始化内核
kernel = sk.Kernel()

# 添加AI服务
api_key = "YOUR_API_KEY"
kernel.add_chat_service("chat-gpt", OpenAIChatCompletion("gpt-3.5-turbo", api_key))

# 创建提示
prompt = "解释量子计算的概念，使用简单的术语。"
result = kernel.run(
    kernel.func_from_prompt(prompt_template=prompt, description="A function that explains quantum computing")
)
print(result)
```

**优势**：
- 优秀的插件架构
- 内存管理功能
- 多AI服务支持

## 选择框架的考虑因素

### 1. 项目需求
- 单代理 vs 多代理
- 信息检索需求
- 需要的交互复杂度

### 2. 技术要求
- 编程语言偏好
- 部署环境
- 性能需求

### 3. 团队技能
- Python/JavaScript熟练度
- 对特定框架的熟悉程度
- 学习曲线接受度

## 比较矩阵

| 框架 | 多代理支持 | RAG能力 | 易学性 | 生态系统 | 适用场景 |
|------|------------|---------|--------|----------|----------|
| LangGraph | 高 | 中 | 中 | 中 | 复杂状态工作流 |
| AutoGen | 高 | 高 | 中 | 高 | 多代理协作 |
| CrewAI | 高 | 中 | 高 | 高 | 团队协作任务 |
| LlamaIndex | 低 | 高 | 高 | 高 | 数据驱动应用 |
| Haystack | 中 | 高 | 中 | 中 | 搜索应用 |
| Semantic Kernel | 中 | 中 | 中 | 中 | 企业AI集成 |

## 最佳实践

### 1. 框架选择
- 根据具体用例需求选择
- 考虑长期维护性
- 评估社区支持

### 2. 实施策略
- 从小规模开始
- 渐进式复杂化
- 充分测试

## 总结
选择正确的代理框架对项目成功至关重要。不同框架适用于不同场景，了解每个框架的特点和优势有助于做出最佳选择。随着代理技术的不断发展，框架也在持续演进，需要保持对新技术的关注和评估。