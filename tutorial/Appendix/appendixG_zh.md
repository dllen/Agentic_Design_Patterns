# 附录G：编程代理 (Programming Agents)

## 概述
编程代理是专门设计用于理解、生成、调试和优化代码的智能代理系统。它们能够解释自然语言编程需求，生成高质量代码，发现并修复错误，并协助开发者完成各种编程任务。

## 代码理解代理

### 1. 代码分析引擎
```python
import ast
import astor  # 用于将AST转换回代码
from typing import Dict, List, Any

class CodeAnalysisAgent:
    def __init__(self):
        self.analysis_cache = {}
    
    def analyze_function(self, code: str, function_name: str) -> Dict[str, Any]:
        """分析特定函数"""
        tree = ast.parse(code)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                return self._extract_function_info(node)
        
        return {"error": f"Function {function_name} not found"}
    
    def _extract_function_info(self, func_node: ast.FunctionDef) -> Dict[str, Any]:
        """提取函数信息"""
        return {
            "name": func_node.name,
            "args": [arg.arg for arg in func_node.args.args],
            "returns": self._analyze_return_statements(func_node),
            "docstring": ast.get_docstring(func_node),
            "complexity": self._calculate_complexity(func_node),
            "dependencies": self._find_dependencies(func_node)
        }
    
    def _analyze_return_statements(self, func_node: ast.FunctionDef) -> List[str]:
        """分析返回语句"""
        returns = []
        for node in ast.walk(func_node):
            if isinstance(node, ast.Return) and node.value:
                returns.append(ast.dump(node.value))
        return returns
    
    def _calculate_complexity(self, func_node: ast.FunctionDef) -> int:
        """计算圈复杂度"""
        complexity = 1  # 基础复杂度
        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.With)):
                complexity += 1
            elif isinstance(node, ast.Try):
                complexity += len(node.handlers)
        return complexity
    
    def _find_dependencies(self, func_node: ast.FunctionDef) -> List[str]:
        """查找函数依赖"""
        dependencies = set()
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    dependencies.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    dependencies.add(node.func.attr)
        return list(dependencies)
    
    def analyze_code_structure(self, code: str) -> Dict[str, Any]:
        """分析代码整体结构"""
        tree = ast.parse(code)
        structure = {
            "classes": [],
            "functions": [],
            "imports": [],
            "docstring": ast.get_docstring(tree)
        }
        
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                structure["functions"].append({
                    "name": node.name,
                    "args": [arg.arg for arg in node.args.args]
                })
            elif isinstance(node, ast.ClassDef):
                structure["classes"].append({
                    "name": node.name,
                    "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                })
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                structure["imports"].append(ast.unparse(node))
        
        return structure

# 使用示例
code_analyzer = CodeAnalysisAgent()

sample_code = '''
def bubble_sort(arr):
    """
    冒泡排序算法实现
    """
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
'''

function_info = code_analyzer.analyze_function(sample_code, "bubble_sort")
print("函数信息:", function_info)
```

### 2. 代码相似性检测
```python
import ast
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class CodeSimilarityAgent:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
    
    def normalize_code(self, code: str) -> str:
        """标准化代码以进行比较"""
        # 解析AST并重新格式化以消除格式差异
        try:
            tree = ast.parse(code)
            normalized = astor.to_source(tree)
            return normalized
        except SyntaxError:
            return code
    
    def extract_features(self, code: str) -> str:
        """提取代码特征用于相似性比较"""
        tree = ast.parse(code)
        features = []
        
        # 提取函数名、变量名、操作符等
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                features.append(f"function:{node.name}")
            elif isinstance(node, ast.Name):
                features.append(f"variable:{node.id}")
            elif isinstance(node, ast.BinOp):
                op_type = type(node.op).__name__
                features.append(f"operator:{op_type}")
        
        return " ".join(features)
    
    def calculate_similarity(self, code1: str, code2: str) -> float:
        """计算两段代码的相似度"""
        features1 = self.extract_features(code1)
        features2 = self.extract_features(code2)
        
        vectorizer = TfidfVectorizer().fit([features1, features2])
        vectors = vectorizer.transform([features1, features2])
        
        similarity = cosine_similarity(vectors[0], vectors[1])[0][0]
        return similarity
```

## 代码生成代理

