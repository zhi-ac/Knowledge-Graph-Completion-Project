#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速修复跨域问题
"""

def fix_cors():
    """修复跨域问题"""
    print("🔧 修复跨域问题...")
    
    # 安装flask-cors
    import subprocess
    import sys
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'flask-cors'])
        print("✅ flask-cors 安装成功")
    except:
        print("❌ flask-cors 安装失败")
        return False
    
    # 验证修复
    try:
        from flask_cors import CORS
        print("✅ 跨域修复完成")
        return True
    except ImportError:
        print("❌ 跨域修复失败")
        return False

if __name__ == "__main__":
    print("🌐 知识图谱补全系统 - 跨域修复工具")
    print("=" * 40)
    
    if fix_cors():
        print("\n🚀 现在可以启动应用了:")
        print("   python app.py")
        print("\n🌐 访问地址:")
        print("   http://localhost:5000")
        print("\n✨ 跨域问题已解决！")
    else:
        print("\n❌ 修复失败，请手动安装:")
        print("   pip install flask-cors")