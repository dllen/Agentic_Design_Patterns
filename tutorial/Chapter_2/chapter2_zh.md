# 第2章：路由 (Routing)

## 模式概述
虽然通过提示链进行顺序处理是使用语言模型执行确定性、线性工作流的基础技术，但在需要自适应响应的情况下，其适用性有限。现实世界的代理系统通常必须根据环境状态、用户输入或先前操作的结果等偶然因素在多个潜在操作之间进行仲裁。这种动态决策能力通过一种称为路由的机制实现，该机制控制流向不同专业功能、工具或子流程的控制流。

路由在代理操作框架中引入了条件逻辑，使模型从固定执行路径转变为代理动态评估特定标准以从可能的后续操作集中进行选择。这允许更灵活和上下文感知的系统行为。

## 核心概念
1. **动态决策**：根据实时条件动态选择执行路径。
2. **意图分类**：将用户输入分类为不同的意图类别。
3. **专业化路由**：将查询路由到专门的代理或工具链。

## 实现方式
路由机制可以通过以下几种方式实现：

- **基于LLM的路由**：语言模型本身可以被提示分析输入并输出指示下一个步骤或目的地的特定标识符或指令。
- **基于嵌入的路由**：输入查询可以转换为向量嵌入，然后与表示不同路由或功能的嵌入进行比较。
- **基于规则的路由**：使用基于关键字、模式或从输入中提取的结构化数据的预定义规则或逻辑。
- **基于机器学习模型的路由**：使用在少量标记数据上专门训练的判别模型（如分类器）来执行路由任务。

## 实际应用
考虑一个为客户查询设计的代理，当配备路由功能时，可以首先对传入查询进行分类以确定用户意图。基于此分类，它可以将查询定向到直接问答的专门代理、与订单数据库交互的数据库检索工具，或复杂问题的升级程序，而不是默认为单一的预定响应路径。

## 代码示例
以下是使用LangGraph实现路由模式的完整示例：

```python
# Copyright (c) 2025 Marco Fago
#
# This code is licensed under the MIT License.
# See the LICENSE file in the repository for the full license text.

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableBranch

# --- Configuration ---
# Ensure your API key environment variable is set (e.g., GOOGLE_API_KEY)
try:
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    print(f"Language model initialized: {llm.model}")
except Exception as e:
    print(f"Error initializing language model: {e}")
    llm = None

# --- Define Simulated Sub-Agent Handlers (equivalent to ADK sub_agents) ---

def booking_handler(request: str) -> str:
    """Simulates the Booking Agent handling a request."""
    print("\n--- DELEGATING TO BOOKING HANDLER ---")
    return f"Booking Handler processed request: '{request}'. Result: Simulated booking action."

def info_handler(request: str) -> str:
    """Simulates the Info Agent handling a request."""
    print("\n--- DELEGATING TO INFO HANDLER ---")
    return f"Info Handler processed request: '{request}'. Result: Simulated information retrieval."

def unclear_handler(request: str) -> str:
    """Handles requests that couldn't be delegated."""
    print("\n--- HANDLING UNCLEAR REQUEST ---")
    return f"Coordinator could not delegate request: '{request}'. Please clarify."

# --- Define Coordinator Router Chain (equivalent to ADK coordinator's instruction) ---
# This chain decides which handler to delegate to.
coordinator_router_prompt = ChatPromptTemplate.from_messages([
    ("system", """Analyze the user's request and determine which specialist handler should process it.
     - If the request is related to booking flights or hotels, output 'booker'.
     - For all other general information questions, output 'info'.
     - If the request is unclear or doesn't fit either category, output 'unclear'.
     ONLY output one word: 'booker', 'info', or 'unclear'."""),
    ("user", "{request}")
])

if llm:
    coordinator_router_chain = coordinator_router_prompt | llm | StrOutputParser()

# --- Define the Delegation Logic (equivalent to ADK's Auto-Flow based on sub_agents) ---
# Use RunnableBranch to route based on the router chain's output.

# Define the branches for the RunnableBranch
branches = {
    "booker": RunnablePassthrough.assign(output=lambda x: booking_handler(x['request']['request'])),
    "info": RunnablePassthrough.assign(output=lambda x: info_handler(x['request']['request'])),
    "unclear": RunnablePassthrough.assign(output=lambda x: unclear_handler(x['request']['request'])),
}

# Create the RunnableBranch. It takes the output of the router chain
# and routes the original input ('request') to the corresponding handler.
delegation_branch = RunnableBranch(
    (lambda x: x['decision'].strip() == 'booker', branches["booker"]), # Added .strip()
    (lambda x: x['decision'].strip() == 'info', branches["info"]),     # Added .strip()
    branches["unclear"] # Default branch for 'unclear' or any other output
)

# Combine the router chain and the delegation branch into a single runnable
# The router chain's output ('decision') is passed along with the original input ('request')
# to the delegation_branch.
coordinator_agent = {
    "decision": coordinator_router_chain,
    "request": RunnablePassthrough()
} | delegation_branch | (lambda x: x['output']) # Extract the final output

# --- Example Usage ---
def main():
    if not llm:
        print("\nSkipping execution due to LLM initialization failure.")
        return

    print("--- Running with a booking request ---")
    request_a = "Book me a flight to London."
    result_a = coordinator_agent.invoke({"request": request_a})
    print(f"Final Result A: {result_a}")

    print("\n--- Running with an info request ---")
    request_b = "What is the capital of Italy?"
    result_b = coordinator_agent.invoke({"request": request_b})
    print(f"Final Result B: {result_b}")

    print("\n--- Running with an unclear request ---")
    request_c = "Tell me about quantum physics."
    result_c = coordinator_agent.invoke({"request": request_c})
    print(f"Final Result C: {result_c}")

if __name__ == "__main__":
    main()
```

这个示例展示了如何使用LangGraph实现一个路由系统，根据用户请求的类型将它们分派给不同的处理程序。

## 总结
路由模式是构建灵活和自适应AI代理的关键技术。它使代理能够根据输入和上下文动态选择最合适的处理路径，大大提高了系统的灵活性和上下文感知能力。