### 1. 结构化代码生成
```python
import openai
from typing import Dict, List

class CodeGenerationAgent:
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.template_store = {}
        self.validation_rules = []
    
    def add_template(self, name: str, template: str):
        """添加代码模板"""
        self.template_store[name] = template
    
    def generate_function(self, description: str, language: str = "python") -> str:
        """根据描述生成函数"""
        prompt = f"""
根据以下描述生成{language}代码：

描述：{description}

要求：
1. 包含适当的文档字符串
2. 包含类型注解（如果语言支持）
3. 包含错误处理
4. 遵循最佳实践

代码：
"""
        if self.llm_client:
            return self.llm_client.generate(prompt)
        else:
            # 模拟生成
            return f"# {language} function for: {description}"
    
    def generate_class(self, description: str, class_name: str, methods: List[str]) -> str:
        """生成类定义"""
        prompt = f"""
生成一个名为{class_name}的类，具有以下功能：{description}

需要实现的方法：
{chr(10).join([f"- {method}" for method in methods])}

要求：
1. 包含初始化方法
2. 每个方法都有适当的文档字符串
3. 包含示例用法

类定义：
"""
        if self.llm_client:
            return self.llm_client.generate(prompt)
        else:
            # 模拟生成
            class_def = f"class {class_name}:\n    def __init__(self):\n        pass\n"
            for method in methods:
                class_def += f"\n    def {method}(self):\n        # TODO: Implement {method}\n        pass\n"
            return class_def
    
    def validate_code(self, code: str) -> Dict[str, List[str]]:
        """验证生成的代码"""
        errors = []
        warnings = []
        
        try:
            # 尝试解析代码
            ast.parse(code)
        except SyntaxError as e:
            errors.append(f"语法错误: {str(e)}")
        
        # 检查其他规则
        for rule in self.validation_rules:
            rule_result = rule(code)
            errors.extend(rule_result.get('errors', []))
            warnings.extend(rule_result.get('warnings', []))
        
        return {"errors": errors, "warnings": warnings}

# 预定义验证规则
def check_docstrings(code: str) -> Dict[str, List[str]]:
    """检查文档字符串"""
    tree = ast.parse(code)
    missing_docs = []
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
            if not ast.get_docstring(node):
                missing_docs.append(f"Missing docstring in {getattr(node, 'name', 'module')}")
    
    return {"errors": [], "warnings": missing_docs}
```

### 2. 测试生成代理
```python
class TestGenerationAgent:
    def __init__(self, code_generator: CodeGenerationAgent):
        self.code_gen = code_generator
    
    def generate_unit_tests(self, function_code: str, function_name: str) -> str:
        """为给定函数生成单元测试"""
        analysis = self.code_gen.analyze_function(function_code, function_name)
        
        prompt = f"""
为以下函数生成单元测试：

函数定义：
{function_code}

函数分析：
- 参数: {analysis.get('args', [])}
- 返回值: {analysis.get('returns', [])}
- 复杂度: {analysis.get('complexity', 0)}

生成测试用例，包括：
1. 正常情况测试
2. 边界情况测试
3. 错误情况测试

测试代码（使用pytest格式）：
"""
        if self.code_gen.llm_client:
            return self.code_gen.llm_client.generate(prompt)
        else:
            # 模拟生成
            return f"def test_{function_name}():\n    # TODO: Implement tests for {function_name}\n    pass"
    
    def generate_integration_tests(self, class_code: str, class_name: str) -> str:
        """生成集成测试"""
        prompt = f"""
为以下类生成集成测试：

类定义：
{class_code}

测试应该验证：
1. 类的初始化
2. 方法之间的交互
3. 复杂的使用场景

集成测试代码：
"""
        if self.code_gen.llm_client:
            return self.code_gen.llm_client.generate(prompt)
        else:
            return f"def test_{class_name}_integration():\n    # TODO: Implement integration tests for {class_name}\n    pass"
```

## 代码调试代理

