#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库模型和操作层
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Index, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import json

# 创建基类
Base = declarative_base()

# 全局数据库变量
engine = None
SessionLocal = None
session = None

def init_database():
    """初始化数据库连接"""
    global engine, SessionLocal, session
    
    try:
        from config import Config
        engine = create_engine(
            Config.DATABASE_URI,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        
        SessionLocal = sessionmaker(bind=engine)
        session = scoped_session(SessionLocal)
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        
        print("[SUCCESS] 数据库连接成功")
        return True
        
    except Exception as e:
        print(f"[ERROR] 数据库连接失败: {e}")
        print("[INFO] 将使用内存模式运行")
        return False

class Entity(Base):
    """实体表"""
    __tablename__ = 'entities'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_entity_name', 'name'),
    )

class Relation(Base):
    """关系表"""
    __tablename__ = 'relations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_relation_name', 'name'),
    )

class Triple(Base):
    """三元组表"""
    __tablename__ = 'triples'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    head_entity_id = Column(Integer, nullable=False, index=True)
    relation_id = Column(Integer, nullable=False, index=True)
    tail_entity_id = Column(Integer, nullable=False, index=True)
    confidence = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_triple_head_relation', 'head_entity_id', 'relation_id'),
        Index('idx_triple_relation_tail', 'relation_id', 'tail_entity_id'),
        Index('idx_triple_complete', 'head_entity_id', 'relation_id', 'tail_entity_id'),
    )

class Embedding(Base):
    """嵌入向量表"""
    __tablename__ = 'embeddings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_id = Column(Integer, nullable=True, unique=True, index=True)
    relation_id = Column(Integer, nullable=True, unique=True, index=True)
    embedding_type = Column(String(20), nullable=False)  # 'entity' 或 'relation'
    vector_data = Column(Text, nullable=False)  # JSON格式存储向量
    embedding_dim = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_embedding_entity_type', 'entity_id', 'embedding_type'),
    )

