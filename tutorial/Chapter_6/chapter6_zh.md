# 第6章：规划 (Planning)

## 模式概述
规划（Planning）是智能代理系统中的一个关键设计模式，它使代理能够制定策略或计划来完成复杂任务。这种模式允许代理在执行实际操作之前分解问题、确定子任务的顺序，并考虑执行过程中可能出现的依赖关系。

规划模式的核心思想是创建一个结构化的行动计划，指导代理完成目标。这包括识别所需的步骤、确定它们的执行顺序、预测潜在障碍以及制定应对策略。通过在执行前进行规划，代理可以更高效、更有组织地处理复杂任务。

通过实施规划，代理可以显著提高其在复杂任务中的成功率，减少执行时间，并更好地管理资源。这种模式对于需要多步骤协调或具有依赖关系的任务特别有价值。

## 核心概念
1. **任务分解**：将复杂目标分解为更小、更易管理的子任务。
2. **顺序规划**：确定子任务的执行顺序和依赖关系。
3. **策略制定**：创建完成任务的详细行动计划。
4. **适应性规划**：在执行过程中根据需要调整和修改计划。

## 实际应用
规划模式广泛应用于各种场景，包括：
- 项目管理和任务调度
- 自动化工作流管理
- 复杂问题解决
- 资源分配和优化
- 长期目标实现

## 代码示例

### 使用CrewAI的计划和编写代理

```python
import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

# 从.env文件加载环境变量以确保安全
load_dotenv()

# 1. 明确定义语言模型
llm = ChatOpenAI(model="gpt-4-turbo")

# 2. 定义清晰专注的代理
planner_writer_agent = Agent(
    role='文章规划和编写员',
    goal='规划并编写关于指定主题的简明、引人入胜的摘要',
    backstory=(
        '您是专业的技术作家和内容策略师。 '
        '您的优势在于在编写前创建清晰的行动计划，'
        '确保最终摘要既有信息量又易于理解。'
    ),
    verbose=True,
    allow_delegation=False,
    llm=llm # 将特定LLM分配给代理
)

# 3. 定义具有更结构化和特定预期输出的任务
topic = "强化学习在AI中的重要性"
high_level_task = Task(
    description=(
        f"1. 为关于主题的摘要创建一个要点计划：'{topic}'\\n"
        f"2. 根据您的计划编写摘要，保持在200字左右。"
    ),
    expected_output=(
        "包含两个不同部分的最终报告：\\n\\n"
        "### 计划\\n"
        "- 概要主要要点的项目列表。\\n\\n"
        "### 摘要\\n"
        "- 关于主题的简明和结构良好的摘要。"
    ),
    agent=planner_writer_agent,
)

# 创建具有清晰流程的团队
crew = Crew(
    agents=[planner_writer_agent],
    tasks=[high_level_task],
    process=Process.sequential,
)

# 执行任务
print("## 运行规划和编写任务 ##")
result = crew.kickoff()

print("\\n\\n---\\n## 任务结果 ##\\n---")
print(result)
```

### 更复杂的规划示例

```python
import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

load_dotenv()

# 定义多个代理进行复杂规划
llm = ChatOpenAI(model="gpt-4-turbo")

researcher = Agent(
    role="研究分析师",
    goal="收集关于指定主题的全面信息",
    backstory="您是经验丰富的研究分析师，擅长收集和分析复杂主题的信息。",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

planner = Agent(
    role="项目规划师",
    goal="为项目制定详细的战略计划",
    backstory="您是精通创建高效、可执行项目计划的规划专家。",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

writer = Agent(
    role="内容编写员",
    goal="根据研究和计划创建高质量内容",
    backstory="您是擅长将复杂信息转化为清晰、引人入胜内容的专业作家。",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# 定义相互依赖的任务

# 研究任务
research_task = Task(
    description="对'AI在医疗保健中的应用'进行全面研究，包括主要优势、挑战和未来趋势。",
    expected_output="一份包含关键发现的详细报告，至少包含5个主要优势、3个主要挑战和2个未来趋势。",
    agent=researcher,
)

# 规划任务 - 依赖于研究结果
planning_task = Task(
    description="基于研究结果，为部署AI医疗解决方案制定详细的战略计划。包括实施阶段、时间表和资源需求。",
    expected_output="一个包含至少4个实施阶段、每个阶段的预计时间表和所需资源的详细计划。",
    agent=planner,
    context=[research_task]  # 规划任务依赖于研究任务的输出
)

# 编写任务 - 依赖于研究和规划结果
writing_task = Task(
    description="创建一份全面报告，总结研究发现和实施计划。使内容易于医疗专业人员理解。",
    expected_output="一份综合报告，包含研究摘要、实施计划和预期结果，不少于1000字。",
    agent=writer,
    context=[research_task, planning_task]  # 写作任务依赖于研究和规划任务的输出
)

# 创建顺序执行的团队
project_crew = Crew(
    agents=[researcher, planner, writer],
    tasks=[research_task, planning_task, writing_task],
    process=Process.sequential,
)

print("## 运行复杂规划项目 ##")
result = project_crew.kickoff()

print("\\n\\n---\\n## 项目结果 ##\\n---")
print(result)
```

