#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证系统基本功能
"""

print("🧠 知识图谱补全系统验证")
print("=" * 40)

# 1. 验证数据模型
try:
    from models.kg_data import KnowledgeGraph, KGDataset
    kg = KGDataset.create_sample_dataset()
    print(f"✅ 知识图谱数据模型: {kg.get_entity_count()}实体, {kg.get_relation_count()}关系, {kg.get_triple_count()}三元组")
except Exception as e:
    print(f"❌ 数据模型错误: {e}")

# 2. 验证Flask应用
try:
    from app import app
    print("✅ Flask Web应用: 导入成功")
except Exception as e:
    print(f"❌ Flask应用错误: {e}")

print("\n🎉 核心模块验证完成！")
print("🌐 启动命令: python app.py")
print("🌐 访问地址: http://localhost:5000")