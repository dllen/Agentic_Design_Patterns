# 第4章：反思 (Reflection)

## 模式概述
反思（Reflection）是智能代理系统中的一个重要设计模式，它允许代理对自己的输出、行为或决策过程进行批判性评估。这种自我评估能力使代理能够识别错误、改进输出，并在不依赖外部反馈的情况下进行自我完善。

反思模式的核心思想是创建一个迭代循环，其中代理首先生成输出，然后从批判性角度分析该输出，最后根据分析结果进行改进。这个过程模拟了人类在思考和创作过程中自然发生的反思行为。

通过实施反思，代理可以显著提高其输出质量，减少错误，并在复杂任务中表现出更高的可靠性和准确性。这种模式对于需要高度准确性或创造性输出的任务特别有价值。

## 核心概念
1. **迭代改进**：通过生成-评估-改进的循环不断完善输出。
2. **自我评估**：代理能够批判性地分析自己的输出。
3. **错误检测**：识别输出中的不一致、错误或不足之处。
4. **自主优化**：在没有外部干预的情况下提高输出质量。

## 实际应用
反思模式广泛应用于各种场景，包括：
- 代码生成和优化
- 内容创作和编辑
- 问题解决和规划
- 质量控制和验证

## 代码示例

### 示例1：使用ADK的反思模式

```python
from google.adk.agents import SequentialAgent, LlmAgent

# 第一个代理生成初始草稿
generator = LlmAgent(
    name="DraftWriter",
    description="根据给定主题生成初始草稿内容",
    instruction="为用户提供一个简短、信息丰富的段落。",
    output_key="draft_text" # 输出保存到此状态键
)

# 第二个代理批评第一个代理的草稿
reviewer = LlmAgent(
    name="FactChecker",
    description="审查给定文本的事实准确性并提供结构化评论",
    instruction="""
    你是严谨的事实核查员。
    1. 阅读保存在状态键 'draft_text' 中的文本
    2. 仔细核实所有声明的事实准确性
    3. 最终输出必须是一个包含两个键的字典：
       - "status": 字符串，"ACCURATE" 或 "INACCURATE"
       - "reasoning": 字符串，提供清晰的解释，如有问题则引用具体问题
    """,
    output_key="review_output" # 结构化字典输出保存在这里
)

# SequentialAgent 确保生成器在评论者之前运行
review_pipeline = SequentialAgent(
    name="WriteAndReview_Pipeline",
    sub_agents=[generator, reviewer]
)

# 执行流程：
# 1. generator 运行 -> 将段落保存到 state['draft_text']
# 2. reviewer 运行 -> 读取 state['draft_text'] 并将字典输出保存到 state['review_output']
```

### 示例2：使用LangChain的反思循环

```python
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

# --- 配置 ---
# 从.env文件加载环境变量（用于OPENAI_API_KEY）
load_dotenv()

# 检查API密钥是否设置
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("在.env文件中未找到OPENAI_API_KEY。请添加。")

# 初始化聊天LLM。我们使用强大的模型如gpt-4o以获得更好的推理能力
# 使用较低的温度以获得更确定和专注的输出
llm = ChatOpenAI(model="gpt-4o", temperature=0.1)


def run_reflection_loop():
    """
    演示多步骤AI反思循环，以逐步改进Python函数
    """

    # --- 核心任务 ---
    task_prompt = """
    你的任务是创建一个名为 `calculate_factorial` 的Python函数。
    该函数应执行以下操作：
    1. 接受单个整数 `n` 作为输入
    2. 计算其阶乘（n!）
    3. 包含清晰的文档字符串，解释函数的功能
    4. 处理边界情况：0的阶乘是1
    5. 处理无效输入：如果输入是负数则引发ValueError
    """

    # --- 反思循环 ---
    max_iterations = 3
    current_code = ""
    # 我们将构建一个对话历史以在每个步骤中提供上下文
    message_history = [HumanMessage(content=task_prompt)]

    for i in range(max_iterations):
        print("\n" + "="*25 + f" 反思循环：迭代 {i + 1} " + "="*25)

        # --- 1. 生成/改进阶段 ---
        # 在第一次迭代中，它生成。在后续迭代中，它进行改进
        if i == 0:
            print("\n>>> 阶段 1: 生成初始代码...")
            # 第一条消息只是任务提示
            response = llm.invoke(message_history)
            current_code = response.content
        else:
            print("\n>>> 阶段 1: 根据先前评论改进代码...")
            # 消息历史现在包含任务、上次代码和上次评论
            # 我们指示模型应用提供的评论
            message_history.append(HumanMessage(content="请使用提供的评论改进代码。"))
            response = llm.invoke(message_history)
            current_code = response.content

        print("\n--- 生成的代码 (v" + str(i + 1) + ") ---\n" + current_code)
        message_history.append(response) # 将生成的代码添加到历史记录
        
        # --- 2. 反思阶段 ---
        print("\n>>> 阶段 2: 反思生成的代码...")

        # 为反思代理创建特定提示
        # 这要求模型充当高级代码审查员
        reflector_prompt = [
            SystemMessage(content="""
                你是高级软件工程师和Python专家。
                你的角色是执行细致的代码审查。
                根据原始任务要求，批判性评估提供的Python代码。
                查找错误、样式问题、缺失的边界情况和需要改进的地方。
                如果代码完美且满足所有要求，回复短语 'CODE_IS_PERFECT'。
                否则，提供评论的项目列表。
            """),
            HumanMessage(content=f"原始任务：\n{task_prompt}\n\n要审查的代码：\n{current_code}")
        ]

        critique_response = llm.invoke(reflector_prompt)
        critique = critique_response.content

        # --- 3. 停止条件 ---
        if "CODE_IS_PERFECT" in critique:
            print("\n--- 评论 ---\n未找到进一步的评论。代码令人满意。")
            break

        print("\n--- 评论 ---\n" + critique)
        # 将评论添加到历史记录以供下一次改进循环使用
        message_history.append(HumanMessage(content=f"先前代码的评论：\n{critique}"))

    print("\n" + "="*30 + " 最终结果 " + "="*30)
    print("\n反思过程后的最终改进代码：\n")
    print(current_code)


if __name__ == "__main__":
    run_reflection_loop()
```

