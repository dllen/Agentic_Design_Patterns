# 附录E：命令行上的代理 (Agents on the Command Line)

## 概述
命令行代理是专门设计在终端环境中运行的智能代理系统。它们能够解释自然语言命令、执行复杂任务、自动化工作流程，并与系统资源交互。本附录探讨了构建和使用命令行代理的技术和最佳实践。

## 命令行代理架构

### 1. 核心组件
命令行代理通常包含以下组件：

- **输入解析器**：解析自然语言输入
- **命令映射器**：将自然语言映射到系统命令
- **执行引擎**：执行系统命令和脚本
- **输出处理器**：格式化和呈现输出

### 2. 基础实现框架

```python
import argparse
import subprocess
import json
import os
from typing import Dict, List, Optional

class CommandLineAgent:
    def __init__(self, config_file: Optional[str] = None):
        self.commands = self.load_command_mappings()
        self.context = {}
        self.history = []
        
    def load_command_mappings(self) -> Dict[str, str]:
        """加载自然语言到命令的映射"""
        # 默认映射
        default_mappings = {
            "list files": "ls -la",
            "show disk usage": "df -h",
            "show memory usage": "free -m",
            "check system info": "uname -a",
            "find file": "find . -name '{}' -type f",
            "search text": "grep -r '{}' ."
        }
        return default_mappings
    
    def parse_input(self, user_input: str) -> Dict:
        """解析用户输入"""
        # 更高级的解析可以使用NLP
        processed_input = user_input.lower().strip()
        return {
            "raw": user_input,
            "processed": processed_input,
            "intent": self.identify_intent(processed_input)
        }
    
    def identify_intent(self, processed_input: str) -> str:
        """识别用户意图"""
        for intent in self.commands:
            if intent in processed_input:
                return intent
        return "unknown"
    
    def execute_command(self, command: str) -> Dict:
        """执行系统命令"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "command": command
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out",
                "command": command
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": command
            }

# 使用示例
agent = CommandLineAgent()
result = agent.execute_command("ls -la")
print(result)
```

## 高级功能实现

### 1. 自然语言到命令的映射
```python
import re
from typing import Pattern

class AdvancedNLPMapper:
    def __init__(self):
        self.patterns = {
            r'list files in directory (.+)': self._handle_list_directory,
            r'find file named (.+)': self._handle_find_file,
            r'search for text "(.+)" in (.+)': self._handle_search_text,
            r'create directory (.+)': self._handle_create_directory,
        }
    
    def map_natural_language(self, input_text: str) -> str:
        """将自然语言映射到命令"""
        input_lower = input_text.lower()
        
        for pattern, handler in self.patterns.items():
            match = re.search(pattern, input_lower, re.IGNORECASE)
            if match:
                return handler(match.groups())
        
        # 如果没有匹配，尝试基本匹配
        return self._basic_mapping(input_text)
    
    def _handle_list_directory(self, args: tuple) -> str:
        return f"ls -la {args[0]}"
    
    def _handle_find_file(self, args: tuple) -> str:
        return f"find . -name '{args[0]}' -type f"
    
    def _handle_search_text(self, args: tuple) -> str:
        return f"grep -r '{args[0]}' {args[1]}"
    
    def _handle_create_directory(self, args: tuple) -> str:
        return f"mkdir -p {args[0]}"
    
    def _basic_mapping(self, input_text: str) -> str:
        """基本映射"""
        basic_mappings = {
            "list files": "ls -la",
            "show disk space": "df -h",
            "check processes": "ps aux",
            "show network": "netstat -tuln",
        }
        
        for key, cmd in basic_mappings.items():
            if key in input_text.lower():
                return cmd
        
        return "echo 'Command not recognized'"
```

### 2. 上下文感知代理
```python
class ContextAwareAgent:
    def __init__(self):
        self.context = {
            "current_directory": os.getcwd(),
            "last_command": "",
            "last_output": "",
            "history": [],
            "variables": {}
        }
    
    def update_context(self, command: str, result: Dict):
        """更新上下文"""
        self.context.update({
            "last_command": command,
            "last_output": result.get("stdout", "")[:500],  # 只保留前500字符
            "history": self.context["history"][-10:] + [command],  # 保留最后10个命令
        })
    
    def execute_with_context(self, user_input: str) -> Dict:
        """执行命令并使用上下文"""
        # 解析输入
        parsed = self.parse_input(user_input)
        
        # 基于上下文调整命令
        command = self.adjust_command_with_context(parsed)
        
        # 执行命令
        result = self.execute_command(command)
        
        # 更新上下文
        self.update_context(command, result)
        
        return result
    
    def parse_input(self, user_input: str) -> Dict:
        """解析输入并考虑上下文"""
        # 如果输入是"that"或"it"等代词，引用之前的输出
        if user_input.lower() in ["that", "it", "previous"]:
            return {"command": self.context["last_output"]}
        
        # 如果输入包含变量引用
        if "$" in user_input:
            user_input = self._resolve_variables(user_input)
        
        return {"command": user_input}
    
    def _resolve_variables(self, user_input: str) -> str:
        """解析变量"""
        for var_name, var_value in self.context["variables"].items():
            user_input = user_input.replace(f"${var_name}", str(var_value))
        return user_input
```

