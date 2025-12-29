#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识图谱补全系统 - 主启动脚本
"""

import sys
import os

def main():
    """主启动函数"""
    print("🧠 知识图谱补全系统")
    print("=" * 40)
    
    # 检查数据库状态
    print("📊 检查数据库状态...")
    try:
        import pymysql
        conn = pymysql.connect(
            host='localhost', 
            user='root', 
            password='123456', 
            database='kgc_project'
        )
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM entities')
        entity_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM relations') 
        relation_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM triples')
        triple_count = cursor.fetchone()[0]
        
        print(f"   ✅ 实体: {entity_count} | 关系: {relation_count} | 三元组: {triple_count}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"   ⚠️  数据库连接失败: {e}")
        print("   💡 系统将使用内存模式运行")
    
    # 启动应用
    print("\n🚀 启动Web应用...")
    print("📍 访问地址: http://localhost:5000")
    print("💡 按Ctrl+C停止应用")
    print("-" * 40)
    
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n👋 应用已安全停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        print("💡 请检查端口5000是否被占用")

if __name__ == "__main__":
    main()