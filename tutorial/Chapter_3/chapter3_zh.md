# 第3章：并行化 (Parallelization)

## 模式概述
在前面的章节中，我们探讨了用于顺序工作流的提示链和用于动态决策和不同路径之间转换的路由。虽然这些模式是必不可少的，但许多复杂的代理任务涉及可以同时执行而不是一个接一个执行的多个子任务。这就是并行化模式变得至关重要的地方。

并行化涉及同时执行多个组件，如LLM调用、工具使用，甚至整个子代理。通过并行执行，独立任务可以在同一时间运行，大大减少了可以分解为独立部分的任务的总体执行时间。

## 核心概念
1. **并发执行**：独立任务可以同时运行，而不是按顺序执行。
2. **任务分解**：将复杂任务分解为可以并行执行的独立子任务。
3. **性能优化**：通过并行化减少整体执行时间，特别是在处理外部服务时。

## 实际应用
考虑一个设计用于研究主题并总结其发现的代理。顺序方法可能：
1. 搜索源A
2. 摘要源A
3. 搜索源B
4. 摘要源B
5. 从摘要A和B合成最终答案

并行方法可以：
1. 同时搜索源A和搜索源B
2. 两个搜索完成后，同时摘要源A和源B
3. 从摘要A和B合成最终答案（这一步通常是顺序的，等待并行步骤完成）

核心思想是识别工作流中不依赖于其他部分输出的部分并将它们并行执行。当处理具有延迟的外部服务（如API或数据库）时，这种方法特别有效，因为您可以同时发出多个请求。

## 代码示例
以下是使用LangChain实现并行化模式的完整示例：

```python
import os
import asyncio
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable, RunnableParallel, RunnablePassthrough

# --- Configuration ---
# Ensure your API key environment variable is set (e.g., OPENAI_API_KEY)
try:
    llm: Optional[ChatOpenAI] = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    if llm:
        print(f"Language model initialized: {llm.model_name}")
except Exception as e:
    print(f"Error initializing language model: {e}")
    llm = None


# --- Define Independent Chains ---
# These three chains represent distinct tasks that can be executed in parallel.

summarize_chain: Runnable = (
    ChatPromptTemplate.from_messages([
        ("system", "Summarize the following topic concisely:"),
        ("user", "{topic}")
    ])
    | llm
    | StrOutputParser()
)

questions_chain: Runnable = (
    ChatPromptTemplate.from_messages([
        ("system", "Generate three interesting questions about the following topic:"),
        ("user", "{topic}")
    ])
    | llm
    | StrOutputParser()
)

terms_chain: Runnable = (
    ChatPromptTemplate.from_messages([
        ("system", "Identify 5-10 key terms from the following topic, separated by commas:"),
        ("user", "{topic}")
    ])
    | llm
    | StrOutputParser()
)


# --- Build the Parallel + Synthesis Chain ---

# 1. Define the block of tasks to run in parallel. The results of these,
#    along with the original topic, will be fed into the next step.
map_chain = RunnableParallel(
    {
        "summary": summarize_chain,
        "questions": questions_chain,
        "key_terms": terms_chain,
        "topic": RunnablePassthrough(),  # Pass the original topic through
    }
)

# 2. Define the final synthesis prompt which will combine the parallel results.
synthesis_prompt = ChatPromptTemplate.from_messages([
    ("system", """Based on the following information:
     Summary: {summary}
     Related Questions: {questions}
     Key Terms: {key_terms}
     Synthesize a comprehensive answer."""),
    ("user", "Original topic: {topic}")
])

# 3. Construct the full chain by piping the parallel results directly
#    into the synthesis prompt, followed by the LLM and output parser.
full_parallel_chain = map_chain | synthesis_prompt | llm | StrOutputParser()


# --- Run the Chain ---
async def run_parallel_example(topic: str) -> None:
    """
    Asynchronously invokes the parallel processing chain with a specific topic
    and prints the synthesized result.

    Args:
        topic: The input topic to be processed by the LangChain chains.
    """
    if not llm:
        print("LLM not initialized. Cannot run example.")
        return

    print(f"\n--- Running Parallel LangChain Example for Topic: '{topic}' ---")
    try:
        # The input to `ainvoke` is the single 'topic' string, which is
        # then passed to each runnable in the `map_chain`.
        response = await full_parallel_chain.ainvoke(topic)
        print("\n--- Final Response ---")
        print(response)
    except Exception as e:
        print(f"\nAn error occurred during chain execution: {e}")

if __name__ == "__main__":
    test_topic = "The history of space exploration"
    # In Python 3.7+, asyncio.run is the standard way to run an async function.
    asyncio.run(run_parallel_example(test_topic))
```

这个示例演示了使用LangChain的`RunnableParallel`组件并行执行三个独立的任务（摘要、问题生成和关键词提取），然后将结果合成到最终输出中。

## 总结
并行化模式通过使独立任务能够同时运行，显著提高了代理系统的效率。这是处理复杂任务的关键技术，这些任务可以分解为独立的子任务，从而减少执行时间并提高整体性能。