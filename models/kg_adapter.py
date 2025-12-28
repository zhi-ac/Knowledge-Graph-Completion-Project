#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识图谱数据适配器 - 桥接数据库和内存模式
"""

from typing import Set, List, Tuple, Dict
from .kg_data import KnowledgeGraph
from .database import KGDatabase, init_database

class HybridKnowledgeGraph(KnowledgeGraph):
    """混合知识图谱类 - 支持数据库和内存双重模式"""
    
    def __init__(self, use_database=True):
        super().__init__()
        self.use_database = use_database
        self.db_available = False
        
        if use_database:
            self.db_available = init_database()
            if self.db_available:
                self._load_from_database()
            else:
                print("[INFO] 数据库不可用，使用内存模式")
    
    def _load_from_database(self):
        """从数据库加载知识图谱"""
        if not self.db_available:
            return
        
        try:
            # 加载实体
            entities = KGDatabase.get_all_entities()
            self.entities = set(entities)
            
            # 加载关系
            relations = KGDatabase.get_all_relations()
            self.relations = set(relations)
            
            # 加载三元组
            triples = KGDatabase.get_all_triples()
            self.triples = triples
            
            # 重建映射
            self.build_mappings()
            
            print(f"[SUCCESS] 从数据库加载完成: {len(self.entities)}实体, {len(self.relations)}关系, {len(self.triples)}三元组")
            
        except Exception as e:
            print(f"[ERROR] 从数据库加载失败: {e}")
            self.db_available = False
    
    def add_triple(self, head: str, relation: str, tail: str):
        """添加三元组"""
        # 添加到内存
        super().add_triple(head, relation, tail)
        
        # 同步到数据库
        if self.db_available:
            try:
                success = KGDatabase.add_triple(head, relation, tail)
                if success:
                    print(f"[SUCCESS] 三元组已保存到数据库: {head} --{relation}--> {tail}")
                else:
                    print(f"[ERROR] 三元组保存失败: {head} --{relation}--> {tail}")
            except Exception as e:
                print(f"[ERROR] 数据库操作错误: {e}")
    
    def build_mappings(self):
        """构建ID映射"""
        super().build_mappings()
        
        # 如果使用数据库，确保数据库中有对应的实体和关系
        if self.db_available:
            self._sync_to_database()
    
    def _sync_to_database(self):
        """同步到数据库"""
        try:
            # 同步实体
            for entity in self.entities:
                KGDatabase.get_or_create_entity(entity)
            
            # 同步关系
            for relation in self.relations:
                KGDatabase.get_or_create_relation(relation)
            
            print("[SUCCESS] 实体和关系已同步到数据库")
            
        except Exception as e:
            print(f"[ERROR] 同步到数据库失败: {e}")
    
    def save_to_database(self):
        """显式保存到数据库"""
        if not self.db_available:
            print("[INFO] 数据库不可用，无法保存")
            return False
        
        try:
            success_count = 0
            for head, relation, tail in self.triples:
                if KGDatabase.add_triple(head, relation, tail):
                    success_count += 1
            
            print(f"[SUCCESS] 已保存 {success_count}/{len(self.triples)} 个三元组到数据库")
            return True
            
        except Exception as e:
            print(f"[ERROR] 保存到数据库失败: {e}")
            return False
    
    def get_database_statistics(self):
        """获取数据库统计信息"""
        if not self.db_available:
            return {"status": "database_unavailable"}
        
        try:
            stats = KGDatabase.get_statistics()
            stats["status"] = "available"
            return stats
        except Exception as e:
            return {"status": "error", "message": str(e)}

class HybridTransE:
    """混合TransE类 - 支持数据库存储嵌入向量"""
    
    def __init__(self, kg: HybridKnowledgeGraph, embedding_dim: int = 100, margin: float = 1.0, 
                 learning_rate: float = 0.01, epochs: int = 100):
        # 延迟导入避免循环依赖
        from .transe import TransE
        
        # 创建标准TransE实例
        self.base_transE = TransE(kg, embedding_dim, margin, learning_rate, epochs)
        self.kg = kg
        self.db_available = kg.db_available
    
    def __getattr__(self, name):
        """代理TransE的所有方法"""
        return getattr(self.base_transE, name)
    
    def train(self):
        """训练模型"""
        # 调用基础训练
        self.base_transE.train()
        
        # 训练完成后保存到数据库
        if self.db_available:
            self._save_embeddings_to_database()
    
    def _save_embeddings_to_database(self):
        """保存嵌入向量到数据库"""
        try:
            success = KGDatabase.save_embeddings(
                self.base_transE.entity_embeddings,
                self.base_transE.relation_embeddings,
                self.base_transE.kg.entity2id,
                self.base_transE.kg.relation2id
            )
            
            if success:
                print("[SUCCESS] 嵌入向量已保存到数据库")
            else:
                print("[ERROR] 嵌入向量保存失败")
                
        except Exception as e:
            print(f"[ERROR] 保存嵌入向量到数据库失败: {e}")
    
    def load_embeddings_from_database(self):
        """从数据库加载嵌入向量"""
        if not self.db_available:
            print("[INFO] 数据库不可用，无法加载嵌入向量")
            return False
        
        try:
            entity_embeddings, relation_embeddings, entity2id, relation2id = KGDatabase.load_embeddings()
            
            if entity_embeddings is not None:
                self.base_transE.entity_embeddings = entity_embeddings
                self.base_transE.relation_embeddings = relation_embeddings
                self.base_transE.kg.entity2id = entity2id
                self.base_transE.kg.relation2id = relation2id
                print("[SUCCESS] 从数据库加载嵌入向量成功")
                return True
            else:
                print("[ERROR] 从数据库加载嵌入向量失败")
                return False
                
        except Exception as e:
            print(f"[ERROR] 从数据库加载嵌入向量失败: {e}")
            return False