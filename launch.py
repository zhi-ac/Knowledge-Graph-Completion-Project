#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识图谱补全系统 - 演示启动脚本
"""

def main():
    print("🧠 知识图谱补全系统 - 完整演示")
    print("=" * 60)
    
    print("📋 系统功能:")
    print("   ✅ 知识图谱数据管理")
    print("   ✅ MySQL数据库存储")
    print("   ✅ TransE算法训练")
    print("   ✅ 知识图谱补全")
    print("   ✅ 智能链接预测")
    print("   ✅ 交互式可视化")
    
    print("\n🗄️  数据库状态:")
    try:
        import pymysql
        conn = pymysql.connect(host='localhost', user='root', password='123456', database='kgc_project')
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM entities')
        entity_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM relations') 
        relation_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM triples')
        triple_count = cursor.fetchone()[0]
        
        print(f"   📊 实体数量: {entity_count}")
        print(f"   🔗 关系数量: {relation_count}")
        print(f"   📝 三元组数量: {triple_count}")
        print("   ✅ 数据库连接正常")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"   ❌ 数据库连接失败: {e}")
        print("   💡 将使用内存模式")
    
    print("\n🚀 启动步骤:")
    print("   1. 运行: python app.py")
    print("   2. 访问: http://localhost:5000")
    print("   3. 点击 '🚀 初始化知识图谱'")
    print("   4. 点击 '🎯 训练模型'")
    print("   5. 体验知识图谱补全功能")
    
    print("\n💡 演示示例:")
    print("   📝 添加三元组: 居里夫人 → 发现了 → 镭")
    print("   🔮 知识补全: 爱因斯坦 → 提出了 → ?")
    print("   🔗 链接预测: ?")
    
    print("\n🌟 特色功能:")
    print("   🎯 智能补全: 基于TransE算法的实体预测")
    print("   🔗 关系发现: 发现实体间的潜在关联") 
    print("   📊 实时可视化: 交互式知识图谱展示")
    print("   💾 数据持久化: MySQL数据库存储")
    print("   🔄 混合模式: 内存性能+数据库安全")
    
    print("\n" + "=" * 60)
    print("🎉 系统已完全就绪！现在运行 python app.py 开始体验")
    
    # 询问是否直接启动
    choice = input("\n🚀 是否立即启动应用？(y/n): ").lower().strip()
    if choice in ['y', 'yes', '是']:
        print("\n🚀 正在启动应用...")
        try:
            from app import app
            app.run(debug=True, host='0.0.0.0', port=5000)
        except KeyboardInterrupt:
            print("\n👋 应用已停止")
        except Exception as e:
            print(f"\n❌ 启动失败: {e}")
    else:
        print("\n💡 记得运行 'python app.py' 来启动系统")

if __name__ == "__main__":
    main()