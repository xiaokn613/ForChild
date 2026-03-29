#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
家长端路由
"""

from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from models import get_db_connection
from datetime import datetime

bp = Blueprint('parent_routes', __name__, template_folder='templates')

@bp.route('/login')
def login():
    """家长登录页面"""
    return redirect(url_for('child_routes.login'))

@bp.route('/dashboard')
def dashboard():
    """家长控制台首页"""
    if 'user_id' not in session or session.get('role') != 'parent':
        return redirect(url_for('parent_routes.login'))
    
    conn = get_db_connection()
    
    # 获取所有儿童（只获取当前家长的孩子）
    children = conn.execute('''
        SELECT c.*, u.username as name
        FROM children c 
        JOIN users u ON c.user_id = u.id 
        WHERE c.parent_id = ?
    ''', (session['user_id'],)).fetchall()
    
    # 统计信息
    total_children = len(children)
    total_tasks = conn.execute('''
        SELECT COUNT(*) FROM daily_tasks 
        WHERE task_date = ?
    ''', (datetime.now().strftime('%Y-%m-%d'),)).fetchone()[0]
    
    completed_tasks = conn.execute('''
        SELECT COUNT(*) FROM daily_tasks 
        WHERE task_date = ? AND status = 'completed'
    ''', (datetime.now().strftime('%Y-%m-%d'),)).fetchone()[0]
    
    # 获取宠物领养关系
    adoptions = conn.execute('''
        SELECT p.*, c.nickname as child_name, ps.breed_name, ps.species,
               d.dict_value as species_name
        FROM pets p
        JOIN children c ON p.child_id = c.id
        LEFT JOIN pet_store ps ON p.type = ps.species AND p.name = ps.breed_name
        LEFT JOIN dictionaries d ON d.dict_type = 'pet_species' AND d.dict_key = ps.species
        WHERE c.parent_id = ?
        ORDER BY p.created_at DESC
    ''', (session['user_id'],)).fetchall()
    
    conn.close()
    
    return render_template('parent/dashboard.html', 
                         children=children,
                         total_children=total_children,
                         total_tasks=total_tasks,
                         completed_tasks=completed_tasks,
                         adoptions=adoptions)

@bp.route('/tasks')
def tasks():
    """任务管理页面"""
    if 'user_id' not in session or session.get('role') != 'parent':
        return redirect(url_for('parent_routes.login'))
    
    conn = get_db_connection()
    
    children = conn.execute("SELECT * FROM children").fetchall()
    templates = conn.execute('''
        SELECT tt.*, c.nickname as child_name 
        FROM task_templates tt
        JOIN children c ON tt.child_id = c.id
        ORDER BY tt.created_at DESC
    ''').fetchall()
    
    conn.close()
    
    return render_template('parent/tasks.html', children=children, templates=templates)

@bp.route('/shop')
def shop():
    """商城管理页面"""
    if 'user_id' not in session or session.get('role') != 'parent':
        return redirect(url_for('parent_routes.login'))
    
    conn = get_db_connection()
    items = conn.execute('''
        SELECT * FROM shop_items 
        ORDER BY category, price_stars
    ''').fetchall()
    
    # 获取商品类别字典
    categories_raw = conn.execute('''
        SELECT dict_key, dict_value 
        FROM dictionaries 
        WHERE dict_type = 'shop_category'
        ORDER BY sort_order
    ''').fetchall()
    
    # 构建类别字典：{key: value}
    categories = {}
    for row in categories_raw:
        categories[row['dict_key']] = row['dict_value']
    
    conn.close()
    
    return render_template('parent/shop.html', items=items, categories=dict(categories))

@bp.route('/statistics')
def statistics():
    """统计分析页面"""
    if 'user_id' not in session or session.get('role') != 'parent':
        return redirect(url_for('parent_routes.login'))
    
    conn = get_db_connection()
    
    children = conn.execute("SELECT * FROM children").fetchall()
    
    # 最近 7 天统计
    stats = conn.execute('''
        SELECT s.*, c.nickname as child_name
        FROM statistics s
        JOIN children c ON s.child_id = c.id
        ORDER BY s.stat_date DESC
        LIMIT 100
    ''').fetchall()
    
    conn.close()
    
    return render_template('parent/statistics.html', children=children, stats=stats)

@bp.route('/pets')
def pets():
    """宠物商城页面"""
    if 'user_id' not in session or session.get('role') != 'parent':
        return redirect(url_for('parent_routes.login'))
    
    conn = get_db_connection()
    
    # 获取宠物商城列表
    pet_store_items = conn.execute('''
        SELECT * FROM pet_store 
        ORDER BY adoption_fee DESC
    ''').fetchall()
    
    # 获取宠物物种字典
    pet_species_raw = conn.execute('''
        SELECT dict_key, dict_value 
        FROM dictionaries 
        WHERE dict_type = 'pet_species'
        ORDER BY sort_order
    ''').fetchall()
    
    # 构建字典：{key: value}
    pet_species = {}
    for row in pet_species_raw:
        pet_species[row['dict_key']] = row['dict_value']
    
    conn.close()
    
    return render_template('parent/pets.html', pet_store_items=pet_store_items, pet_species=dict(pet_species))

@bp.route('/wishlists')
def wishlists():
    """愿望单管理页面"""
    if 'user_id' not in session or session.get('role') != 'parent':
        return redirect(url_for('parent_routes.login'))
    
    conn = get_db_connection()
    
    children = conn.execute("SELECT * FROM children").fetchall()
    wishlists = conn.execute('''
        SELECT w.*, c.nickname as child_name
        FROM wishlists w
        JOIN children c ON w.child_id = c.id
        ORDER BY w.created_at DESC
    ''').fetchall()
    
    conn.close()
    
    return render_template('parent/wishlists.html', children=children, wishlists=wishlists)

@bp.route('/dictionaries')
def dictionaries():
    """字典管理页面"""
    if 'user_id' not in session or session.get('role') != 'parent':
        return redirect(url_for('parent_routes.login'))
    
    return render_template('parent/dictionaries.html')
