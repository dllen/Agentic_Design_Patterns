# 第1章：提示链 (Prompt Chaining)

## 模式概述
提示链（Prompt Chaining），有时也被称为流水线模式（Pipeline pattern），是一种在使用大语言模型（LLMs）时处理复杂任务的强大范式。它不是期望LLM在单个、单一的步骤中解决复杂问题，而是提倡采用分而治之的策略。

核心思想是将原始的、令人生畏的问题分解为一系列更小、更易管理的子问题。每个子问题都通过特定设计的提示单独解决，然后将一个提示生成的输出策略性地作为链中下一个提示的输入。

这种顺序处理技术本质上为LLM交互引入了模块化和清晰性。通过分解复杂任务，可以更容易理解和调试每个单独步骤，使整体过程更加健壮和可解释。每个步骤都可以精心制作和优化，以专注于更大问题的特定方面，从而产生更准确和集中的输出。

一个步骤的输出作为下一个步骤的输入是至关重要的。这种信息传递建立了依赖关系链，因此得名，其中先前操作的上下文和结果指导后续处理。这使LLM能够建立在其先前工作之上，完善其理解，并逐步接近所需的解决方案。

此外，提示链不仅仅是关于分解问题；它还启用了外部知识和工具的集成。在每个步骤中，可以指示LLM与外部系统、API或数据库交互，丰富其知识和能力，超越其内部训练数据。这种能力大大扩展了LLM的潜力，使它们不仅作为孤立模型，而且作为更智能系统的组成部分。

## 核心概念
1. **模块化**：将复杂任务分解为更小的、可管理的部分。
2. **顺序处理**：将前一个步骤的输出作为下一个步骤的输入。
3. **上下文传递**：在步骤之间传递信息，建立依赖关系链。
4. **外部集成**：在工作流中整合外部工具和API。

## 实际应用
提示链通过分解问题，使每个步骤更容易理解和调试，从而使整体过程更加健壮和可解释。每个步骤都可以精心制作和优化，以专注于更大问题的特定方面，从而产生更准确和集中的输出。

## 代码示例
根据相关笔记本，以下是使用LangChain的一个示例：

```python
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 初始化语言模型
llm = ChatOpenAI(temperature=0)

# 提示1：提取信息
prompt_extract = ChatPromptTemplate.from_template(
    "从以下文本中提取技术规格:\n\n{text_input}"
)

# 提示2：转换为JSON
prompt_transform = ChatPromptTemplate.from_template(
    "将以下规格转换为具有'cpu'、'memory'和'storage'键的JSON对象:\n\n{specifications}"
)

# 构建链
extraction_chain = prompt_extract | llm | StrOutputParser()
full_chain = (
    {"specifications": extraction_chain}
    | prompt_transform
    | llm
    | StrOutputParser()
)

# 运行链
input_text = "新款笔记本电脑型号配备3.5 GHz八核处理器、16GB RAM和1TB NVMe SSD。"

final_result = full_chain.invoke({"text_input": input_text})
print("\n--- 最终JSON输出 ---")
print(final_result)
```

## 总结
提示链是构建复杂AI代理的重要基础技术。它通过将复杂任务分解为更小的、可管理的步骤，使代理能够自主规划、推理和在动态环境中行动。这种模式使得LLM能够模仿人类思维过程，允许与复杂领域和系统进行更自然和有效的交互。