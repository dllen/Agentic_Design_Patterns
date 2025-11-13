# 第8章：内存管理 (Memory Management)

## 模式概述
内存管理（Memory Management）是智能代理系统中的一个关键设计模式，它使代理能够存储、检索和管理信息，以便在当前和未来的交互中使用。这种模式为代理提供了持续性上下文感知能力，使其能够记住先前的交互、用户偏好、对话历史和其他相关信息。

内存管理模式的核心思想是创建一个系统，使代理能够：
1. 存储重要信息供以后使用
2. 从内存中检索相关信息
3. 管理内存的生命周期和容量
4. 在不同会话和交互之间保持上下文

通过实施有效的内存管理，代理可以提供更个性化、上下文感知和连续的用户体验。这种模式对于需要长期对话、多步骤任务管理或用户个性化体验的应用特别有价值。

## 核心概念
1. **会话记忆**：存储单个对话或会话期间的相关信息
2. **长期记忆**：存储可在多个会话和交互中访问的信息
3. **记忆检索**：从内存中有效检索相关信息
4. **记忆管理**：管理内存的生命周期、容量和清理

## 实际应用
内存管理模式广泛应用于各种场景，包括：
- 持续对话和聊天机器人
- 个性化用户体验
- 任务和目标跟踪
- 用户偏好管理
- 上下文感知推荐

## 代码示例

### 示例1：使用ADK的InMemoryMemoryService

```python
# 示例：使用InMemoryMemoryService
# 这适用于本地开发和测试，其中数据在应用程序重启后
# 不需要持久化。内存内容在应用程序停止时丢失。
from google.adk.memory import InMemoryMemoryService
memory_service = InMemoryMemoryService()
```

### 示例2：使用VertexAiRagMemoryService

```python
# 示例：使用VertexAiRagMemoryService
# 这适用于在Google Cloud Platform上可扩展的生产环境，利用
# Vertex AI RAG（检索增强生成）进行持久、可搜索的内存。
# 需要：pip install google-adk[vertexai]，GCP设置/身份验证，以及Vertex AI RAG Corpus。
from google.adk.memory import VertexAiRagMemoryService

# 您的Vertex AI RAG Corpus资源名称
RAG_CORPUS_RESOURCE_NAME = "projects/your-gcp-project-id/locations/us-central1/ragCorpora/your-corpus-id" # 替换为您的Corpus资源名称

# 检索行为的可选配置
SIMILARITY_TOP_K = 5 # 要检索的顶部结果数
VECTOR_DISTANCE_THRESHOLD = 0.7 # 向量相似度阈值

memory_service = VertexAiRagMemoryService(
    rag_corpus=RAG_CORPUS_RESOURCE_NAME,
    similarity_top_k=SIMILARITY_TOP_K,
    vector_distance_threshold=VECTOR_DISTANCE_THRESHOLD
)
# 使用此服务时，add_session_to_memory和search_memory等方法
# 将与指定的Vertex AI RAG Corpus交互。
```

### 更实用的内存管理示例

