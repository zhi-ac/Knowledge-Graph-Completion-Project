#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
"""

import sys
import os

def create_database():
    """创建数据库和表"""
    try:
        print("[INIT] 开始初始化数据库...")
        
        # 导入配置
        from config import Config
        print(f"数据库配置: {Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}")
        
        # 连接MySQL并创建数据库
        import pymysql
        connection = pymysql.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            port=Config.DB_PORT,
            charset=Config.DB_CHARSET
        )
        
        cursor = connection.cursor()
        
        # 创建数据库（如果不存在）
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DB_NAME} CHARACTER SET {Config.DB_CHARSET} COLLATE {Config.DB_CHARSET}_unicode_ci")
        print(f"[SUCCESS] 数据库 '{Config.DB_NAME}' 创建成功")
        
        cursor.close()
        connection.close()
        
        # 初始化表结构
        from models.database import init_database
        if init_database():
            print("[SUCCESS] 数据库表结构创建成功")
            return True
        else:
            print("[ERROR] 数据库表结构创建失败")
            return False
            
    except ImportError:
        print("[ERROR] 请先安装依赖: pip install pymysql sqlalchemy")
        return False
    except Exception as e:
        print(f"[ERROR] 数据库初始化失败: {e}")
        print("[INFO] 请检查MySQL服务是否启动，连接信息是否正确")
        return False

def test_connection():
    """测试数据库连接"""
    try:
        from models.database import init_database, KGDatabase
        
        if init_database():
            stats = KGDatabase.get_statistics()
            print("[SUCCESS] 数据库连接测试成功")
            print(f"[STATS] 当前统计: {stats}")
            return True
        else:
            print("[ERROR] 数据库连接测试失败")
            return False
            
    except Exception as e:
        print(f"[ERROR] 连接测试失败: {e}")
        return False

def load_sample_data():
    """加载示例数据到数据库"""
    try:
        from models.database import KGDatabase, init_database
        
        if not init_database():
            return False
        
        print("[LOAD] 加载示例数据到数据库...")
        
        from models.kg_data import KGDataset
        sample_kg = KGDataset.create_sample_dataset()
        
        success_count = 0
        for head, relation, tail in sample_kg.triples:
            if KGDatabase.add_triple(head, relation, tail):
                success_count += 1
        
        print(f"[SUCCESS] 成功加载 {success_count}/{len(sample_kg.triples)} 个三元组")
        
        # 显示统计信息
        stats = KGDatabase.get_statistics()
        print(f"[STATS] 数据库统计: {stats}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 加载示例数据失败: {e}")
        return False

if __name__ == "__main__":
    print("[DB] 知识图谱数据库初始化工具")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "create":
            create_database()
        elif command == "test":
            test_connection()
        elif command == "sample":
            load_sample_data()
        else:
            print("[ERROR] 未知命令")
    else:
        print("使用方法:")
        print("  python init_database.py create  # 创建数据库和表")
        print("  python init_database.py test    # 测试数据库连接")
        print("  python init_database.py sample  # 加载示例数据")
        print("\n[INFO] 推荐执行顺序:")
        print("  1. python init_database.py create")
        print("  2. python init_database.py sample")
        print("  3. python app.py")