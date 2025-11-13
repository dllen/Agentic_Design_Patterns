# 第11章：目标设定与监控 (Goal Setting and Monitoring)

## 模式概述
目标设定与监控模式是代理系统中的一个重要概念，旨在构建能够根据预定义目标自主生成、改进和评估解决方案的AI代理。该模式的核心是创建一个迭代过程，其中代理生成解决方案，根据目标评估该解决方案，然后在必要时进行改进，直到满足目标。

这种模式特别适用于需要高质量输出的任务，其中解决方案需要满足特定标准，如简单性、正确性、边缘情况处理等。通过建立反馈循环，代理可以持续改进其输出，直到满足预定标准。

## 核心概念
1. **目标驱动**：代理的行动由明确的目标集指导。
2. **迭代改进**：解决方案在多次迭代中得到完善，直到达到目标。
3. **自动评估**：使用大语言模型评估解决方案是否满足目标。
4. **反馈循环**：从评估中获取反馈以指导下一次迭代。

## 实际应用
Chapter 11笔记中提供了一个具体示例：构建一个AI代理，根据指定的用例和目标编写代码。该代理：
- 接受编码问题（用例）作为输入
- 接受目标列表（如"简单"、"经过测试"、"处理边缘情况"）作为输入
- 使用LLM（如GPT-4o）生成和细化Python代码，直到满足目标
- 为检查目标是否满足，向LLM询问并回答True或False，从而更容易停止迭代

## 代码示例
以下是笔记中Goal Setting and Monitoring模式的简化实现：

```python
import os
import random
import re
from pathlib import Path
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv, find_dotenv

# 加载环境变量
_ = load_dotenv(find_dotenv())
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise EnvironmentError("请设置OPENAI_API_KEY环境变量")

# 初始化OpenAI模型
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.3,
    openai_api_key=OPENAI_API_KEY,
)

def generate_prompt(use_case: str, goals: list[str], previous_code: str = "", feedback: str = "") -> str:
    base_prompt = f"""
You are an AI coding agent. Your job is to write Python code based on the following use case:

Use Case: {use_case}

Your goals are:
{chr(10).join(f"- {g.strip()}" for g in goals)}
"""
    if previous_code:
        base_prompt += f"\nPreviously generated code:\n{previous_code}"
    if feedback:
        base_prompt += f"\nFeedback on previous version:\n{feedback}\n"

    base_prompt += "\nPlease return only the revised Python code. Do not include comments or explanations outside the code."
    return base_prompt

def get_code_feedback(code: str, goals: list[str]) -> str:
    feedback_prompt = f"""
You are a Python code reviewer. A code snippet is shown below. Based on the following goals:

{chr(10).join(f"- {g.strip()}" for g in goals)}

Please critique this code and identify if the goals are met. Mention if improvements are needed for clarity, simplicity, correctness, edge case handling, or test coverage.

Code:
{code}
"""
    return llm.invoke(feedback_prompt)

def goals_met(feedback_text: str, goals: list[str]) -> bool:
    """
    使用LLM评估基于反馈文本是否满足目标
    返回True或False（从LLM输出解析）
    """
    review_prompt = f"""
You are an AI reviewer.

Here are the goals:
{chr(10).join(f"- {g.strip()}" for g in goals)}

Here is the feedback on the code:
\"\"\"
{feedback_text}
\"\"\"

Based on the feedback above, have the goals been met?

Respond with only one word: True or False.
"""
    response = llm.invoke(review_prompt).content.strip().lower()
    return response == "true"

def run_code_agent(use_case: str, goals_input: str, max_iterations: int = 5) -> str:
    goals = [g.strip() for g in goals_input.split(",")]

    print(f"\n🎯 Use Case: {use_case}")
    print("🎯 Goals:")
    for g in goals:
        print(f"  - {g}")

    previous_code = ""
    feedback = ""

    for i in range(max_iterations):
        print(f"\n=== 🔁 Iteration {i + 1} of {max_iterations} ===")
        prompt = generate_prompt(use_case, goals, previous_code, feedback if isinstance(feedback, str) else feedback.content)

        print("🚧 Generating code...")
        code_response = llm.invoke(prompt)
        raw_code = code_response.content.strip()
        # Clean code block if needed
        lines = raw_code.strip().splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        code = "\n".join(lines).strip()
        print(f"\n🧾 Generated Code:\n{'-' * 50}\n{code}\n{'-' * 50}")

        print("\n📤 Submitting code for feedback review...")
        feedback = get_code_feedback(code, goals)
        feedback_text = feedback.content.strip()
        print(f"\n📥 Feedback Received:\n{'-' * 50}\n{feedback_text}\n{'-' * 50}")

        if goals_met(feedback_text, goals):
            print("✅ LLM confirms goals are met. Stopping iteration.")
            break

        print("🛠️ Goals not fully met. Preparing for next iteration...")
        previous_code = code

    return code
```

## 总结
目标设定与监控模式是构建能够自主优化其输出以满足特定标准的AI代理的重要技术。通过建立迭代改进和自动评估的反馈循环，代理可以生成越来越符合预定目标的高质量解决方案。