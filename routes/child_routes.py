#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
儿童端路由
"""

from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from models import get_db_connection
from datetime import datetime

bp = Blueprint('child_routes', __name__, template_folder='templates')

@bp.route('/login')
def login():
    """儿童登录页面"""
    return render_template('child/login.html')

@bp.route('/home')
def home():
    """儿童首页"""
    if 'user_id' not in session or session.get('role') != 'child':
        return redirect(url_for('child_routes.login'))
    
    conn = get_db_connection()
    child = conn.execute('''
        SELECT c.*, u.username 
        FROM children c 
        JOIN users u ON c.user_id = u.id 
        WHERE u.id = ?
    ''', (session['user_id'],)).fetchone()
    
    pet = conn.execute('''
        SELECT * FROM pets 
        WHERE child_id = ? AND is_active = 1 
        ORDER BY created_at DESC LIMIT 1
    ''', (child['id'],)).fetchone()
    
    conn.close()
    
    return render_template('child/home.html', child=child, pet=pet)

@bp.route('/tasks')
def tasks():
    """任务列表页面"""
    if 'user_id' not in session or session.get('role') != 'child':
        return redirect(url_for('child_routes.login'))
    
    conn = get_db_connection()
    child = conn.execute('''
        SELECT c.* FROM children c 
        JOIN users u ON c.user_id = u.id 
        WHERE u.id = ?
    ''', (session['user_id'],)).fetchone()
    
    # 获取今日任务
    today = datetime.now().strftime('%Y-%m-%d')
    tasks = conn.execute('''
        SELECT dt.*, tt.name, tt.description, tt.star_reward, tt.task_type
        FROM daily_tasks dt
        JOIN task_templates tt ON dt.template_id = tt.id
        WHERE dt.child_id = ? AND dt.task_date = ?
        ORDER BY tt.task_type, dt.id
    ''', (child['id'], today)).fetchall()
    
    conn.close()
    
    return render_template('child/tasks.html', child=child, tasks=tasks)

@bp.route('/pets')
def pets():
    """宠物页面"""
    if 'user_id' not in session or session.get('role') != 'child':
        return redirect(url_for('child_routes.login'))
    
    conn = get_db_connection()
    child = conn.execute('''
        SELECT c.* FROM children c 
        JOIN users u ON c.user_id = u.id 
        WHERE u.id = ?
    ''', (session['user_id'],)).fetchone()
    
    pet = conn.execute('''
        SELECT * FROM pets 
        WHERE child_id = ? AND is_active = 1 
        ORDER BY created_at DESC LIMIT 1
    ''', (child['id'],)).fetchone()
    
    conn.close()
    
    return render_template('child/pets.html', child=child, pet=pet)

@bp.route('/shop')
def shop():
    """商城页面"""
    if 'user_id' not in session or session.get('role') != 'child':
        return redirect(url_for('child_routes.login'))
    
    conn = get_db_connection()
    child = conn.execute('''
        SELECT c.* FROM children c 
        JOIN users u ON c.user_id = u.id 
        WHERE u.id = ?
    ''', (session['user_id'],)).fetchone()
    
    items = conn.execute('''
        SELECT * FROM shop_items 
        WHERE is_active = 1 
        ORDER BY category, price_stars
    ''').fetchall()
    
    conn.close()
    
    return render_template('child/shop.html', child=child, items=items)

@bp.route('/badges')
def badges():
    """徽章墙页面"""
    if 'user_id' not in session or session.get('role') != 'child':
        return redirect(url_for('child_routes.login'))
    
    conn = get_db_connection()
    child = conn.execute('''
        SELECT c.* FROM children c 
        JOIN users u ON c.user_id = u.id 
        WHERE u.id = ?
    ''', (session['user_id'],)).fetchone()
    
    all_badges = conn.execute('SELECT * FROM badges WHERE is_active = 1').fetchall()
    earned_badges = conn.execute('''
        SELECT b.* FROM badges b
        JOIN child_badges cb ON b.id = cb.badge_id
        WHERE cb.child_id = ?
    ''', (child['id'],)).fetchall()
    earned_ids = [b['id'] for b in earned_badges]
    
    conn.close()
    
    return render_template('child/badges.html', child=child, badges=all_badges, earned_ids=earned_ids)

@bp.route('/trophies')
def trophies():
    """奖杯墙页面"""
    if 'user_id' not in session or session.get('role') != 'child':
        return redirect(url_for('child_routes.login'))
    
    conn = get_db_connection()
    child = conn.execute('''
        SELECT c.* FROM children c 
        JOIN users u ON c.user_id = u.id 
        WHERE u.id = ?
    ''', (session['user_id'],)).fetchone()
    
    all_trophies = conn.execute('SELECT * FROM trophies WHERE is_active = 1').fetchall()
    earned_trophies = conn.execute('''
        SELECT t.*, ct.stars_awarded FROM trophies t
        JOIN child_trophies ct ON t.id = ct.trophy_id
        WHERE ct.child_id = ?
    ''', (child['id'],)).fetchall()
    earned_ids = [t['id'] for t in earned_trophies]
    
    conn.close()
    
    return render_template('child/trophies.html', child=child, trophies=all_trophies, earned_ids=earned_ids)

@bp.route('/wishlists')
def wishlists():
    """愿望单页面"""
    if 'user_id' not in session or session.get('role') != 'child':
        return redirect(url_for('child_routes.login'))
    
    conn = get_db_connection()
    child = conn.execute('''
        SELECT c.* FROM children c 
        JOIN users u ON c.user_id = u.id 
        WHERE u.id = ?
    ''', (session['user_id'],)).fetchone()
    
    wishlists = conn.execute('''
        SELECT * FROM wishlists 
        WHERE child_id = ? 
        ORDER BY is_completed, created_at DESC
    ''', (child['id'],)).fetchall()
    
    conn.close()
    
    return render_template('child/wishlists.html', child=child, wishlists=wishlists)
