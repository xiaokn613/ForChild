#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
一键启动脚本 - 儿童任务激励网站
兼容 Mac 和 Windows 系统
"""

import os
import sys
import subprocess
import platform

def print_banner():
    """打印启动横幅"""
    print("=" * 60)
    print("🎉 儿童任务激励网站 - 一键启动")
    print("=" * 60)

def check_python_version():
    """检查 Python 版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ 错误：需要 Python 3.8 或更高版本")
        print(f"当前版本：Python {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python 版本：{version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """安装依赖包"""
    print("\n📦 正在检查并安装依赖...")
    try:
        # 检查 requirements.txt 是否存在
        if not os.path.exists('requirements.txt'):
            print("❌ 未找到 requirements.txt 文件")
            return False
        
        # 使用 pip 安装依赖
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ 依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败：{e}")
        return False
    except Exception as e:
        print(f"❌ 发生错误：{e}")
        return False

def init_database():
    """初始化数据库"""
    print("\n🗄️ 正在初始化数据库...")
    try:
        from models import init_db
        init_db()
        print("✅ 数据库初始化完成")
        return True
    except Exception as e:
        print(f"❌ 数据库初始化失败：{e}")
        return False

def start_server():
    """启动服务器"""
    print("\n🚀 正在启动服务器...")
    try:
        from app import create_app
        app = create_app()
        print("\n" + "=" * 60)
        print("✅ 服务器启动成功！")
        print("=" * 60)
        print("📱 儿童端访问：http://localhost:28080/child/login")
        print("👨‍👩‍👧 家长端访问：http://localhost:28080/parent/login")
        print("=" * 60)
        print("💡 默认账号:")
        print("   儿童端：用户名 child / 密码 123456")
        print("   家长端：用户名 parent / 密码 123456")
        print("=" * 60)
        print("🛑 按 Ctrl+C 停止服务")
        print("=" * 60 + "\n")
        
        # 启动 Flask 应用（启用调试模式，支持热更新）
        app.run(host='0.0.0.0', port=28080, debug=True)
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")
    except Exception as e:
        print(f"\n❌ 服务器启动失败：{e}")
        return False
    
    return True

def main():
    """主函数"""
    print_banner()
    
    # 获取系统信息
    system = platform.system()
    print(f"💻 操作系统：{system}")
    
    # 检查 Python 版本
    if not check_python_version():
        sys.exit(1)
    
    # 安装依赖
    if not install_dependencies():
        sys.exit(1)
    
    # 初始化数据库
    if not init_database():
        sys.exit(1)
    
    # 启动服务器
    if not start_server():
        sys.exit(1)

if __name__ == '__main__':
    main()
