#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试索引越界问题修复
"""

import sys
import os
sys.path.append('.')

def test_dynamic_adding():
    """测试动态添加三元组的修复"""
    print("🔧 测试动态添加三元组的索引越界修复")
    print("=" * 50)
    
    try:
        from models.kg_data import KGDataset
        from models.transe import TransE
        
        # 创建基础知识图谱
        kg = KGDataset.create_sample_dataset()
        print(f"初始知识图谱: {kg.get_entity_count()}实体, {kg.get_relation_count()}关系")
        
        # 创建并训练模型
        model = TransE(kg, embedding_dim=20, epochs=5)
        model.train()
        print("✅ 初始模型训练完成")
        
        # 测试添加新三元组
        print("\n➕ 添加新三元组...")
        kg.add_triple("居里夫人", "发现了", "镭")
        kg.add_triple("居里夫人", "获得了", "诺贝尔奖")
        kg.add_triple("镭", "是", "放射性元素")
        kg.build_mappings()
        
        print(f"添加后知识图谱: {kg.get_entity_count()}实体, {kg.get_relation_count()}关系")
        
        # 同步嵌入向量
        model.check_embeddings_sync()
        print("✅ 嵌入向量同步完成")
        
        # 测试预测功能（这里容易出现索引越界）
        print("\n🔮 测试知识图谱补全...")
        results = model.complete_triple(head="居里夫人", relation="发现了", top_k=3)
        print(f"✅ 补全结果数量: {len(results)}")
        for i, (entity, score) in enumerate(results):
            print(f"   {i+1}. 居里夫人 --发现了--> {entity} (得分: {score:.3f})")
        
        print("\n🔗 测试链接预测...")
        predictions = model.predict_missing_links("居里夫人", top_k=3)
        print(f"✅ 预测结果数量: {len(predictions)}")
        for i, (entity, relation, score) in enumerate(predictions):
            print(f"   {i+1}. 居里夫人 --{relation}--> {entity} (得分: {score:.3f})")
        
        print("\n🎉 所有测试通过！索引越界问题已修复！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_dynamic_adding()
    if success:
        print("\n✅ 修复验证成功！系统现在可以安全地动态添加三元组。")
    else:
        print("\n❌ 仍有问题需要解决。")