### 1. 错误检测与修复
```python
import traceback
import re

class DebuggingAgent:
    def __init__(self):
        self.error_patterns = self._initialize_error_patterns()
        self.fix_strategies = self._initialize_fix_strategies()
    
    def _initialize_error_patterns(self):
        """初始化错误模式"""
        return {
            'indentation': re.compile(r'  File ".+", line (\d+), in .+\nIndentationError: (.+)'),
            'syntax': re.compile(r'  File ".+", line (\d+), in .+\nSyntaxError: (.+)'),
            'name_error': re.compile(r'  File ".+", line (\d+), in .+\nNameError: name \'(.+)\' is not defined'),
            'type_error': re.compile(r'  File ".+", line (\d+), in .+\nTypeError: (.+)'),
            'attribute_error': re.compile(r'  File ".+", line (\d+), in .+\nAttributeError: (.+)'),
        }
    
    def _initialize_fix_strategies(self):
        """初始化修复策略"""
        return {
            'undefined_variable': self._fix_undefined_variable,
            'missing_import': self._fix_missing_import,
            'incorrect_syntax': self._fix_syntax_error,
            'wrong_indentation': self._fix_indentation_error,
        }
    
    def analyze_error(self, error_traceback: str, code: str) -> Dict[str, Any]:
        """分析错误"""
        for error_type, pattern in self.error_patterns.items():
            match = pattern.search(error_traceback)
            if match:
                return {
                    "type": error_type,
                    "line_number": int(match.group(1)) if len(match.groups()) > 1 else 0,
                    "message": match.group(len(match.groups())),
                    "suggested_fix": self._suggest_fix(error_type, match.group(0), code)
                }
        
        return {"type": "unknown", "message": "Unable to parse error", "suggested_fix": ""}

    def _suggest_fix(self, error_type: str, error_message: str, code: str) -> str:
        """建议修复方案"""
        if error_type == 'name_error':
            var_name = re.search(r"name '(.+)' is not defined", error_message)
            if var_name:
                return self._fix_undefined_variable(var_name.group(1), code)
        elif error_type == 'syntax':
            return self._fix_syntax_error(error_message, code)
        elif error_type == 'indentation':
            return self._fix_indentation_error(error_message, code)
        
        return "无法确定修复方案"
    
    def _fix_undefined_variable(self, var_name: str, code: str) -> str:
        """修复未定义变量"""
        # 检查是否是拼写错误
        lines = code.split('\n')
        suggestions = []
        
        for i, line in enumerate(lines):
            if var_name.lower() in line.lower() and var_name not in line:
                # 可能是拼写错误
                suggestions.append(f"检查行 {i+1} 中的变量名拼写")
        
        if not suggestions:
            suggestions.append(f"确保变量 '{var_name}' 在使用前已定义")
        
        return "; ".join(suggestions)
    
    def _fix_syntax_error(self, error_message: str, code: str) -> str:
        """修复语法错误"""
        # 这里可以实现更复杂的语法错误修复逻辑
        return f"检查语法错误: {error_message}"
    
    def _fix_indentation_error(self, error_message: str, code: str) -> str:
        """修复缩进错误"""
        return "检查并修正代码缩进，确保使用一致的缩进（推荐使用4个空格）"
```

### 2. 性能分析代理
```python
import cProfile
import pstats
import io
from contextlib import redirect_stdout

class PerformanceAnalysisAgent:
    def __init__(self):
        self.profile_results = {}
    
    def profile_code(self, func, *args, **kwargs) -> Dict[str, Any]:
        """分析代码性能"""
        pr = cProfile.Profile()
        
        # 运行性能分析
        pr.enable()
        result = func(*args, **kwargs)
        pr.disable()
        
        # 获取分析结果
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s)
        ps.sort_stats('cumulative')
        ps.print_stats()
        
        analysis = self._analyze_profile_data(ps)
        
        return {
            "result": result,
            "profile_output": s.getvalue(),
            "analysis": analysis
        }
    
    def _analyze_profile_data(self, stats: pstats.Stats) -> Dict[str, Any]:
        """分析性能数据"""
        # 获取最耗时的函数
        top_functions = []
        stats_data = stats.get_stats_profile()
        
        # 这里可以实现更详细的性能分析
        # 当前返回一些基本指标
        return {
            "total_calls": stats.total_calls,
            "total_time": stats.total_tt,
            "top_functions": top_functions[:10]  # 前10个最耗时函数
        }
    
    def suggest_optimizations(self, profile_data: Dict) -> List[str]:
        """建议优化方案"""
        suggestions = []
        
        if profile_data["total_time"] > 1.0:  # 如果总时间超过1秒
            suggestions.append("考虑优化算法复杂度")
        
        # 基于具体性能数据添加更多建议
        return suggestions
```

## 代码重构代理

