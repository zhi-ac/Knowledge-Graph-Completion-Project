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
            # 核心人物与基本信息
            ("汤庸", "职业", "教授"),
            ("汤庸", "工作于", "华南师范大学"),
            ("汤庸", "创建了", "学者网"),
            ("汤庸", "身份", "国家教学名师"),
            ("汤庸", "身份", "国家级领军人才"),
            ("汤庸", "创建了", "社交网络数智开放实验室"),

            ("崔斌", "职业", "教授"),
            ("崔斌", "工作于", "北京大学"),
            ("崔斌", "领导", "北京大学数据与智能实验室"),

            ("金耀初", "职业", "教授"),
            ("金耀初", "工作于", "西湖大学"),
            ("金耀初", "身份", "欧洲科学院院士"),
            ("金耀初", "身份", "IEEE Fellow"),
            ("金耀初", "领导", "可信及通用人工智能实验室"),

            # 研究机构与实验室
            ("社交网络数智开放实验室", "别名", "SCHOLAT LAB"),
            ("社交网络数智开放实验室", "隶属于", "广东省服务计算工程研究中心"),
            ("广东省服务计算工程研究中心", "位于", "华南师范大学"),

            ("北京大学数据与智能实验室", "别名", "PKU-DAIR"),

            # 学术成果
            ("SCHOLAT数据智能开放实验室", "发表了", "Context-Driven Learning Path Recommendation论文"),
            ("SCHOLAT数据智能开放实验室", "发表了", "A Multi-Dimensional Analysis of Academic Social Networks论文"),
            ("Context-Driven Learning Path Recommendation论文", "被录用", "AAAI2026 AI4EDU会议"),
            ("A Multi-Dimensional Analysis of Academic Social Networks论文", "被发表", "ASPLOS 2026会议"),

            # 学术会议
            ("AAAI2026 AI4EDU", "是", "学术会议"),
            ("ASPLOS 2026", "是", "学术会议"),
            ("第六届社会计算国际会议", "别名", "ICSC 2025"),
            ("ICSC 2025", "举办于", "复旦大学"),

            # 学者网平台功能
            ("学者网", "提供", "学者网机构号"),
            ("学者网机构号", "描述为", "学术圈的公众号"),
            ("PKUDAIR", "是", "学者网机构号"),
            ("湾区科技观察", "是", "学者网机构号"),
            ("可信及通用人工智能实验室", "拥有", "学者网机构号"),

            # 课程信息
            ("汤庸", "创建了课程", "高级数据库技术"),
            ("潘家辉", "创建了课程", "数据结构与算法(C++描述)"),
            ("李丁丁", "创建了课程", "操作系统原理及课程设计"),
            ("高级数据库技术", "属于", "学者网活跃课程"),

            # 期刊信息
            ("International Journal of Computer Vision", "别名", "IJCV"),
            ("IJCV", "级别", "CCF A"),
            ("IJCV", "影响因子", "9.3"),
        ]        
        # 添加示例三元组（人物、地点、作品等）
        # sample_triples = [
        #     # 人物信息
        #     ("爱因斯坦", "出生于", "德国"),
        #     ("爱因斯坦", "职业", "物理学家"),
        #     ("爱因斯坦", "提出了", "相对论"),
        #     ("爱因斯坦", "获得了", "诺贝尔物理学奖"),
            
        #     # 地理信息
        #     ("德国", "位于", "欧洲"),
        #     ("德国", "首都", "柏林"),
        #     ("柏林", "是", "城市"),
            
        #     # 科学概念
        #     ("相对论", "包括", "狭义相对论"),
        #     ("相对论", "包括", "广义相对论"),
        #     ("狭义相对论", "提出了", "爱因斯坦"),
        #     ("广义相对论", "提出了", "爱因斯坦"),
            
        #     # 其他人物
        #     ("牛顿", "职业", "物理学家"),
        #     ("牛顿", "提出了", "万有引力定律"),
        #     ("牛顿", "出生于", "英国"),
        #     ("英国", "位于", "欧洲"),
        #     ("英国", "首都", "伦敦"),
            
        #     # 奖项
        #     ("诺贝尔物理学奖", "是", "科学奖项"),
        #     ("诺贝尔物理学奖", "颁发国家", "瑞典"),
        # ]
        
        for head, relation, tail in sample_triples:
            kg.add_triple(head, relation, tail)
        
        kg.build_mappings()
        return kg