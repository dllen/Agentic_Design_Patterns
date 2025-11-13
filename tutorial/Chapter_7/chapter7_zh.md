# 第7章：多代理协作 (Multi-Agent Collaboration)

## 模式概述
多代理协作代表AI开发中的重要范式转变，从追求单一的全能超级代理转向复杂协作多代理系统的兴起。这种方法认识到，复杂挑战通常最好由协同工作的专家团队而非单一通才来解决。这种模式直接反映了人类组织的结构，其中不同部门被分配特定角色并协作解决多面目标。这种系统的集体优势在于劳动分工和通过协调努力创造的协同效应。

## 核心概念
1. **劳动分工**：不同代理专门负责特定任务或功能。
2. **协调合作**：代理之间的无缝通信和信息共享。
3. **集中协调**：使用中央协调器来管理任务分配和流程。
4. **专业化**：每个代理专注于特定领域，提高整体效率。

## 实际应用
以启动新产品的复杂工作流程为例。与其让一个代理尝试处理每个方面，不如让"项目经理"代理作为中央协调器。这个管理者通过将任务委托给其他专门代理来协调整个过程：用于收集消费者数据的"市场研究"代理、用于开发概念的"产品设计"代理，以及用于制作促销材料的"营销"代理。它们成功的关键是它们之间无缝的沟通和信息共享，确保所有个人努力都与集体目标保持一致。

在技术实现方面，多代理系统可以通过不同的架构来实现：
- **中心化架构**：有一个中央代理协调所有其他代理的活动
- **去中心化架构**：代理相互通信和协作，没有中央控制
- **混合架构**：结合中心化和去中心化方法的元素

## 代码示例

以下是使用CrewAI和Google Gemini实现多代理协作的完整示例：

```python
import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI

def setup_environment():
    """Loads environment variables and checks for the required API key."""
    load_dotenv()
    if not os.getenv("GOOGLE_API_KEY"):
        raise ValueError("GOOGLE_API_KEY not found. Please set it in your .env file.")

def main():
    """
    Initializes and runs the AI crew for content creation using the latest Gemini model.
    """
    setup_environment()

    # Define the language model to use.
    # Updated to a model from the Gemini 2.0 series for better performance and features.
    # For cutting-edge (preview) capabilities, you could use "gemini-2.5-flash".
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

    # Define Agents with specific roles and goals
    researcher = Agent(
        role='Senior Research Analyst',
        goal='Find and summarize the latest trends in AI.',
        backstory="You are an experienced research analyst with a knack for identifying key trends and synthesizing information.",
        verbose=True,
        allow_delegation=False,
    )

    writer = Agent(
        role='Technical Content Writer',
        goal='Write a clear and engaging blog post based on research findings.',
        backstory="You are a skilled writer who can translate complex technical topics into accessible content.",
        verbose=True,
        allow_delegation=False,
    )

    # Define Tasks for the agents
    research_task = Task(
        description="Research the top 3 emerging trends in Artificial Intelligence in 2024-2025. Focus on practical applications and potential impact.",
        expected_output="A detailed summary of the top 3 AI trends, including key points and sources.",
        agent=researcher,
    )

    writing_task = Task(
        description="Write a 500-word blog post based on the research findings. The post should be engaging and easy for a general audience to understand.",
        expected_output="A complete 500-word blog post about the latest AI trends.",
        agent=writer,
        context=[research_task],
    )

    # Create the Crew
    blog_creation_crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, writing_task],
        process=Process.sequential,
        llm=llm,
        verbose=2 # Set verbosity for detailed crew execution logs
    )

    # Execute the Crew
    print("## Running the blog creation crew with Gemini 2.0 Flash... ##")
    try:
        result = blog_creation_crew.kickoff()
        print("\n------------------\n")
        print("## Crew Final Output ##")
        print(result)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
```

这个示例展示了如何使用CrewAI框架创建一个包含两个专门代理的协作系统：
1. **研究代理**：负责查找和总结最新的AI趋势
2. **写作代理**：基于研究结果创作博客文章

写作代理的任务依赖于研究代理的输出（通过`context=[research_task]`），这演示了代理间的信息共享和协调。

## 总结
多代理协作模式展示了从单一全能代理到专业化协作代理的转变。它模仿了人类组织的结构，其中不同的代理被分配特定角色，协作解决多面目标，利用集体能力和协同效应来解决复杂挑战。