## 实际应用示例

### 1. 项目管理代理
```python
class ProjectManagementAgent:
    def __init__(self, project_root: str = "."):
        self.project_root = project_root
        self.project_info = self._analyze_project()
    
    def _analyze_project(self) -> Dict:
        """分析项目结构"""
        info = {
            "has_git": os.path.exists(os.path.join(self.project_root, ".git")),
            "has_docker": os.path.exists(os.path.join(self.project_root, "Dockerfile")),
            "has_requirements": os.path.exists(os.path.join(self.project_root, "requirements.txt")),
            "has_package_json": os.path.exists(os.path.join(self.project_root, "package.json")),
            "has_makefile": os.path.exists(os.path.join(self.project_root, "Makefile"))
        }
        return info
    
    def handle_project_commands(self, command: str) -> Dict:
        """处理项目相关命令"""
        if "build" in command.lower():
            return self._handle_build()
        elif "test" in command.lower():
            return self._handle_test()
        elif "deploy" in command.lower():
            return self._handle_deploy()
        elif "status" in command.lower():
            return self._handle_status()
        else:
            return {"error": "Unknown project command"}
    
    def _handle_build(self) -> Dict:
        """处理构建命令"""
        if self.project_info["has_makefile"]:
            return self._run_command("make")
        elif self.project_info["has_package_json"]:
            return self._run_command("npm run build")
        elif self.project_info["has_requirements"]:
            return self._run_command("python setup.py build")
        else:
            return {"error": "No build system detected"}
    
    def _handle_test(self) -> Dict:
        """处理测试命令"""
        if self.project_info["has_makefile"]:
            return self._run_command("make test")
        elif self.project_info["has_package_json"]:
            return self._run_command("npm test")
        elif self.project_info["has_requirements"]:
            return self._run_command("pytest")
        else:
            return {"error": "No testing framework detected"}
    
    def _run_command(self, cmd: str) -> Dict:
        """运行命令"""
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                shell=True,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# 使用示例
project_agent = ProjectManagementAgent("/path/to/project")
result = project_agent.handle_project_commands("build project")
```

### 2. 文件管理代理
```python
import shutil
from pathlib import Path

class FileManagerAgent:
    def __init__(self):
        self.current_path = Path.cwd()
    
    def handle_file_commands(self, command: str) -> Dict:
        """处理文件命令"""
        if "copy file" in command.lower():
            return self._handle_copy(command)
        elif "move file" in command.lower():
            return self._handle_move(command)
        elif "delete file" in command.lower():
            return self._handle_delete(command)
        elif "create directory" in command.lower():
            return self._handle_create_dir(command)
        elif "find file" in command.lower():
            return self._handle_find(command)
        else:
            return self._handle_generic_command(command)
    
    def _handle_copy(self, command: str) -> Dict:
        """处理复制命令"""
        # 从自然语言中提取源和目标
        pattern = r"copy file (.+) to (.+)"
        match = re.search(pattern, command, re.IGNORECASE)
        
        if match:
            source, target = match.groups()
            source_path = Path(source)
            target_path = Path(target)
            
            try:
                if source_path.is_file():
                    shutil.copy2(source_path, target_path)
                    return {"success": True, "message": f"Copied {source} to {target}"}
                else:
                    return {"success": False, "error": f"Source {source} does not exist"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        else:
            return {"success": False, "error": "Could not parse copy command"}
    
    def _handle_move(self, command: str) -> Dict:
        """处理移动命令"""
        pattern = r"move file (.+) to (.+)"
        match = re.search(pattern, command, re.IGNORECASE)
        
        if match:
            source, target = match.groups()
            source_path = Path(source)
            target_path = Path(target)
            
            try:
                if source_path.is_file():
                    shutil.move(str(source_path), str(target_path))
                    return {"success": True, "message": f"Moved {source} to {target}"}
                else:
                    return {"success": False, "error": f"Source {source} does not exist"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        else:
            return {"success": False, "error": "Could not parse move command"}

# 更高级的实现可以结合大语言模型进行更精确的意图识别
class LLMEnhancedAgent:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.base_agent = CommandLineAgent()
    
    def process_command(self, user_input: str) -> Dict:
        """使用LLM增强命令处理"""
        # 使用LLM解释用户意图
        intent_explanation = self._get_llm_intent(user_input)
        
        # 根据LLM的解释执行相应的操作
        if intent_explanation.get("command_type") == "file_operation":
            file_agent = FileManagerAgent()
            return file_agent.handle_file_commands(user_input)
        elif intent_explanation.get("command_type") == "project_operation":
            # 假设当前在项目目录中
            project_agent = ProjectManagementAgent()
            return project_agent.handle_project_commands(user_input)
        else:
            # 使用基本命令映射
            return self.base_agent.execute_command(intent_explanation.get("command", user_input))
    
    def _get_llm_intent(self, user_input: str) -> Dict:
        """使用LLM获取命令意图"""
        # 这里应该调用实际的LLM API
        # 为了示例，我们提供一个模拟实现
        
        # 模拟LLM响应
        if any(word in user_input.lower() for word in ["file", "copy", "move", "delete"]):
            return {
                "command_type": "file_operation",
                "command": user_input
            }
        elif any(word in user_input.lower() for word in ["build", "test", "deploy", "project"]):
            return {
                "command_type": "project_operation", 
                "command": user_input
            }
        else:
            return {
                "command_type": "system_command",
                "command": user_input
            }
```

