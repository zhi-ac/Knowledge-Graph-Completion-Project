#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_basic_functionality():
    """测试基本功能"""
    print("=" * 50)
    print("🧠 知识图谱补全系统 - 基础功能测试")
    print("=" * 50)
    
    try:
        # 测试数据模型
        from models.kg_data import KnowledgeGraph, KGDataset
        print("✅ 数据模型导入成功")
        
        # 创建示例知识图谱
        kg = KGDataset.create_sample_dataset()
        print(f"✅ 知识图谱创建成功: {kg.get_entity_count()}个实体, {kg.get_relation_count()}个关系, {kg.get_triple_count()}个三元组")
        
        # 测试TransE模型
        from models.transe import TransE
        print("✅ TransE模型导入成功")
        
        # 创建模型（使用较小的参数用于快速测试）
        model = TransE(kg, embedding_dim=20, epochs=10, learning_rate=0.1)
        print("✅ TransE模型初始化成功")
        
        # 简单训练
        print("🎯 开始训练...")
        model.train()
        print("✅ 模型训练完成")
        
        # 测试补全功能
        print("\n🔮 测试知识图谱补全...")
        results = model.complete_triple(head="爱因斯坦", relation="提出了", top_k=3)
        print("✅ 补全功能测试成功")
        for i, (entity, score) in enumerate(results):
            print(f"   {i+1}. 爱因斯坦 --提出了--> {entity} (得分: {score:.3f})")
        
        print("\n🌐 测试链接预测...")
        predictions = model.predict_missing_links("爱因斯坦", top_k=3)
        print("✅ 链接预测功能测试成功")
        for i, (entity, relation, score) in enumerate(predictions):
            print(f"   {i+1}. 爱因斯坦 --{relation}--> {entity} (得分: {score:.3f})")
        
        print("\n🎉 所有基础功能测试通过！")
        print("\n🌐 现在可以运行以下命令启动Web服务:")
        print("   python app.py")
        print("   然后访问 http://localhost:5000")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_basic_functionality()
    if success:
        print("\n✅ 系统已就绪，可以开始使用！")
    else:
        print("\n❌ 请检查错误并修复后重试。")