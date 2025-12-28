import numpy as np
import json
from typing import Dict, List, Tuple, Set
import pickle
import os

class KnowledgeGraph:
    """知识图谱数据结构"""
    def __init__(self):
        self.entities = set()  # 实体集合
        self.relations = set()  # 关系集合
        self.triples = []  # 三元组列表 (head, relation, tail)
        self.entity2id = {}  # 实体到ID的映射
        self.relation2id = {}  # 关系到ID的映射
        self.id2entity = {}  # ID到实体的映射
        self.id2relation = {}  # ID到关系的映射
        
    def add_triple(self, head: str, relation: str, tail: str):
        """添加三元组"""
        self.entities.add(head)
        self.entities.add(tail)
        self.relations.add(relation)
        self.triples.append((head, relation, tail))
        
    def build_mappings(self):
        """构建实体和关系的ID映射"""
        self.entity2id = {entity: idx for idx, entity in enumerate(sorted(self.entities))}
        self.relation2id = {relation: idx for idx, relation in enumerate(sorted(self.relations))}
        self.id2entity = {idx: entity for entity, idx in self.entity2id.items()}
        self.id2relation = {idx: relation for relation, idx in self.relation2id.items()}
        
    def get_entity_count(self):
        """获取实体数量"""
        return len(self.entities)
    
    def get_relation_count(self):
        """获取关系数量"""
        return len(self.relations)
    
    def get_triple_count(self):
        """获取三元组数量"""
        return len(self.triples)
    
    def save(self, filepath: str):
        """保存知识图谱"""
        data = {
            'entities': list(self.entities),
            'relations': list(self.relations),
            'triples': self.triples,
            'entity2id': self.entity2id,
            'relation2id': self.relation2id,
            'id2entity': self.id2entity,
            'id2relation': self.id2relation
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load(self, filepath: str):
        """加载知识图谱"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.entities = set(data['entities'])
        self.relations = set(data['relations'])
        self.triples = data['triples']
        self.entity2id = data['entity2id']
        self.relation2id = data['relation2id']
        self.id2entity = {int(k): v for k, v in data['id2entity'].items()}
        self.id2relation = {int(k): v for k, v in data['id2relation'].items()}

class KGDataset:
    """知识图谱数据集类"""
    @staticmethod
    def create_sample_dataset():
        """创建示例数据集"""
        kg = KnowledgeGraph()
        
        # 添加示例三元组（人物、地点、作品等）
        sample_triples = [
            # 人物信息
            ("爱因斯坦", "出生于", "德国"),
            ("爱因斯坦", "职业", "物理学家"),
            ("爱因斯坦", "提出了", "相对论"),
            ("爱因斯坦", "获得了", "诺贝尔物理学奖"),
            
            # 地理信息
            ("德国", "位于", "欧洲"),
            ("德国", "首都", "柏林"),
            ("柏林", "是", "城市"),
            
            # 科学概念
            ("相对论", "包括", "狭义相对论"),
            ("相对论", "包括", "广义相对论"),
            ("狭义相对论", "提出了", "爱因斯坦"),
            ("广义相对论", "提出了", "爱因斯坦"),
            
            # 其他人物
            ("牛顿", "职业", "物理学家"),
            ("牛顿", "提出了", "万有引力定律"),
            ("牛顿", "出生于", "英国"),
            ("英国", "位于", "欧洲"),
            ("英国", "首都", "伦敦"),
            
            # 奖项
            ("诺贝尔物理学奖", "是", "科学奖项"),
            ("诺贝尔物理学奖", "颁发国家", "瑞典"),
        ]
        
        for head, relation, tail in sample_triples:
            kg.add_triple(head, relation, tail)
        
        kg.build_mappings()
        return kg