### 示例3：使用LangChain的反射链

```python
import os
import sys
import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# --- 配置 ---
# 确保已设置API密钥环境变量（如OPENAI_API_KEY）
try:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    print(f"语言模型初始化：{llm.model_name}")
except Exception as e:
    print(f"初始化语言模型时出错：{e}", file=sys.stderr)
    print("请确保正确设置OPENAI_API_KEY。", file=sys.stderr)
    sys.exit(1) # 如果无法初始化LLM则退出


# --- 定义链组件 ---

# 1. 初始生成：创建产品描述的初稿
# 此链的输入将是字典，因此我们更新提示模板
generation_chain = (
    ChatPromptTemplate.from_messages([
        ("system", "为新的智能咖啡杯编写简短、简单的产品描述。"),
        ("user", "{product_details}")
    ])
    | llm
    | StrOutputParser()
)

# 2. 评论：评估生成的描述并提供反馈
critique_chain = (
    ChatPromptTemplate.from_messages([
        ("system", """根据清晰性、简洁性和吸引力批判性评估以下产品描述。
        提供具体的改进建议。"""),
        # 这将从前一步接收'initial_description'
        ("user", "要评论的产品描述：\n{initial_description}")
    ])
    | llm
    | StrOutputParser()
)

# 3. 改进：根据原始详情和评论重写描述
refinement_chain = (
    ChatPromptTemplate.from_messages([
        ("system", """基于原始产品详情和以下评论，
        重写产品描述以更加有效。

        原始产品详情：{product_details}
        评论：{critique}

        改进后的产品描述："""),
        ("user", "") # 用户输入为空，因为上下文在系统消息中提供
    ])
    | llm
    | StrOutputParser()
)


# --- 构建完整反射链（重构） ---
# 此链的结构更易读和线性
full_reflection_chain = (
    RunnablePassthrough.assign(
        initial_description=generation_chain
    )
    | RunnablePassthrough.assign(
        critique=critique_chain
    )
    | refinement_chain
)


# --- 运行链 ---
async def run_reflection_example(product_details: str):
    """使用产品详情运行LangChain反射示例"""
    print(f"\n--- 运行产品反射示例：'{product_details}' ---")
    try:
        # 链现在从开始就期望字典作为输入
        final_refined_description = await full_reflection_chain.ainvoke(
            {"product_details": product_details}
        )
        print("\n--- 最终改进的产品描述 ---")
        print(final_refined_description)
    except Exception as e:
        print(f"\n链执行期间发生错误：{e}")

if __name__ == "__main__":
    test_product_details = "一个能保持咖啡温度并可通过智能手机应用控制的杯子。"
    asyncio.run(run_reflection_example(test_product_details))
```

## 总结
反思模式是构建健壮和高质量AI代理的关键技术。它通过实施生成-评估-改进的循环使代理能够自主检测和纠正错误，从而提高输出质量。这种模式在要求高准确性的应用中特别有价值，因为它允许代理在没有人类干预的情况下进行自我完善，从而产生更可靠和准确的结果。