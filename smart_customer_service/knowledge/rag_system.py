import json
import os
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import sys
import os
# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knowledge_base import KnowledgeBase


class RAGSystem:
    """检索增强生成系统"""
    
    def __init__(self, knowledge_base: KnowledgeBase = None):
        self.knowledge_base = knowledge_base or KnowledgeBase()
        self.embeddings = None
        self._init_embeddings()
    
    def _init_embeddings(self):
        """初始化知识库嵌入向量"""
        # 这里我们模拟嵌入向量
        print("初始化知识库嵌入...")
        
        self.embeddings = []
        for entry in self.knowledge_base.entries:
            # 模拟为每个问题和答案创建嵌入向量
            question_embedding = np.random.rand(128)  # 模拟向量
            self.embeddings.append(question_embedding)
    
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """搜索最相关的结果"""
        if not self.embeddings:
            return []
            
        # 模拟查询嵌入
        query_embedding = np.random.rand(128)  # 模拟
        
        # 计算相似度
        similarities = []
        for emb in self.embeddings:
            sim = cosine_similarity([query_embedding], [emb])[0][0]
            similarities.append(sim)
        
        # 获取最相似的top_k个结果
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if idx < len(self.knowledge_base.entries):
                entry = self.knowledge_base.entries[idx].copy()
                entry['similarity'] = similarities[idx]
                results.append(entry)
        
        return results
    
    def get_answer(self, query: str) -> Optional[Dict[str, Any]]:
        """根据查询获取答案"""
        results = self.search(query)
        if results:
            # 返回最相似的结果
            return results[0]
        return None