#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复跨域问题并启动应用
"""

import sys
import subprocess

def install_dependencies():
    """安装必要的依赖"""
    print("📦 检查并安装依赖...")
    
    try:
        import flask_cors
        print("✅ flask-cors 已安装")
    except ImportError:
        print("📦 正在安装 flask-cors...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'flask-cors'])
        print("✅ flask-cors 安装完成")
    
    try:
        import pymysql
        print("✅ pymysql 已安装")
    except ImportError:
        print("📦 正在安装 pymysql...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pymysql'])
        print("✅ pymysql 安装完成")
    
    try:
        import sqlalchemy
        print("✅ sqlalchemy 已安装")
    except ImportError:
        print("📦 正在安装 sqlalchemy...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'sqlalchemy'])
        print("✅ sqlalchemy 安装完成")

def test_database_connection():
    """测试数据库连接"""
    try:
        import pymysql
        conn = pymysql.connect(host='localhost', user='root', password='123456', database='kgc_project')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM entities')
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        print(f"✅ 数据库连接正常，包含 {count} 个实体")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

def launch_app():
    """启动应用"""
    print("\n🚀 启动知识图谱补全系统...")
    print("📍 访问地址: http://localhost:5000")
    print("🔧 跨域问题已修复")
    print("💡 按Ctrl+C停止应用")
    print("-" * 60)
    
    try:
        from app import app
        
        # 设置更好的启动参数
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            threaded=True
        )
        
    except KeyboardInterrupt:
        print("\n👋 应用已安全停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        print("💡 请检查端口5000是否被占用")

def main():
    """主函数"""
    print("🔧 知识图谱补全系统 - 修复并启动")
    print("=" * 50)
    
    # 1. 安装依赖
    install_dependencies()
    
    # 2. 测试数据库
    print("\n🗄️  测试数据库连接...")
    db_ok = test_database_connection()
    
    # 3. 启动应用
    if db_ok:
        print("\n✅ 环境检查通过，启动应用...")
        launch_app()
    else:
        print("\n⚠️  数据库连接失败，但仍可使用内存模式")
        choice = input("是否继续启动？(y/n): ").lower().strip()
        if choice in ['y', 'yes', '是']:
            launch_app()
        else:
            print("👋 启动已取消")

if __name__ == "__main__":
    main()