### 使用OpenAI Deep Research API的高级规划示例

```python
from openai import OpenAI

# 使用API密钥初始化客户端
client = OpenAI(api_key="YOUR_OPENAI_API_KEY")

# 定义代理的角色和用户的研究问题
system_message = """You are a professional researcher preparing a structured, data-driven report.
Focus on data-rich insights, use reliable sources, and include inline citations."""
user_query = "Research the economic impact of semaglutide on global healthcare systems."

# 创建深度研究API调用
response = client.responses.create(
  model="o3-deep-research-2025-06-26",
  input=[
    {
      "role": "developer",
      "content": [{"type": "input_text", "text": system_message}]
    },
    {
      "role": "user",
      "content": [{"type": "input_text", "text": user_query}]
    }
  ],
  reasoning={"summary": "auto"},
  tools=[{"type": "web_search_preview"}]
)

# 访问并打印响应中的最终报告
final_report = response.output[-1].content[0].text
print(final_report)

# --- 访问内联引用和元数据 ---
print("--- 引用 ---")
annotations = response.output[-1].content[0].annotations

if not annotations:
    print("报告中未找到注释。")
else:
    for i, citation in enumerate(annotations):
        # 引用所指的文本范围
        cited_text = final_report[citation.start_index:citation.end_index]

        print(f"引用 {i+1}:")
        print(f"  引用文本: {cited_text}")
        print(f"  标题: {citation.title}")
        print(f"  URL: {citation.url}")
        print(f"  位置: 字符 {citation.start_index}–{citation.end_index}")
print("\\n" + "="*50 + "\\n")


# --- 检查中间步骤 ---
print("--- 中间步骤 ---")

# 1. 推理步骤: 模型生成的内部计划和摘要。
try:
    reasoning_step = next(item for item in response.output if item.type == "reasoning")
    print("\\n[找到推理步骤]")
    for summary_part in reasoning_step.summary:
        print(f"  - {summary_part.text}")
except StopIteration:
    print("\\n未找到推理步骤。")

# 2. 网络搜索调用: 代理执行的确切搜索查询。
try:
    search_step = next(item for item in response.output if item.type == "web_search_call")
    print("\\n[找到网络搜索调用]")
    print(f"  执行的查询: '{search_step.action['query']}'")
    print(f"  状态: {search_step.status}")
except StopIteration:
    print("\\n未找到网络搜索步骤。")

# 3. 代码执行: 代理使用代码解释器运行的任何代码。
try:
    code_step = next(item for item in response.output if item.type == "code_interpreter_call")
    print("\\n[找到代码执行步骤]")
    print("  代码输入:")
    print(f"  ```python\\n{code_step.input}\\n  ```")
    print("  代码输出:")
    print(f"  {code_step.output}")
except StopIteration:
    print("\\n未找到代码执行步骤。")
```

这个示例展示了如何使用OpenAI的深度研究API进行高级规划和研究任务，包括对中间步骤和引用的访问，这使得代理能够进行更深入、更透明的规划过程。

## 最佳实践
1. **清晰目标定义**：在开始规划前明确定义目标和预期结果。
2. **任务分解**：将复杂任务分解为可管理的子任务。
3. **依赖关系管理**：正确识别和管理任务之间的依赖关系。
4. **时间估计**：为每个任务提供现实的时间估计。
5. **风险评估**：识别潜在风险并制定缓解策略。

## 总结
规划模式是构建智能代理的关键技术，它使代理能够战略性地处理复杂任务。通过实施有效的规划，代理可以更高效地实现目标，更好地管理资源，并在复杂环境中表现出更高的成功率。这种模式对于需要多步骤协调和复杂决策的任务特别重要。