#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
宠物商城 API 接口
"""

from flask import Blueprint, jsonify, request, session, current_app
from models import get_db_connection
from datetime import datetime
import os
import random

bp = Blueprint('pet_store_api', __name__, url_prefix='/api/pet_store')

@bp.route('/add', methods=['POST'])
def add_pet_store_item():
    """家长新增宠物商城物品"""
    if 'user_id' not in session or session.get('role') != 'parent':
        return jsonify({'success': False, 'message': '未登录或无权限'}), 401
    
    breed_name = request.form.get('name')
    species = request.form.get('species', '')
    description = request.form.get('description', '')
    adoption_fee = int(request.form.get('adoption_fee', 0))
    
    # 验证必填项
    if not breed_name:
        return jsonify({
            'success': False,
            'message': '品种名称为必填项'
        }), 400
    
    conn = get_db_connection()
    try:
        image_filename = None
        
        # 处理图片上传
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                # 检查文件扩展名
                if '.' in file.filename and \
                   file.filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']:
                    # 生成唯一文件名
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    unique_filename = f"pet_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}.{ext}"
                    
                    # 保存文件
                    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename))
                    image_filename = f'/static/uploads/shop/{unique_filename}'
        
        # 插入数据库
        conn.execute('''
            INSERT INTO pet_store (breed_name, species, description, adoption_fee, image)
            VALUES (?, ?, ?, ?, ?)
        ''', (breed_name, species, description, adoption_fee, image_filename))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': '宠物品种添加成功'
        })
        
    except Exception as e:
        conn.rollback()
        return jsonify({
            'success': False,
            'message': f'添加失败：{str(e)}'
        }), 500
    finally:
        conn.close()

@bp.route('/<int:item_id>', methods=['GET'])
def get_pet_store_item(item_id):
    """获取宠物商城物品详情"""
    if 'user_id' not in session or session.get('role') != 'parent':
        return jsonify({'success': False, 'message': '未登录或无权限'}), 401
    
    conn = get_db_connection()
    try:
        item = conn.execute('''
            SELECT * FROM pet_store WHERE id = ?
        ''', (item_id,)).fetchone()
        
        if not item:
            return jsonify({
                'success': False,
                'message': '宠物品种不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': dict(item)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取失败：{str(e)}'
        }), 500
    finally:
        conn.close()

@bp.route('/<int:item_id>', methods=['PUT'])
def update_pet_store_item(item_id):
    """家长更新宠物商城物品"""
    if 'user_id' not in session or session.get('role') != 'parent':
        return jsonify({'success': False, 'message': '未登录或无权限'}), 401
    
    breed_name = request.form.get('name') or request.json.get('name') if request.is_json else None
    species = request.form.get('species') or request.json.get('species') if request.is_json else None
    description = request.form.get('description') or request.json.get('description', '') if request.is_json else ''
    adoption_fee = int(request.form.get('adoption_fee') or request.json.get('adoption_fee', 0)) if request.is_json else 0
    
    # 验证必填项
    if not breed_name:
        return jsonify({
            'success': False,
            'message': '品种名称为必填项'
        }), 400
    
    conn = get_db_connection()
    try:
        # 检查物品是否存在
        existing_item = conn.execute('''
            SELECT * FROM pet_store WHERE id = ?
        ''', (item_id,)).fetchone()
        
        if not existing_item:
            return jsonify({
                'success': False,
                'message': '宠物品种不存在'
            }), 404
        
        image_filename = None
        
        # 处理图片上传
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                # 检查文件扩展名
                if '.' in file.filename and \
                   file.filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']:
                    # 生成唯一文件名
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    unique_filename = f"pet_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}.{ext}"
                    
                    # 保存文件
                    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename))
                    image_filename = f'/static/uploads/shop/{unique_filename}'
        elif not request.is_json and request.form.get('image'):
            # 如果是表单数据且指定了图片 URL
            image_filename = request.form.get('image')
        elif request.is_json and request.json.get('image'):
            # 如果是 JSON 数据且指定了图片 URL
            image_filename = request.json.get('image')
        else:
            # 保持原有图片
            image_filename = existing_item['image']
        
        # 更新数据库
        conn.execute('''
            UPDATE pet_store 
            SET breed_name = ?, species = ?, description = ?, adoption_fee = ?, image = ?
            WHERE id = ?
        ''', (breed_name, species, description, adoption_fee, image_filename, item_id))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': '宠物品种更新成功'
        })
        
    except Exception as e:
        conn.rollback()
        return jsonify({
            'success': False,
            'message': f'更新失败：{str(e)}'
        }), 500
    finally:
        conn.close()

@bp.route('/<int:item_id>', methods=['DELETE'])
def delete_pet_store_item(item_id):
    """家长删除宠物商城物品"""
    if 'user_id' not in session or session.get('role') != 'parent':
        return jsonify({'success': False, 'message': '未登录或无权限'}), 401
    
    conn = get_db_connection()
    try:
        # 检查物品是否存在
        item = conn.execute('''
            SELECT * FROM pet_store WHERE id = ?
        ''', (item_id,)).fetchone()
        
        if not item:
            return jsonify({
                'success': False,
                'message': '宠物品种不存在'
            }), 404
        
        # 删除物品
        conn.execute('DELETE FROM pet_store WHERE id = ?', (item_id,))
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': '宠物品种删除成功'
        })
        
    except Exception as e:
        conn.rollback()
        return jsonify({
            'success': False,
            'message': f'删除失败：{str(e)}'
        }), 500
    finally:
        conn.close()

@bp.route('/<int:item_id>/toggle', methods=['PUT'])
def toggle_pet_store_item(item_id):
    """家长上下架宠物商城物品"""
    if 'user_id' not in session or session.get('role') != 'parent':
        return jsonify({'success': False, 'message': '未登录或无权限'}), 401
    
    data = request.json
    is_active = data.get('is_active', True)
    
    conn = get_db_connection()
    try:
        # 检查物品是否存在
        existing_item = conn.execute('''
            SELECT * FROM pet_store WHERE id = ?
        ''', (item_id,)).fetchone()
        
        if not existing_item:
            return jsonify({
                'success': False,
                'message': '宠物品种不存在'
            }), 404
        
        # 更新状态
        conn.execute('''
            UPDATE pet_store SET is_active = ? WHERE id = ?
        ''', (1 if is_active else 0, item_id))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': '操作成功'
        })
        
    except Exception as e:
        conn.rollback()
        return jsonify({
            'success': False,
            'message': f'操作失败：{str(e)}'
        }), 500
    finally:
        conn.close()

@bp.route('/<int:item_id>/adopt', methods=['POST'])
def adopt_pet(item_id):
    """孩子领养宠物（消耗星星）"""
    if 'user_id' not in session or session.get('role') != 'child':
        return jsonify({'success': False, 'message': '未登录或无权限'}), 401
    
    conn = get_db_connection()
    try:
        # 获取当前孩子的信息
        child = conn.execute('''
            SELECT c.* FROM children c
            JOIN users u ON c.user_id = u.id
            WHERE u.id = ?
        ''', (session['user_id'],)).fetchone()
        
        if not child:
            return jsonify({
                'success': False,
                'message': '孩子信息不存在'
            }), 404
        
        # 获取宠物品种信息
        pet_store_item = conn.execute('''
            SELECT * FROM pet_store WHERE id = ?
        ''', (item_id,)).fetchone()
        
        if not pet_store_item:
            return jsonify({
                'success': False,
                'message': '宠物品种不存在'
            }), 404
        
        # 检查星星是否足够
        adoption_fee = pet_store_item['adoption_fee']
        if child['total_stars'] < adoption_fee:
            return jsonify({
                'success': False,
                'message': f'星星不足！需要 {adoption_fee} 颗星星，您只有 {child["total_stars"]} 颗'
            }), 400
        
        # 扣除星星
        conn.execute('''
            UPDATE children SET total_stars = total_stars - ? WHERE id = ?
        ''', (adoption_fee, child['id']))
        
        # 记录星星消费
        conn.execute('''
            INSERT INTO star_records (child_id, amount, type, source, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (child['id'], adoption_fee, 'spend', '领养宠物', f'领养{pet_store_item["breed_name"]}'))
        
        # 创建宠物实例
        conn.execute('''
            INSERT INTO pets (child_id, name, type, gender, color, hunger, cleanliness, mood)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            child['id'],
            pet_store_item['breed_name'],
            pet_store_item['species'] or 'dog',
            'male',  # 默认性别
            'brown',  # 默认颜色
            100,  # 饱腹度
            100,  # 清洁度
            100   # 心情
        ))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': f'领养成功！扣除 {adoption_fee} 颗星星，{pet_store_item["breed_name"]} 已成为您的宠物'
        })
        
    except Exception as e:
        conn.rollback()
        return jsonify({
            'success': False,
            'message': f'领养失败：{str(e)}'
        }), 500
    finally:
        conn.close()

@bp.route('/<int:item_id>/assign', methods=['POST'])
def assign_pet(item_id):
    """家长为孩子分配宠物（不消耗星星）"""
    if 'user_id' not in session or session.get('role') != 'parent':
        return jsonify({'success': False, 'message': '未登录或无权限'}), 401
    
    data = request.json
    child_name = data.get('child_name', '').strip()
    
    if not child_name:
        return jsonify({
            'success': False,
            'message': '请输入孩子姓名'
        }), 400
    
    conn = get_db_connection()
    try:
        # 根据姓名或昵称查找孩子
        child = conn.execute('''
            SELECT c.*, u.username 
            FROM children c
            JOIN users u ON c.user_id = u.id
            WHERE (c.nickname = ? OR u.username = ?)
        ''', (child_name, child_name)).fetchone()
        
        if not child:
            return jsonify({
                'success': False,
                'message': f'未找到名为 "{child_name}" 的孩子'
            }), 404
        
        # 获取宠物品种信息
        pet_store_item = conn.execute('''
            SELECT * FROM pet_store WHERE id = ?
        ''', (item_id,)).fetchone()
        
        if not pet_store_item:
            return jsonify({
                'success': False,
                'message': '宠物品种不存在'
            }), 404
        
        # 创建宠物实例（不消耗星星）
        conn.execute('''
            INSERT INTO pets (child_id, name, type, gender, color, hunger, cleanliness, mood)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            child['id'],
            pet_store_item['breed_name'],
            pet_store_item['species'] or 'dog',
            'male',  # 默认性别
            'brown',  # 默认颜色
            100,  # 饱腹度
            100,  # 清洁度
            100   # 心情
        ))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': f'分配成功！{pet_store_item["breed_name"]} 已成为 {child["nickname"]} 的宠物'
        })
        
    except Exception as e:
        conn.rollback()
        return jsonify({
            'success': False,
            'message': f'分配失败：{str(e)}'
        }), 500
    finally:
        conn.close()
