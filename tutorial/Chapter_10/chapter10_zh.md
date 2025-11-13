# 第10章：模型上下文协议 (Model Context Protocol - MCP)

## 模式概述
模型上下文协议（Model Context Protocol，MCP）是一个标准化框架，用于在AI模型和各种工具、服务或数据源之间建立通信。MCP解决了AI代理在访问外部资源时面临的关键挑战：缺乏标准化的接口来与不同的工具和服务进行交互。通过提供统一的协议，MCP使AI模型能够以一致的方式发现、配置和使用各种外部能力。

MCP的重要性在于它为AI代理提供了一种标准化的方式来扩展其功能，而无需为每个新工具重新实现集成逻辑。这使得构建能够与广泛外部系统交互的更灵活、更强大的AI代理成为可能。

## 核心概念
1. **标准化接口**：提供一致的方式来与不同工具和服务交互
2. **发现机制**：允许模型发现可用的工具和能力
3. **配置管理**：处理工具的设置和认证
4. **请求/响应模式**：定义模型和工具之间的通信协议

## 实际应用
MCP在以下场景中特别有用：
- 集成各种API：如天气服务、金融数据、新闻源等
- 访问本地工具：如文件系统、数据库、命令行工具
- 企业系统集成：如CRM、ERP、内部文档系统
- 版本控制和代码仓库：如Git、GitHub等

MCP使AI代理能够：
- 动态发现可用工具
- 了解工具的能力和要求
- 以标准化方式执行工具调用
- 处理工具响应并将其整合到决策过程中

## 代码示例

### 1. FastMCP 服务器示例

以下是使用 FastMCP 创建简单服务器的代码：

```python
# fastmcp_server.py
# This script demonstrates how to create a simple MCP server using FastMCP.
# It exposes a single tool that generates a greeting.

# To run this server:
# 1. Make sure you have FastMCP installed: pip install fastmcp
# 2. Save this code as fastmcp_server.py
# 3. Run from your terminal: python fastmcp_server.py

from fastmcp import FastMCP, tool
import asyncio # Required for FastMCP's async capabilities

# Define a simple tool function.
# The `@tool()` decorator registers this Python function as an MCP tool.
# The docstring becomes the tool's description for the LLM.
@tool()
def greet(name: str) -> str:
    """
    Generates a personalized greeting.

    Args:
        name: The name of the person to greet.

    Returns:
        A greeting string.
    """
    return f"Hello, {name}! Nice to meet you."

# Initialize the FastMCP server.
# By default, FastMCP runs on http://localhost:8000
# and automatically discovers functions decorated with @tool().
mcp_server = FastMCP()

# To run the server, you typically use `mcp_server.run()` or `mcp_server.run_async()`.
# For a simple script, `run()` is sufficient.
if __name__ == "__main__":
    print("Starting FastMCP server...")
    print("This server exposes a 'greet' tool.")
    print("Access the tool schema at http://localhost:8000/tools.json")
    print("Press Ctrl+C to stop the server.")
    # FastMCP's run() method is blocking and starts the server.
    # It handles the asyncio event loop internally.
    mcp_server.run()
```

### 2. ADK 客户端代理消费 MCP 服务器

以下是使用 ADK 框架的客户端代理，它连接到上述 FastMCP 服务器：

```python
# ./adk_agent_samples/fastmcp_client_agent/agent.py
import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, HttpServerParameters

# Define the FastMCP server's address.
# Make sure your fastmcp_server.py (defined previously) is running on this port.
FASTMCP_SERVER_URL = "http://localhost:8000"

root_agent = LlmAgent(
    model='gemini-2.0-flash', # Or your preferred model
    name='fastmcp_greeter_agent',
    instruction='You are a friendly assistant that can greet people by their name. Use the "greet" tool.',
    tools=[
        MCPToolset(
            connection_params=HttpServerParameters(
                url=FASTMCP_SERVER_URL,
            ),
            # Optional: Filter which tools from the MCP server are exposed
            # For this example, we're expecting only 'greet'
            tool_filter=['greet']
        )
    ],
)
```

### 3. 文件系统 MCP 服务器示例

以下是使用 MCP 文件系统服务器的示例，允许 AI 代理管理文件：

```python
import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

# Create a reliable absolute path to a folder named 'mcp_managed_files'
# within the same directory as this agent script.
# This ensures the agent works out-of-the-box for demonstration.
# For production, you would point this to a more persistent and secure location.
TARGET_FOLDER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_managed_files")

# Ensure the target directory exists before the agent needs it.
os.makedirs(TARGET_FOLDER_PATH, exist_ok=True)

root_agent = LlmAgent(
    model='gemini-2.0-flash',
    name='filesystem_assistant_agent',
    instruction=(
        'Help the user manage their files. You can list files, read files, and write files. '
        f'You are operating in the following directory: {TARGET_FOLDER_PATH}'
    ),
    tools=[
        MCPToolset(
            connection_params=StdioServerParameters(
                command='npx',
                args=[
                    "-y",  # Argument for npx to auto-confirm install
                    "@modelcontextprotocol/server-filesystem",
                    # This MUST be an absolute path to a folder.
                    TARGET_FOLDER_PATH,
                ],
            ),
            # Optional: You can filter which tools from the MCP server are exposed.
            # For example, to only allow reading:
            # tool_filter=['list_directory', 'read_file']
        )
    ],
)
```

### 4. 其他 MCP 服务器示例

MCP 支持多种类型的服务器，包括通过 uvx 运行的 Google Sheets 服务器：

```python
# 通过 uvx 运行 MCP Google Sheets 服务器
from google.adk.tools.mcp_tool.mcp_toolset import StdioServerParameters

connection_params = StdioServerParameters(
  server_params={
    "command": "uvx",
    "args": ["mcp-google-sheets@latest"],
    "env": {
      "SERVICE_ACCOUNT_PATH": SERVICE_ACCOUNT_PATH,
      "DRIVE_FOLDER_ID": DRIVE_FOLDER_ID
    }
  }
)
```

## MCP 的重要优势

1. **标准化**：提供统一的接口，使 AI 代理可以与任何符合 MCP 标准的工具交互
2. **安全性**：用户控制哪些工具可以被 AI 代理访问
3. **可扩展性**：可以轻松添加新的 MCP 服务器来扩展 AI 代理的能力
4. **本地运行**：MCP 服务器通常在本地运行，保护敏感数据

## 总结
模型上下文协议（MCP）是构建能够与广泛外部系统交互的AI代理的关键技术。通过提供标准化接口，MCP使AI模型能够以一致的方式访问和利用各种工具和服务，从而大大扩展了其能力。这是实现真正通用AI代理的重要步骤，这些代理可以适应和利用可用的各种外部资源。