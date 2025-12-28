#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识图谱补全系统演示脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.kg_data import KnowledgeGraph, KGDataset
from models.transe import TransE

def demo_transE():
    """演示TransE算法"""
    print("=" * 60)
    print("🧠 知识图谱补全系统演示")
    print("=" * 60)
    
    # 1. 创建示例知识图谱
    print("\n📊 1. 创建示例知识图谱...")
    kg = KGDataset.create_sample_dataset()
    
    print(f"   - 实体数量: {kg.get_entity_count()}")
    print(f"   - 关系数量: {kg.get_relation_count()}") 
    print(f"   - 三元组数量: {kg.get_triple_count()}")
    
    print("\n📝 实体列表:")
    for entity in sorted(kg.entities):
        print(f"   • {entity}")
    
    print("\n📝 关系列表:")
    for relation in sorted(kg.relations):
        print(f"   • {relation}")
    
    print("\n📝 三元组示例:")
    for i, triple in enumerate(kg.triples[:5]):
        print(f"   {i+1}. {triple[0]} --{triple[1]}--> {triple[2]}")
    if len(kg.triples) > 5:
        print(f"   ... 还有 {len(kg.triples)-5} 个三元组")
    
    # 2. 训练TransE模型
    print("\n🎯 2. 训练TransE模型...")
    model = TransE(kg, embedding_dim=50, epochs=50, learning_rate=0.01)
    model.train()
    
    # 3. 知识图谱补全演示
    print("\n🔮 3. 知识图谱补全演示...")
    
    # 示例1: 预测爱因斯坦的相关信息
    print("\n   示例1: 预测与'爱因斯坦'相关的缺失链接")
    results = model.predict_missing_links("爱因斯坦", top_k=5)
    for i, (entity, relation, score) in enumerate(results):
        confidence = max(0, 1 - score)  # 转换为置信度
        print(f"   {i+1}. 爱因斯坦 --{relation}--> {entity} (置信度: {confidence:.3f})")
    
    # 示例2: 补全三元组 (爱因斯坦, ?, ?)
    print("\n   示例2: 补全三元组 (爱因斯坦, 提出了, ?)")
    results = model.complete_triple(head="爱因斯坦", relation="提出了", top_k=3)
    for i, (entity, score) in enumerate(results):
        confidence = max(0, 1 - score)
        print(f"   {i+1}. 爱因斯坦 --提出了--> {entity} (置信度: {confidence:.3f})")
    
    # 示例3: 补全三元组 (?, 位于, 德国)
    print("\n   示例3: 补全三元组 (?, 位于, 德国)")
    results = model.complete_triple(relation="位于", tail="德国", top_k=3)
    for i, (entity, score) in enumerate(results):
        confidence = max(0, 1 - score)
        print(f"   {i+1}. {entity} --位于--> 德国 (置信度: {confidence:.3f})")
    
    # 4. 嵌入向量质量评估
    print("\n📈 4. 嵌入向量质量评估...")
    
    # 计算一些实体对的相似度
    def cosine_similarity(emb1, emb2):
        """计算余弦相似度"""
        dot_product = np.dot(emb1, emb2)
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        return dot_product / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0
    
    import numpy as np
    
    test_pairs = [
        ("爱因斯坦", "牛顿"),
        ("德国", "英国"), 
        ("相对论", "万有引力定律"),
        ("诺贝尔物理学奖", "科学奖项")
    ]
    
    print("   实体间余弦相似度:")
    for entity1, entity2 in test_pairs:
        if entity1 in kg.entity2id and entity2 in kg.entity2id:
            id1, id2 = kg.entity2id[entity1], kg.entity2id[entity2]
            emb1, emb2 = model.entity_embeddings[id1], model.entity_embeddings[id2]
            similarity = cosine_similarity(emb1, emb2)
            print(f"   • {entity1} vs {entity2}: {similarity:.3f}")
    
    print("\n✅ 演示完成！")
    print("\n🌐 现在可以运行以下命令启动Web界面:")
    print("   python app.py")
    print("   然后在浏览器中访问: http://localhost:5000")

if __name__ == "__main__":
    demo_transE()