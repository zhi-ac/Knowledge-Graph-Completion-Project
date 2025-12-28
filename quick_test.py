#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试脚本 - 验证知识图谱补全系统
"""

def quick_test():
    print("🧠 知识图谱补全系统快速测试")
    print("=" * 50)
    
    try:
        # 测试基本导入
        print("1. 测试模块导入...")
        from models.kg_data import KnowledgeGraph, KGDataset
        from models.transe import TransE
        print("   ✅ 所有模块导入成功")
        
        # 创建示例知识图谱
        print("\n2. 创建知识图谱...")
        kg = KGDataset.create_sample_dataset()
        print(f"   ✅ 创建成功: {kg.get_entity_count()}个实体, {kg.get_relation_count()}个关系")
        
        # 快速训练模型（小参数）
        print("\n3. 训练TransE模型...")
        model = TransE(kg, embedding_dim=10, epochs=5, learning_rate=0.1)
        model.train()
        print("   ✅ 模型训练完成")
        
        # 测试补全功能
        print("\n4. 测试知识图谱补全...")
        results = model.complete_triple(head="爱因斯坦", relation="提出了", top_k=3)
        print("   ✅ 补全结果:")
        for i, (entity, score) in enumerate(results):
            print(f"     {i+1}. 爱因斯坦 --提出了--> {entity} (得分: {score:.3f})")
        
        # 测试链接预测
        print("\n5. 测试链接预测...")
        predictions = model.predict_missing_links("爱因斯坦", top_k=3)
        print("   ✅ 预测结果:")
        for i, (entity, relation, score) in enumerate(predictions[:3]):
            print(f"     {i+1}. 爱因斯坦 --{relation}--> {entity} (得分: {score:.3f})")
        
        print("\n🎉 所有测试通过！系统运行正常！")
        print("\n🌐 启动Web界面测试:")
        print("   python app.py")
        print("   然后访问: http://localhost:5000")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = quick_test()
    input("\n按Enter键退出...")