### 1. 重构建议引擎
```python
class RefactoringAgent:
    def __init__(self):
        self.refactoring_rules = [
            self._check_long_method,
            self._check_duplicate_code,
            self._check_complex_conditionals,
            self._check_large_class,
        ]
    
    def analyze_for_refactoring(self, code: str) -> List[Dict[str, str]]:
        """分析代码并提出重构建议"""
        suggestions = []
        tree = ast.parse(code)
        
        for rule in self.refactoring_rules:
            rule_suggestions = rule(tree, code)
            suggestions.extend(rule_suggestions)
        
        return suggestions
    
    def _check_long_method(self, tree: ast.AST, code: str) -> List[Dict[str, str]]:
        """检查过长的方法"""
        suggestions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 简单地计算函数行数（实际实现可能更复杂）
                source_lines = ast.get_source_segment(code, node).split('\n')
                if len([line for line in source_lines if line.strip()]) > 20:  # 假设超过20行为长方法
                    suggestions.append({
                        "type": "long_method",
                        "function": node.name,
                        "message": f"函数 {node.name} 过长，考虑拆分为多个小函数"
                    })
        
        return suggestions
    
    def _check_duplicate_code(self, tree: ast.AST, code: str) -> List[Dict[str, str]]:
        """检查重复代码"""
        # 简化的重复代码检测
        suggestions = []
        
        # 在实际实现中，这会比较复杂，需要比较AST节点
        return suggestions
    
    def _check_complex_conditionals(self, tree: ast.AST, code: str) -> List[Dict[str, str]]:
        """检查复杂条件"""
        suggestions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                # 检查嵌套的if语句
                complexity = self._calculate_conditional_complexity(node)
                if complexity > 3:  # 假设复杂度超过3需要重构
                    suggestions.append({
                        "type": "complex_conditional",
                        "message": f"条件语句过于复杂，建议简化"
                    })
        
        return suggestions
    
    def _calculate_conditional_complexity(self, node) -> int:
        """计算条件复杂度"""
        count = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                count += 1
        return count

# 辅助函数
def apply_refactoring_suggestion(code: str, suggestion: Dict[str, str]) -> str:
    """应用重构建议（简化实现）"""
    # 这里应该实现实际的代码重构逻辑
    print(f"建议: {suggestion['message']}")
    return code
```

## 代码文档代理

### 1. 自动文档生成
```python
class DocumentationAgent:
    def __init__(self):
        self.docstring_templates = {
            'function': '''def {name}({params}):
    """
    {name} - {description}
    
    Args:
{args_doc}
    
    Returns:
        {return_type}: {return_description}
    """
''',
            'class': '''class {name}:
    """
    {name} - {description}
    
    Attributes:
{attributes_doc}
    """
''',
        }
    
    def generate_docstring(self, code_element: str, element_type: str = 'function') -> str:
        """生成文档字符串"""
        if element_type == 'function':
            return self._generate_function_docstring(code_element)
        elif element_type == 'class':
            return self._generate_class_docstring(code_element)
        else:
            return f"# TODO: Add documentation for this {element_type}"
    
    def _generate_function_docstring(self, func_code: str) -> str:
        """为函数生成文档字符串"""
        try:
            tree = ast.parse(func_code)
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    # 提取参数信息
                    args = node.args.args
                    arg_names = [arg.arg for arg in args if arg.arg != 'self']
                    
                    args_doc = "\n".join([f"        {arg_name}: TODO: describe parameter" for arg_name in arg_names])
                    if not args_doc:
                        args_doc = "        None"
                    
                    docstring = f'''    """
    TODO: Add function description
    
    Args:
{args_doc}
    
    Returns:
        TODO: describe return value
    """
'''
                    return docstring
        except:
            pass
        
        return '    """TODO: Add documentation"""\n'
    
    def generate_api_documentation(self, code: str) -> str:
        """生成API文档"""
        tree = ast.parse(code)
        doc_parts = ["# API Documentation\n"]
        
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                docstring = ast.get_docstring(node) or "No description provided"
                
                doc_parts.append(f"## {node.name}()")
                doc_parts.append(f"{docstring}\n")
                
                # 参数信息
                args = [arg.arg for arg in node.args.args if arg.arg != 'self']
                if args:
                    doc_parts.append("### Parameters")
                    for arg in args:
                        doc_parts.append(f"- `{arg}`: TODO: describe")
                    doc_parts.append("")
                
                # 返回值信息
                doc_parts.append("### Returns")
                doc_parts.append("TODO: describe return value\n")
        
        return "\n".join(doc_parts)
```

## 完整的编程代理系统

