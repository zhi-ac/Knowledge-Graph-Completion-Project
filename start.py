#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速启动脚本 - 自动初始化并启动应用
"""

import sys
import os

def setup_database():
    """设置数据库"""
    print("[DB] 初始化数据库...")
    
    try:
        # 尝试初始化数据库
        from init_database import create_database, load_sample_data
        
        if create_database():
            print("[SUCCESS] 数据库创建成功")
            
            # 加载示例数据
            if load_sample_data():
                print("[SUCCESS] 示例数据加载成功")
                return True
            else:
                print("[WARNING] 示例数据加载失败，但数据库可用")
                return True
        else:
            print("[ERROR] 数据库初始化失败")
            return False
            
    except ImportError as e:
        print(f"[ERROR] 缺少依赖: {e}")
        print("[INFO] 请运行: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"[ERROR] 数据库设置失败: {e}")
        print("[INFO] 将使用内存模式运行")
        return False

def start_app():
    """启动应用"""
    try:
        print("\n[START] 启动知识图谱补全系统...")
        print("[URL] 访问地址: http://localhost:5000")
        print("[INFO] 按Ctrl+C停止应用")
        print("-" * 50)
        
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n[INFO] 应用已停止")
    except Exception as e:
        print(f"[ERROR] 启动失败: {e}")

def main():
    """主函数"""
    print("[SYSTEM] 知识图谱补全系统 - 快速启动")
    print("=" * 50)
    
    # 检查参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "--no-db":
            print("[INFO] 跳过数据库初始化")
        elif sys.argv[1] == "--db-only":
            setup_database()
            return
        else:
            print("使用方法:")
            print("  python start.py         # 完整启动（含数据库初始化）")
            print("  python start.py --no-db  # 跳过数据库初始化")
            print("  python start.py --db-only # 仅初始化数据库")
            return
    
    # 默认启动流程
    if setup_database():
        start_app()
    else:
        print("\n[WARNING] 数据库初始化失败，是否继续启动应用？")
        choice = input("继续吗？(y/n): ").lower().strip()
        if choice in ['y', 'yes', '是']:
            start_app()
        else:
            print("[INFO] 启动已取消")

if __name__ == "__main__":
    main()