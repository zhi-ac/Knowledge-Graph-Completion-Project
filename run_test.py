import sys
import os

# 添加项目路径
sys.path.append('.')

def test_knowledge_graph():
    """测试知识图谱基本功能"""
    print("测试知识图谱...")
    
    # 创建简单的知识图谱
    from models.kg_data import KnowledgeGraph
    
    kg = KnowledgeGraph()
    kg.add_triple("爱因斯坦", "提出了", "相对论")
    kg.add_triple("爱因斯坦", "出生于", "德国")
    kg.add_triple("德国", "位于", "欧洲")
    kg.build_mappings()
    
    print(f"✅ 知识图谱创建成功: {kg.get_entity_count()}个实体")
    return kg

def test_transse():
    """测试TransE算法"""
    print("测试TransE算法...")
    
    kg = test_knowledge_graph()
    
    # 创建并训练模型
    from models.transe import TransE
    
    model = TransE(kg, embedding_dim=10, epochs=3)
    model.train()
    
    print("✅ TransE模型训练完成")
    
    # 测试补全
    results = model.complete_triple(head="爱因斯坦", relation="提出了", top_k=3)
    print(f"✅ 补全功能正常: {len(results)}个结果")
    
    return model

def test_flask():
    """测试Flask应用"""
    print("测试Flask应用...")
    
    try:
        from app import app
        print("✅ Flask应用导入成功")
        return True
    except Exception as e:
        print(f"❌ Flask应用错误: {e}")
        return False

if __name__ == "__main__":
    print("🧠 知识图谱补全系统测试")
    print("=" * 40)
    
    try:
        # 1. 测试知识图谱
        kg = test_knowledge_graph()
        
        # 2. 测试TransE
        model = test_transse()
        
        # 3. 测试Flask
        flask_ok = test_flask()
        
        print("\n🎉 所有核心功能测试完成！")
        print("\n🌐 启动Web界面:")
        print("   python app.py")
        print("   访问: http://localhost:5000")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()