## 安全考虑

### 1. 命令注入防护
```python
import shlex

class SecureCommandLineAgent:
    def __init__(self):
        self.allowed_commands = {
            "ls", "cd", "pwd", "cat", "grep", "find", "mkdir", 
            "cp", "mv", "rm", "ps", "top", "df", "du", "free"
        }
    
    def validate_command(self, command: str) -> bool:
        """验证命令安全性"""
        # 分割命令以获取主要命令部分
        parts = command.split()
        if not parts:
            return False
        
        main_command = parts[0].split('/')[-1]  # 获取命令名（去掉路径）
        
        # 检查是否在允许列表中
        if main_command not in self.allowed_commands:
            return False
        
        # 检查是否有不安全字符
        dangerous_chars = [';', '&', '|', '`', '$(']
        for char in dangerous_chars:
            if char in command:
                return False
        
        return True
    
    def execute_safely(self, command: str) -> Dict:
        """安全执行命令"""
        if not self.validate_command(command):
            return {"success": False, "error": "Command not allowed for security reasons"}
        
        try:
            # 使用shlex.quote确保参数安全
            result = subprocess.run(
                shlex.split(command),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
```

## 交互式CLI代理

```python
import cmd
import readline  # 用于命令历史

class InteractiveAgentCLI(cmd.Cmd):
    intro = '欢迎使用命令行代理系统。输入 "help" 或 "?" 获取帮助。\n'
    prompt = '(agent) '
    
    def __init__(self):
        super().__init__()
        self.agent = CommandLineAgent()
    
    def do_run(self, arg):
        """运行命令: run <command>"""
        if arg:
            result = self.agent.execute_command(arg)
            if result["success"]:
                print(result["stdout"])
                if result["stderr"]:
                    print("错误:", result["stderr"])
            else:
                print("执行失败:", result.get("error", result.get("stderr", "未知错误")))
        else:
            print("请提供要运行的命令")
    
    def do_natural(self, arg):
        """自然语言命令: natural <command>"""
        if arg:
            # 这里可以集成自然语言处理
            command = self.process_natural_language(arg)
            print(f"解释为: {command}")
            result = self.agent.execute_command(command)
            self.display_result(result)
    
    def process_natural_language(self, natural_input: str):
        """处理自然语言输入（简化版）"""
        # 这里应该使用更复杂的NLP处理
        mapping = {
            "list files": "ls -la",
            "show disk usage": "df -h",
            "what time is it": "date",
            "show calendar": "cal"
        }
        
        for key, cmd in mapping.items():
            if key in natural_input.lower():
                return cmd
        
        return f"echo '无法理解命令: {natural_input}'"
    
    def display_result(self, result: Dict):
        """显示结果"""
        if result["success"]:
            print(result["stdout"])
            if result["stderr"]:
                print("错误:", result["stderr"])
        else:
            print("执行失败:", result.get("error", result.get("stderr", "未知错误")))
    
    def do_history(self, arg):
        """显示命令历史"""
        try:
            for i in range(1, readline.get_current_history_length() + 1):
                print(f"{i}: {readline.get_history_item(i)}")
        except:
            print("无法获取历史记录")
    
    def do_quit(self, arg):
        """退出代理: quit"""
        print("再见！")
        return True
    
    def do_exit(self, arg):
        """退出代理: exit"""
        return self.do_quit(arg)

# 启动交互式CLI
if __name__ == "__main__":
    InteractiveAgentCLI().cmdloop()
```

## 配置和扩展

### 1. 配置文件支持
```python
import yaml
from pathlib import Path

class ConfigurableAgent:
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.custom_commands = self.config.get('custom_commands', {})
    
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        default_config = {
            "custom_commands": {
                "my_build": "npm run build && npm run test",
                "deploy_prod": "git push origin main && docker build -t app . && docker push app:latest"
            },
            "aliases": {
                "ll": "ls -la",
                "h": "history"
            },
            "default_timeout": 30
        }
        
        config_file = Path(config_path) if config_path else Path.home() / ".agent_config.yaml"
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)
        
        return default_config
    
    def expand_command(self, command: str) -> str:
        """扩展自定义命令和别名"""
        # 检查别名
        if command in self.config['aliases']:
            return self.config['aliases'][command]
        
        # 检查自定义命令
        if command in self.config['custom_commands']:
            return self.config['custom_commands'][command]
        
        return command
```

## 总结
命令行上的代理为用户提供了一种自然、高效的方式来与系统交互。通过结合自然语言处理、上下文感知和安全执行机制，可以创建强大而安全的命令行代理系统。这些系统不仅可以理解复杂的用户意图，还能安全地执行相应的系统命令，从而大大提高命令行的易用性和生产力。