class KGDatabase:
    """知识图谱数据库操作类"""
    
    @staticmethod
    def add_entity(name: str, description: str = None) -> int:
        """添加实体，返回实体ID"""
        if session is None:
            return None
        
        existing = session.query(Entity).filter_by(name=name).first()
        if existing:
            return existing.id
        
        entity = Entity(name=name, description=description)
        session.add(entity)
        session.commit()
        return entity.id
    
    @staticmethod
    def add_relation(name: str, description: str = None) -> int:
        """添加关系，返回关系ID"""
        if session is None:
            return None
        
        existing = session.query(Relation).filter_by(name=name).first()
        if existing:
            return existing.id
        
        relation = Relation(name=name, description=description)
        session.add(relation)
        session.commit()
        return relation.id
    
    @staticmethod
    def add_triple(head_entity_name: str, relation_name: str, tail_entity_name: str, confidence: float = 1.0) -> bool:
        """添加三元组"""
        if session is None:
            return False
        
        try:
            head_id = KGDatabase.get_or_create_entity(head_entity_name)
            relation_id = KGDatabase.get_or_create_relation(relation_name)
            tail_id = KGDatabase.get_or_create_entity(tail_entity_name)
            
            existing = session.query(Triple).filter_by(
                head_entity_id=head_id,
                relation_id=relation_id,
                tail_entity_id=tail_id
            ).first()
            
            if existing:
                return True
            
            triple = Triple(
                head_entity_id=head_id,
                relation_id=relation_id,
                tail_entity_id=tail_id,
                confidence=confidence
            )
            session.add(triple)
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            print(f"添加三元组失败: {e}")
            return False
    
    @staticmethod
    def get_or_create_entity(name: str) -> int:
        """获取或创建实体ID"""
        if session is None:
            return None
        
        entity = session.query(Entity).filter_by(name=name).first()
        if entity:
            return entity.id
        
        entity = Entity(name=name)
        session.add(entity)
        session.flush()
        return entity.id
    
    @staticmethod
    def get_or_create_relation(name: str) -> int:
        """获取或创建关系ID"""
        if session is None:
            return None
        
        relation = session.query(Relation).filter_by(name=name).first()
        if relation:
            return relation.id
        
        relation = Relation(name=name)
        session.add(relation)
        session.flush()
        return relation.id
    
    @staticmethod
    def get_all_entities() -> List[str]:
        """获取所有实体名称"""
        if session is None:
            return []
        
        entities = session.query(Entity.name).all()
        return [entity[0] for entity in entities]
    
    @staticmethod
    def get_all_relations() -> List[str]:
        """获取所有关系名称"""
        if session is None:
            return []
        
        relations = session.query(Relation.name).all()
        return [relation[0] for relation in relations]
    
    @staticmethod
    def get_all_triples() -> List[Tuple[str, str, str]]:
        """获取所有三元组"""
        if session is None:
            return []
        
        from sqlalchemy.orm import aliased
        
        head_entity = aliased(Entity)
        tail_entity = aliased(Entity)
        
        triples = session.query(Triple, head_entity, Relation, tail_entity)\
            .join(head_entity, Triple.head_entity_id == head_entity.id)\
            .join(Relation, Triple.relation_id == Relation.id)\
            .join(tail_entity, Triple.tail_entity_id == tail_entity.id)\
            .all()
        
        return [
            (h.name, r.name, t.name)
            for triple, h, r, t in triples
        ]
    
    @staticmethod
    def save_embeddings(entity_embeddings, relation_embeddings, entity2id, relation2id):
        """保存嵌入向量"""
        if session is None:
            return False
        
        try:
            session.query(Embedding).delete()
            
            # 保存实体嵌入向量
            for entity_name, entity_id in entity2id.items():
                if entity_id < len(entity_embeddings):
                    vector = entity_embeddings[entity_id].tolist()
                    embedding = Embedding(
                        entity_id=entity_id,
                        embedding_type='entity',
                        vector_data=json.dumps(vector),
                        embedding_dim=len(vector)
                    )
                    session.add(embedding)
            
            # 保存关系嵌入向量
            for relation_name, relation_id in relation2id.items():
                if relation_id < len(relation_embeddings):
                    vector = relation_embeddings[relation_id].tolist()
                    embedding = Embedding(
                        relation_id=relation_id,
                        embedding_type='relation',
                        vector_data=json.dumps(vector),
                        embedding_dim=len(vector)
                    )
                    session.add(embedding)
            
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            print(f"保存嵌入向量失败: {e}")
            return False
    
    @staticmethod
    def load_embeddings():
        """加载嵌入向量"""
        if session is None:
            return None, None, {}, {}
        
        try:
            entity_embeddings = []
            relation_embeddings = []
            entity2id = {}
            relation2id = {}
            
            # 加载实体嵌入向量
            entity_embs = session.query(Embedding).filter_by(embedding_type='entity').order_by(Embedding.entity_id).all()
            entity_names = session.query(Entity).order_by(Entity.id).all()
            
            for idx, (emb, entity) in enumerate(zip(entity_embs, entity_names)):
                vector = json.loads(emb.vector_data)
                entity_embeddings.append(vector)
                entity2id[entity.name] = idx
            
            # 加载关系嵌入向量
            relation_embs = session.query(Embedding).filter_by(embedding_type='relation').order_by(Embedding.relation_id).all()
            relation_names = session.query(Relation).order_by(Relation.id).all()
            
            for idx, (emb, relation) in enumerate(zip(relation_embs, relation_names)):
                vector = json.loads(emb.vector_data)
                relation_embeddings.append(vector)
                relation2id[relation.name] = idx
            
            return entity_embeddings, relation_embeddings, entity2id, relation2id
            
        except Exception as e:
            print(f"加载嵌入向量失败: {e}")
            return None, None, {}, {}
    
    @staticmethod
    def get_statistics():
        """获取数据库统计信息"""
        if session is None:
            return {}
        
        try:
            entity_count = session.query(Entity).count()
            relation_count = session.query(Relation).count()
            triple_count = session.query(Triple).count()
            embedding_count = session.query(Embedding).count()
            
            return {
                'entity_count': entity_count,
                'relation_count': relation_count,
                'triple_count': triple_count,
                'embedding_count': embedding_count
            }
        except Exception as e:
            print(f"获取统计信息失败: {e}")
            return {}

def close_database():
    """关闭数据库连接"""
    global session
    if session:
        session.remove()
        print("[SUCCESS] 数据库连接已关闭")