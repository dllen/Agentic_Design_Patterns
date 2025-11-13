import json
import os
from typing import List, Dict, Any, Optional
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import re


class KnowledgeBase:
    """知识库类，存储FAQ数据"""
    
    def __init__(self, data_file: str = None):
        self.entries: List[Dict[str, Any]] = []
        if data_file and os.path.exists(data_file):
            self.load_data(data_file)
        else:
            self._init_default_data()
    
    def _init_default_data(self):
        """初始化默认数据"""
        self.entries = [
            {
                "id": 1,
                "question": "如何重置密码？",
                "answer": "您可以登录账户页面，点击'忘记密码'，然后按照提示操作。",
                "category": "账户安全"
            },
            {
                "id": 2,
                "question": "订单状态如何查询？",
                "answer": "登录后在'我的订单'页面可以查询所有订单状态。",
                "category": "订单查询"
            },
            {
                "id": 3,
                "question": "支持哪些支付方式？",
                "answer": "我们支持支付宝、微信支付、银行卡等多种支付方式。",
                "category": "支付"
            },
            {
                "id": 4,
                "question": "如何联系客服？",
                "answer": "您可以在'联系我们'页面找到客服电话或在线客服入口。",
                "category": "客服"
            },
            {
                "id": 5,
                "question": "退款政策是什么？",
                "answer": "我们提供7天无理由退款服务，具体政策请查看退款说明页面。",
                "category": "退款"
            }
        ]
    
    def load_data(self, data_file: str):
        """从文件加载数据"""
        with open(data_file, 'r', encoding='utf-8') as f:
            self.entries = json.load(f)
    
    def save_data(self, data_file: str):
        """保存数据到文件"""
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(self.entries, f, ensure_ascii=False, indent=2)