```python
# 实际内存管理的完整示例
from datetime import datetime
from typing import Dict, List, Optional

class SimpleMemoryManager:
    """
    简单内存管理器的示例实现
    """
    def __init__(self, max_capacity: int = 100):
        self.memory_store: Dict[str, any] = {}
        self.access_log: List[Dict] = []
        self.max_capacity = max_capacity

    def store(self, key: str, value: any, metadata: Optional[Dict] = None):
        """
        在内存中存储值
        """
        if len(self.memory_store) >= self.max_capacity:
            # 简单的LRU（最近最少使用）清理
            self._evict_oldest()
        
        self.memory_store[key] = {
            'value': value,
            'timestamp': datetime.now(),
            'metadata': metadata or {}
        }
        
        self.access_log.append({
            'action': 'store',
            'key': key,
            'timestamp': datetime.now()
        })

    def retrieve(self, key: str) -> any:
        """
        从内存中检索值
        """
        if key in self.memory_store:
            # 更新访问时间
            self.memory_store[key]['timestamp'] = datetime.now()
            
            self.access_log.append({
                'action': 'retrieve',
                'key': key,
                'timestamp': datetime.now()
            })
            
            return self.memory_store[key]['value']
        
        return None

    def search(self, query: str) -> List[any]:
        """
        搜索与查询匹配的内存项
        """
        results = []
        query_lower = query.lower()
        
        for key, item in self.memory_store.items():
            if query_lower in key.lower() or (isinstance(item['value'], str) and query_lower in item['value'].lower()):
                results.append(item['value'])
                
        return results

    def _evict_oldest(self):
        """
        驱逐最旧的内存项
        """
        if not self.memory_store:
            return
            
        oldest_key = min(self.memory_store.keys(), 
                        key=lambda k: self.memory_store[k]['timestamp'])
        del self.memory_store[oldest_key]

    def clear(self):
        """
        清除所有内存
        """
        self.memory_store.clear()
        self.access_log.clear()

# 使用示例
memory_manager = SimpleMemoryManager(max_capacity=50)

# 存储用户信息
memory_manager.store("user_preference", "dark_mode", {"user_id": "12345"})
memory_manager.store("user_profile", {"name": "张三", "age": 30}, {"user_id": "12345", "category": "profile"})

# 检索信息
preferences = memory_manager.retrieve("user_preference")
print(f"用户偏好: {preferences}")

# 搜索相关信息
profile_info = memory_manager.search("profile")
print(f"档案信息: {profile_info}")
```

### 对话历史内存示例

```python
from typing import List, Dict
from datetime import datetime

class ConversationMemory:
    """
    管理对话历史的内存系统
    """
    def __init__(self, max_turns: int = 10):
        self.conversation_history: List[Dict] = []
        self.max_turns = max_turns

    def add_turn(self, user_input: str, agent_response: str):
        """
        添加对话回合到历史记录
        """
        turn = {
            'user_input': user_input,
            'agent_response': agent_response,
            'timestamp': datetime.now()
        }
        
        self.conversation_history.append(turn)
        
        # 限制历史记录长度
        if len(self.conversation_history) > self.max_turns:
            self.conversation_history = self.conversation_history[-self.max_turns:]

    def get_context(self, recent_turns: int = 3) -> List[Dict]:
        """
        获取最近对话回合作为上下文
        """
        return self.conversation_history[-recent_turns:]

    def get_full_history(self) -> List[Dict]:
        """
        获取完整对话历史
        """
        return self.conversation_history

    def clear_history(self):
        """
        清除对话历史
        """
        self.conversation_history.clear()

# 使用示例
conversation_memory = ConversationMemory(max_turns=5)

# 添加对话回合
conversation_memory.add_turn("你好，今天天气怎么样？", "今天天气晴朗，温度20度。")
conversation_memory.add_turn("我想知道附近的餐厅", "附近的推荐餐厅有：川菜馆、意大利餐厅、日本料理。")
conversation_memory.add_turn("请推荐一家川菜馆", "推荐您去'川香园'，评分4.5星，距离您1.2公里。")

# 获取最近的对话上下文
context = conversation_memory.get_context(recent_turns=2)
print("最近对话上下文:")
for i, turn in enumerate(context):
    print(f"轮次 {i+1}: 用户 - {turn['user_input']}")
    print(f"        代理 - {turn['agent_response']}")
```

## 最佳实践
1. **内存容量管理**：实施适当的内存清理策略以防止内存泄漏
2. **隐私和安全**：确保敏感信息得到适当处理和保护
3. **性能优化**：使用高效的检索机制，特别是对于大型内存存储
4. **内存分层**：区分短期和长期内存需求
5. **上下文窗口管理**：在LLM的上下文限制内有效管理内存

## 总结
内存管理是构建智能代理的基础技术，它使代理能够维护上下文、记住用户偏好并提供连续的用户体验。通过实施有效的内存管理系统，代理可以提供更个性化、更智能的交互，显著提高其实用性和用户满意度。这种模式对于任何需要持久性状态或上下文感知能力的代理系统都是至关重要的。