```python
class FullProgrammingAgent:
    def __init__(self, llm_client=None):
        self.code_analyzer = CodeAnalysisAgent()
        self.code_generator = CodeGenerationAgent(llm_client)
        self.test_generator = TestGenerationAgent(self.code_generator)
        self.debugger = DebuggingAgent()
        self.performance_analyzer = PerformanceAnalysisAgent()
        self.refactoring_agent = RefactoringAgent()
        self.documentation_agent = DocumentationAgent()
        
        # 注册验证规则
        self.code_generator.validation_rules.append(check_docstrings)
    
    def assist_with_task(self, task_description: str) -> Dict[str, Any]:
        """协助完成编程任务"""
        response = {
            "task": task_description,
            "generated_code": "",
            "tests": "",
            "documentation": "",
            "refactoring_suggestions": [],
            "validation_results": {}
        }
        
        # 生成代码
        generated_code = self.code_generator.generate_function(task_description)
        response["generated_code"] = generated_code
        
        # 验证代码
        validation = self.code_generator.validate_code(generated_code)
        response["validation_results"] = validation
        
        # 生成测试
        if validation["errors"] == []:
            # 只有在代码语法正确时才生成测试
            try:
                tree = ast.parse(generated_code)
                for node in tree.body:
                    if isinstance(node, ast.FunctionDef):
                        response["tests"] = self.test_generator.generate_unit_tests(
                            generated_code, node.name
                        )
                        break
            except:
                response["tests"] = "# Could not generate tests due to parsing errors"
        
        # 生成文档
        response["documentation"] = self.documentation_agent.generate_docstring(
            generated_code, 'function'
        )
        
        # 重构建议
        response["refactoring_suggestions"] = self.refactoring_agent.analyze_for_refactoring(
            generated_code
        )
        
        return response
    
    def debug_and_fix(self, code: str, error_traceback: str) -> Dict[str, str]:
        """调试并修复代码"""
        analysis = self.debugger.analyze_error(error_traceback, code)
        
        return {
            "error_analysis": analysis,
            "original_code": code,
            "suggested_fixes": analysis.get("suggested_fix", ""),
            "recommended_actions": [
                "Apply the suggested fixes",
                "Run tests to verify the fix",
                "Consider refactoring for better code quality"
            ]
        }

# 使用示例
programming_agent = FullProgrammingAgent()

# 协助实现一个功能
task_result = programming_agent.assist_with_task(
    "实现一个函数来计算斐波那契数列的第n项"
)
print("生成的代码:")
print(task_result["generated_code"])
print("\\n\\n重构建议:")
for suggestion in task_result["refactoring_suggestions"]:
    print(f"- {suggestion['message']}")
```

## 最佳实践和注意事项

### 1. 代码安全性
```python
class SecureCodeAgent:
    def __init__(self):
        self.safety_patterns = [
            r'import\s+os|subprocess|sys',
            r'eval\(|exec\(',
            r'open\(|file\(',
            r'__import__|getattr|setattr',
        ]
    
    def check_code_safety(self, code: str) -> Dict[str, Any]:
        """检查代码安全性"""
        issues = []
        
        for pattern in self.safety_patterns:
            if re.search(pattern, code):
                issues.append(f"潜在安全风险: {pattern}")
        
        return {
            "safe": len(issues) == 0,
            "issues": issues,
            "severity": "high" if issues else "low"
        }
```

### 2. 代码质量检查
```python
class CodeQualityAgent:
    def __init__(self):
        self.quality_metrics = {
            "line_length": 88,  # PEP 8建议的行长度
            "function_length": 50,  # 函数最大行数
            "complexity_threshold": 10,  # 圈复杂度阈值
        }
    
    def assess_quality(self, code: str) -> Dict[str, Any]:
        """评估代码质量"""
        tree = ast.parse(code)
        lines = code.split('\\n')
        
        issues = []
        
        # 检查行长度
        for i, line in enumerate(lines, 1):
            if len(line) > self.quality_metrics["line_length"]:
                issues.append(f"行 {i} 超长: {len(line)} 字符")
        
        # 检查函数长度和复杂度
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_lines = self._count_function_lines(node, lines)
                if func_lines > self.quality_metrics["function_length"]:
                    issues.append(f"函数 {node.name} 过长: {func_lines} 行")
                
                complexity = self._calculate_complexity(node)
                if complexity > self.quality_metrics["complexity_threshold"]:
                    issues.append(f"函数 {node.name} 复杂度过高: {complexity}")
        
        return {
            "issues": issues,
            "score": 100 - len(issues) * 5,  # 简单评分系统
            "recommendations": self._generate_recommendations(issues)
        }
    
    def _count_function_lines(self, func_node, all_lines) -> int:
        """计算函数行数"""
        start_line = func_node.lineno
        end_line = self._find_function_end(func_node, all_lines)
        return end_line - start_line + 1
    
    def _find_function_end(self, func_node, all_lines) -> int:
        """找到函数结束行"""
        # 简化的实现
        return func_node.end_lineno if hasattr(func_node, 'end_lineno') else func_node.lineno
```

## 总结
编程代理代表了AI在软件开发中的重要应用。通过结合代码分析、生成、调试和优化技术，这些代理可以显著提高开发效率，减少错误，并协助开发者创建高质量的软件。随着技术的发展，编程代理将变得更加智能和强大，成为开发工作流程中不可或缺的工具。