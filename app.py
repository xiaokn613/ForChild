#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
儿童任务激励网站 - 主应用入口
基于 Flask + SQLite + Vue.js 3
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from datetime import datetime, timedelta
import sqlite3
import os
import json

# 导入数据库模型
from models import init_db, get_db_connection
from routes import child_routes, parent_routes, api_routes

def create_app():
    app = Flask(__name__)
    app.secret_key = 'forchild_secret_key_2026'  # 用于 session 加密
    
    # 启用 CORS
    CORS(app)
    
    # 初始化数据库
    init_db()
    
    # 注册路由蓝图
    app.register_blueprint(child_routes.bp, url_prefix='/child')
    app.register_blueprint(parent_routes.bp, url_prefix='/parent')
    app.register_blueprint(api_routes.bp, url_prefix='/api')
    
    # 首页重定向到登录页
    @app.route('/')
    def index():
        return redirect(url_for('child_routes.login'))
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': '页面未找到'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': '服务器内部错误'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("=" * 60)
    print("🎉 儿童任务激励网站启动成功！")
    print("=" * 60)
    print("📱 儿童端访问：http://localhost:28080/child/login")
    print("👨‍👩‍👧 家长端访问：http://localhost:28080/parent/login")
    print("🛑 按 Ctrl+C 停止服务")
    print("=" * 60)
    app.run(host='0.0.0.0', port=28080, debug=True)
