#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API 接口路由
提供前后端数据交互
"""

from flask import Blueprint, jsonify, request, session
from models import get_db_connection
from datetime import datetime, timedelta
import json

bp = Blueprint('api_routes', __name__)

# ==================== 认证相关 ====================

@bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')  # 'child' or 'parent'
    
    conn = get_db_connection()
    user = conn.execute('''
        SELECT * FROM users 
        WHERE username = ? AND password = ? AND role = ? AND is_active = 1
    ''', (username, password, role)).fetchone()
    
    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        
        return jsonify({
            'success': True,
            'message': '登录成功',
            'data': {
                'user_id': user['id'],
                'username': user['username'],
                'role': user['role']
            }
        })
    else:
        return jsonify({
            'success': False,
            'message': '用户名或密码错误'
        }), 401
    
    conn.close()

@bp.route('/logout', methods=['POST'])
def logout():
    """用户登出"""
    session.clear()
    return jsonify({'success': True, 'message': '已退出登录'})

@bp.route('/check-auth', methods=['GET'])
def check_auth():
    """检查登录状态"""
    if 'user_id' in session:
        return jsonify({
            'success': True,
            'authenticated': True,
            'data': {
                'user_id': session['user_id'],
                'username': session['username'],
                'role': session['role']
            }
        })
    return jsonify({
        'success': True,
        'authenticated': False
    })

# ==================== 儿童数据 ====================

@bp.route('/child/info', methods=['GET'])
def get_child_info():
    """获取儿童信息"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    conn = get_db_connection()
    child = conn.execute('''
        SELECT c.*, u.username 
        FROM children c 
        JOIN users u ON c.user_id = u.id 
        WHERE u.id = ?
    ''', (session['user_id'],)).fetchone()
    
    if child:
        return jsonify({'success': True, 'data': dict(child)})
    return jsonify({'success': False, 'message': '未找到儿童信息'}), 404
    
    conn.close()

@bp.route('/child/pet', methods=['GET'])
def get_child_pet():
    """获取儿童的宠物信息"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    conn = get_db_connection()
    child = conn.execute('''
        SELECT c.* FROM children c 
        JOIN users u ON c.user_id = u.id 
        WHERE u.id = ?
    ''', (session['user_id'],)).fetchone()
    
    if not child:
        return jsonify({'success': False, 'message': '未找到儿童信息'}), 404
    
    pet = conn.execute('''
        SELECT * FROM pets 
        WHERE child_id = ? AND is_active = 1 
        ORDER BY created_at DESC LIMIT 1
    ''', (child['id'],)).fetchone()
    
    conn.close()
    
    if pet:
        return jsonify({'success': True, 'data': dict(pet)})
    return jsonify({'success': True, 'data': None})  # 没有宠物

@bp.route('/children/add', methods=['POST'])
def add_child():
    """家长新增孩子账号"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    data = request.json
    name = data.get('name')
    nickname = data.get('nickname')
    birthday = data.get('birthday')
    avatar = data.get('avatar')
    preset_stars = data.get('preset_stars', 0)
    preset_badges = data.get('preset_badges', 0)
    preset_trophies = data.get('preset_trophies', 0)
    
    # 验证必填项
    if not name or not nickname:
        return jsonify({
            'success': False,
            'message': '姓名和昵称为必填项'
        }), 400
    
    parent_id = session['user_id']
    
    conn = get_db_connection()
    try:
        # 检查昵称是否已存在
        existing = conn.execute('''
            SELECT id FROM users 
            WHERE username = ? AND role = 'child'
        ''', (nickname,)).fetchone()
        
        if existing:
            return jsonify({
                'success': False,
                'message': '该昵称已被使用，请换一个'
            }), 400
        
        # 创建用户账号
        default_password = '123456'  # 默认密码
        cursor = conn.execute('''
            INSERT INTO users (username, password, role, is_active)
            VALUES (?, ?, 'child', 1)
        ''', (nickname, default_password))
        
        child_user_id = cursor.lastrowid
        
        # 创建儿童详细信息
        conn.execute('''
            INSERT INTO children (user_id, parent_id, nickname, birthday, avatar, total_stars, total_badges, total_trophies)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (child_user_id, parent_id, nickname, birthday, avatar, preset_stars, preset_badges, preset_trophies))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': '孩子账号创建成功',
            'data': {
                'child_user_id': child_user_id,
                'nickname': nickname,
                'default_password': default_password
            }
        })
        
    except Exception as e:
        conn.rollback()
        return jsonify({
            'success': False,
            'message': f'创建失败：{str(e)}'
        }), 500
    finally:
        conn.close()

@bp.route('/children/list', methods=['GET'])
def get_children_list():
    """获取当前家长的所有孩子列表"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    parent_id = session['user_id']
    
    conn = get_db_connection()
    try:
        children = conn.execute('''
            SELECT c.*, u.username as name
            FROM children c
            JOIN users u ON c.user_id = u.id
            WHERE c.parent_id = ?
        ''', (parent_id,)).fetchall()
        
        return jsonify({
            'success': True,
            'data': [dict(c) for c in children]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取失败：{str(e)}'
        }), 500
    finally:
        conn.close()

@bp.route('/children/detail/<int:child_id>', methods=['GET'])
def get_child_detail(child_id):
    """获取孩子详细信息"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    parent_id = session['user_id']
    
    conn = get_db_connection()
    try:
        # 获取孩子信息（包括 user 表的 name 字段）
        child = conn.execute('''
            SELECT c.*, u.username as name
            FROM children c
            JOIN users u ON c.user_id = u.id
            WHERE c.id = ? AND c.parent_id = ?
        ''', (child_id, parent_id)).fetchone()
        
        if not child:
            return jsonify({
                'success': False,
                'message': '孩子不存在或不属于您'
            }), 404
        
        return jsonify({
            'success': True,
            'data': dict(child)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取失败：{str(e)}'
        }), 500
    finally:
        conn.close()

@bp.route('/children/update/<int:child_id>', methods=['PUT'])
def update_child(child_id):
    """更新孩子信息"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    data = request.json
    name = data.get('name')
    nickname = data.get('nickname')
    birthday = data.get('birthday')
    avatar = data.get('avatar')
    total_stars = data.get('total_stars', 0)
    total_badges = data.get('total_badges', 0)
    total_trophies = data.get('total_trophies', 0)
    
    # 验证必填项
    if not name or not nickname:
        return jsonify({
            'success': False,
            'message': '姓名和昵称为必填项'
        }), 400
    
    parent_id = session['user_id']
    
    conn = get_db_connection()
    try:
        # 检查孩子是否存在且属于当前家长
        child = conn.execute('''
            SELECT c.*, u.username as old_name
            FROM children c
            JOIN users u ON c.user_id = u.id
            WHERE c.id = ? AND c.parent_id = ?
        ''', (child_id, parent_id)).fetchone()
        
        if not child:
            return jsonify({
                'success': False,
                'message': '孩子不存在或不属于您'
            }), 404
        
        # 如果昵称有变化，检查新昵称是否已被使用
        if nickname != child['nickname']:
            existing = conn.execute('''
                SELECT id FROM users 
                WHERE username = ? AND role = 'child' AND id != ?
            ''', (nickname, child['user_id'])).fetchone()
            
            if existing:
                return jsonify({
                    'success': False,
                    'message': '该昵称已被使用，请换一个'
                }), 400
            
            # 更新 users 表中的用户名
            conn.execute('''
                UPDATE users SET username = ? WHERE id = ?
            ''', (nickname, child['user_id']))
        
        # 更新 children 表中的其他信息
        conn.execute('''
            UPDATE children 
            SET birthday = ?, avatar = ?, total_stars = ?, total_badges = ?, total_trophies = ?
            WHERE id = ?
        ''', (birthday, avatar, total_stars, total_badges, total_trophies, child_id))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': '孩子信息更新成功'
        })
        
    except Exception as e:
        conn.rollback()
        return jsonify({
            'success': False,
            'message': f'更新失败：{str(e)}'
        }), 500
    finally:
        conn.close()

# ==================== 任务相关 ====================

@bp.route('/tasks/templates', methods=['GET'])
def get_task_templates():
    """获取任务模板列表（家长端）"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    parent_id = session['user_id']
    
    conn = get_db_connection()
    try:
        # 获取当前家长创建的所有任务模板（包括失活的，但不包括删除的）
        # 使用 LEFT JOIN 提高性能
        templates = conn.execute('''
            SELECT tt.id, tt.name, tt.description, tt.child_id, tt.task_type,
                   tt.star_reward, tt.badge_reward, tt.trophy_reward,
                   tt.schedule_time, tt.schedule_time_start, tt.schedule_time_end,
                   tt.repeat_days, tt.is_active, tt.created_at,
                   c.nickname as child_name
            FROM task_templates tt
            LEFT JOIN children c ON tt.child_id = c.id
            WHERE tt.parent_id = ? AND tt.is_deleted = 0
            ORDER BY tt.created_at DESC
        ''', (parent_id,)).fetchall()
        
        # 手动转换为字典列表（更高效）
        result = []
        for t in templates:
            result.append({
                'id': t['id'],
                'name': t['name'],
                'description': t['description'],
                'child_id': t['child_id'],
                'task_type': t['task_type'],
                'star_reward': t['star_reward'],
                'badge_reward': t['badge_reward'],
                'trophy_reward': t['trophy_reward'],
                'schedule_time': t['schedule_time'],
                'schedule_time_start': t['schedule_time_start'],
                'schedule_time_end': t['schedule_time_end'],
                'repeat_days': t['repeat_days'],
                'is_active': bool(t['is_active']),
                'created_at': t['created_at'],
                'child_name': t['child_name']
            })
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取失败：{str(e)}'
        }), 500
    finally:
        conn.close()

@bp.route('/tasks/template/add', methods=['POST'])
def add_task_template():
    """新增任务模板"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    data = request.json
    name = data.get('name')
    description = data.get('description', '')
    child_id = data.get('child_id')
    task_type = data.get('task_type', 'daily')
    star_reward = data.get('star_reward', 0)
    badge_reward = data.get('badge_reward', 0)
    trophy_reward = data.get('trophy_reward', 0)
    schedule_time_start = data.get('schedule_time_start')
    schedule_time_end = data.get('schedule_time_end')
    repeat_days = data.get('repeat_days', '')
    
    # 验证必填项
    if not name:
        return jsonify({'success': False, 'message': '任务名称不能为空'}), 400
    
    if not child_id:
        return jsonify({'success': False, 'message': '请选择孩子'}), 400
    
    # 校验时间范围
    if schedule_time_start and schedule_time_end:
        if schedule_time_end <= schedule_time_start:
            return jsonify({'success': False, 'message': '结束时间不能早于或等于开始时间'}), 400
    
    parent_id = session['user_id']
    
    conn = get_db_connection()
    try:
        # 验证孩子是否属于当前家长
        child = conn.execute('''
            SELECT id FROM children WHERE id = ? AND parent_id = ?
        ''', (child_id, parent_id)).fetchone()
        
        if not child:
            return jsonify({'success': False, 'message': '孩子不存在或不属于您'}), 404
        
        # 创建任务模板
        cursor = conn.execute('''
            INSERT INTO task_templates (
                parent_id, child_id, name, description, task_type, 
                star_reward, badge_reward, trophy_reward, 
                schedule_time_start, schedule_time_end, repeat_days, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        ''', (parent_id, child_id, name, description, task_type, 
              star_reward, badge_reward, trophy_reward, schedule_time_start, schedule_time_end, repeat_days))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': '任务模板创建成功',
            'data': {
                'template_id': cursor.lastrowid
            }
        })
    except Exception as e:
        conn.rollback()
        return jsonify({
            'success': False,
            'message': f'创建失败：{str(e)}'
        }), 500
    finally:
        conn.close()

@bp.route('/tasks/template/<int:template_id>', methods=['GET'])
def get_task_template(template_id):
    """获取单个任务模板详情"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    parent_id = session['user_id']
    
    conn = get_db_connection()
    try:
        template = conn.execute('''
            SELECT tt.*, c.nickname as child_name
            FROM task_templates tt
            JOIN children c ON tt.child_id = c.id
            WHERE tt.id = ? AND tt.parent_id = ? AND tt.is_deleted = 0
        ''', (template_id, parent_id)).fetchone()
        
        if not template:
            return jsonify({
                'success': False,
                'message': '任务模板不存在或不属于您'
            }), 404
        
        return jsonify({
            'success': True,
            'data': dict(template)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取失败：{str(e)}'
        }), 500
    finally:
        conn.close()

@bp.route('/tasks/template/<int:template_id>', methods=['PUT'])
def update_task_template(template_id):
    """更新任务模板"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    data = request.json
    name = data.get('name')
    description = data.get('description', '')
    child_id = data.get('child_id')
    task_type = data.get('task_type', 'daily')
    star_reward = data.get('star_reward', 0)
    badge_reward = data.get('badge_reward', 0)
    trophy_reward = data.get('trophy_reward', 0)
    schedule_time_start = data.get('schedule_time_start')
    schedule_time_end = data.get('schedule_time_end')
    repeat_days = data.get('repeat_days', '')
    
    # 验证必填项
    if not name:
        return jsonify({'success': False, 'message': '任务名称不能为空'}), 400
    
    if not child_id:
        return jsonify({'success': False, 'message': '请选择孩子'}), 400
    
    # 校验时间范围
    if schedule_time_start and schedule_time_end:
        if schedule_time_end <= schedule_time_start:
            return jsonify({'success': False, 'message': '结束时间不能早于或等于开始时间'}), 400
    
    parent_id = session['user_id']
    
    conn = get_db_connection()
    try:
        # 验证任务模板是否存在且属于当前家长（未删除的）
        template = conn.execute('''
            SELECT id FROM task_templates WHERE id = ? AND parent_id = ? AND is_deleted = 0
        ''', (template_id, parent_id)).fetchone()
        
        if not template:
            return jsonify({'success': False, 'message': '任务模板不存在或不属于您'}), 404
        
        # 验证孩子是否属于当前家长
        child = conn.execute('''
            SELECT id FROM children WHERE id = ? AND parent_id = ?
        ''', (child_id, parent_id)).fetchone()
        
        if not child:
            return jsonify({'success': False, 'message': '孩子不存在或不属于您'}), 404
        
        # 更新任务模板
        conn.execute('''
            UPDATE task_templates 
            SET name = ?, description = ?, child_id = ?, task_type = ?,
                star_reward = ?, badge_reward = ?, trophy_reward = ?,
                schedule_time_start = ?, schedule_time_end = ?, repeat_days = ?
            WHERE id = ?
        ''', (name, description, child_id, task_type, star_reward, badge_reward, 
              trophy_reward, schedule_time_start, schedule_time_end, repeat_days, template_id))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': '任务模板更新成功'
        })
    except Exception as e:
        conn.rollback()
        return jsonify({
            'success': False,
            'message': f'更新失败：{str(e)}'
        }), 500
    finally:
        conn.close()

@bp.route('/tasks/template/<int:template_id>', methods=['DELETE'])
def delete_task_template(template_id):
    """删除任务模板（软删除）"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    parent_id = session['user_id']
    
    conn = get_db_connection()
    try:
        # 验证任务模板是否存在且属于当前家长
        template = conn.execute('''
            SELECT id FROM task_templates WHERE id = ? AND parent_id = ?
        ''', (template_id, parent_id)).fetchone()
        
        if not template:
            return jsonify({'success': False, 'message': '任务模板不存在或不属于您'}), 404
        
        # 软删除：设置 is_deleted = 1
        conn.execute('''
            UPDATE task_templates SET is_deleted = 1 WHERE id = ?
        ''', (template_id,))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': '任务模板删除成功'
        })
    except Exception as e:
        conn.rollback()
        return jsonify({
            'success': False,
            'message': f'删除失败：{str(e)}'
        }), 500
    finally:
        conn.close()

@bp.route('/tasks/template/<int:template_id>/toggle-status', methods=['PUT'])
def toggle_task_status(template_id):
    """切换任务模板的激活状态"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    data = request.json
    is_active = data.get('is_active', False)
    
    parent_id = session['user_id']
    
    conn = get_db_connection()
    try:
        # 验证任务模板是否存在且属于当前家长（未删除的）
        template = conn.execute('''
            SELECT id FROM task_templates WHERE id = ? AND parent_id = ? AND is_deleted = 0
        ''', (template_id, parent_id)).fetchone()
        
        if not template:
            return jsonify({'success': False, 'message': '任务模板不存在或不属于您'}), 404
        
        # 更新状态
        conn.execute('''
            UPDATE task_templates SET is_active = ? WHERE id = ?
        ''', (1 if is_active else 0, template_id))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': '状态已更新'
        })
    except Exception as e:
        conn.rollback()
        return jsonify({
            'success': False,
            'message': f'更新失败：{str(e)}'
        }), 500
    finally:
        conn.close()

@bp.route('/tasks/today', methods=['GET'])
def get_today_tasks():
    """获取今日任务列表"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    conn = get_db_connection()
    child = conn.execute('''
        SELECT c.* FROM children c 
        JOIN users u ON c.user_id = u.id 
        WHERE u.id = ?
    ''', (session['user_id'],)).fetchone()
    
    if not child:
        return jsonify({'success': False, 'message': '未找到儿童信息'}), 404
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 获取或创建今日任务
    templates = conn.execute('''
        SELECT * FROM task_templates 
        WHERE child_id = ? AND is_active = 1
    ''', (child['id'],)).fetchall()
    
    tasks = []
    for template in templates:
        # 检查今日任务是否已存在
        daily_task = conn.execute('''
            SELECT * FROM daily_tasks 
            WHERE template_id = ? AND task_date = ?
        ''', (template['id'], today)).fetchone()
        
        if not daily_task:
            # 创建新任务
            conn.execute('''
                INSERT INTO daily_tasks (template_id, child_id, task_date)
                VALUES (?, ?, ?)
            ''', (template['id'], child['id'], today))
            conn.commit()
            
            daily_task = conn.execute('''
                SELECT * FROM daily_tasks 
                WHERE template_id = ? AND task_date = ?
            ''', (template['id'], today)).fetchone()
        
        tasks.append({
            **dict(daily_task),
            'task_name': template['name'],
            'description': template['description'],
            'star_reward': template['star_reward'],
            'task_type': template['task_type']
        })
    
    conn.close()
    
    return jsonify({'success': True, 'data': tasks})

@bp.route('/tasks/complete', methods=['POST'])
def complete_task():
    """完成任务打卡"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    data = request.json
    task_id = data.get('task_id')
    
    conn = get_db_connection()
    child = conn.execute('''
        SELECT c.* FROM children c 
        JOIN users u ON c.user_id = u.id 
        WHERE u.id = ?
    ''', (session['user_id'],)).fetchone()
    
    if not child:
        conn.close()
        return jsonify({'success': False, 'message': '未找到儿童信息'}), 404
    
    # 更新任务状态
    task = conn.execute('''
        SELECT dt.*, tt.star_reward 
        FROM daily_tasks dt
        JOIN task_templates tt ON dt.template_id = tt.id
        WHERE dt.id = ? AND dt.child_id = ?
    ''', (task_id, child['id'])).fetchone()
    
    if not task:
        conn.close()
        return jsonify({'success': False, 'message': '任务不存在'}), 404
    
    if task['status'] == 'completed':
        conn.close()
        return jsonify({'success': False, 'message': '任务已完成'}), 400
    
    # 更新任务状态
    now = datetime.now()
    conn.execute('''
        UPDATE daily_tasks 
        SET status = 'completed', completed_at = ?, stars_earned = ?
        WHERE id = ?
    ''', (now, task['star_reward'], task_id))
    
    # 增加星星积分
    conn.execute('''
        UPDATE children 
        SET total_stars = total_stars + ?
        WHERE id = ?
    ''', (task['star_reward'], child['id']))
    
    # 记录星星获取
    conn.execute('''
        INSERT INTO star_records (child_id, amount, type, source, description)
        VALUES (?, ?, 'earn', 'task', ?)
    ''', (child['id'], task['star_reward'], f"完成任务：{task['task_name']}"))
    
    # 更新统计
    today_str = now.strftime('%Y-%m-%d')
    stat = conn.execute('''
        SELECT * FROM statistics 
        WHERE child_id = ? AND stat_date = ?
    ''', (child['id'], today_str)).fetchone()
    
    if stat:
        conn.execute('''
            UPDATE statistics 
            SET tasks_completed = tasks_completed + 1, stars_earned = stars_earned + ?
            WHERE id = ?
        ''', (task['star_reward'], stat['id']))
    else:
        conn.execute('''
            INSERT INTO statistics (child_id, stat_date, tasks_completed, stars_earned)
            VALUES (?, ?, 1, ?)
        ''', (child['id'], today_str, task['star_reward']))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': '任务完成！获得{}颗星星'.format(task['star_reward']),
        'data': {
            'stars_earned': task['star_reward'],
            'new_total_stars': child['total_stars'] + task['star_reward']
        }
    })

# ==================== 宠物互动 ====================

@bp.route('/pet/interact', methods=['POST'])
def pet_interact():
    """与宠物互动"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    data = request.json
    interaction_type = data.get('type')  # feed, clean, play, sleep
    pet_id = data.get('pet_id')
    
    # 互动配置
    config = {
        'feed': {'cost': 10, 'stat': 'hunger', 'value': 30},
        'clean': {'cost': 15, 'stat': 'cleanliness', 'value': 30},
        'play': {'cost': 20, 'stat': 'mood', 'value': 30},
        'sleep': {'cost': 8, 'stat': 'hunger', 'value': -10}  # 睡觉会减少饱腹度
    }
    
    if interaction_type not in config:
        return jsonify({'success': False, 'message': '无效的互动类型'}), 400
    
    conn = get_db_connection()
    child = conn.execute('''
        SELECT c.* FROM children c 
        JOIN users u ON c.user_id = u.id 
        WHERE u.id = ?
    ''', (session['user_id'],)).fetchone()
    
    if not child:
        conn.close()
        return jsonify({'success': False, 'message': '未找到儿童信息'}), 404
    
    pet = conn.execute('''
        SELECT * FROM pets 
        WHERE id = ? AND child_id = ? AND is_active = 1
    ''', (pet_id, child['id'])).fetchone()
    
    if not pet:
        conn.close()
        return jsonify({'success': False, 'message': '宠物不存在'}), 404
    
    # 检查星星是否足够
    interact_config = config[interaction_type]
    if child['total_stars'] < interact_config['cost']:
        conn.close()
        return jsonify({'success': False, 'message': '星星不足'}), 400
    
    # 更新宠物状态
    new_value = min(100, max(0, pet[interact_config['stat']] + interact_config['value']))
    conn.execute(f'''
        UPDATE pets 
        SET {interact_config['stat']} = ?, last_feed = ?
        WHERE id = ?
    ''', (new_value, datetime.now(), pet_id))
    
    # 扣除星星
    conn.execute('''
        UPDATE children 
        SET total_stars = total_stars - ?
        WHERE id = ?
    ''', (interact_config['cost'], child['id']))
    
    # 记录消费
    conn.execute('''
        INSERT INTO star_records (child_id, amount, type, source, description)
        VALUES (?, ?, 'spend', 'pet_interaction', ?)
    ''', (child['id'], interact_config['cost'], f"宠物互动：{interaction_type}"))
    
    # 记录互动
    conn.execute('''
        INSERT INTO pet_interactions (pet_id, child_id, interaction_type, stars_cost, effect_value)
        VALUES (?, ?, ?, ?, ?)
    ''', (pet_id, child['id'], interaction_type, interact_config['cost'], interact_config['value']))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': '互动成功！',
        'data': {
            'new_value': new_value,
            'stars_cost': interact_config['cost'],
            'new_total_stars': child['total_stars'] - interact_config['cost']
        }
    })

# ==================== 商城相关 ====================

@bp.route('/shop/items', methods=['GET'])
def get_shop_items():
    """获取商城物品列表"""
    conn = get_db_connection()
    items = conn.execute('''
        SELECT * FROM shop_items 
        WHERE is_active = 1 
        ORDER BY category, price_stars
    ''').fetchall()
    conn.close()
    
    return jsonify({'success': True, 'data': [dict(item) for item in items]})

@bp.route('/shop/purchase', methods=['POST'])
def purchase_item():
    """购买物品"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    data = request.json
    item_id = data.get('item_id')
    quantity = data.get('quantity', 1)
    
    conn = get_db_connection()
    child = conn.execute('''
        SELECT c.* FROM children c 
        JOIN users u ON c.user_id = u.id 
        WHERE u.id = ?
    ''', (session['user_id'],)).fetchone()
    
    if not child:
        conn.close()
        return jsonify({'success': False, 'message': '未找到儿童信息'}), 404
    
    item = conn.execute('''
        SELECT * FROM shop_items 
        WHERE id = ? AND is_active = 1
    ''', (item_id,)).fetchone()
    
    if not item:
        conn.close()
        return jsonify({'success': False, 'message': '商品不存在'}), 404
    
    total_price = item['price_stars'] * quantity
    
    # 检查星星是否足够
    if child['total_stars'] < total_price:
        conn.close()
        return jsonify({'success': False, 'message': '星星不足'}), 400
    
    # 扣除星星
    conn.execute('''
        UPDATE children 
        SET total_stars = total_stars - ?
        WHERE id = ?
    ''', (total_price, child['id']))
    
    # 记录消费
    conn.execute('''
        INSERT INTO star_records (child_id, amount, type, source, description)
        VALUES (?, ?, 'spend', 'shop', ?)
    ''', (child['id'], total_price, f"购买商品：{item['name']}"))
    
    # 创建购买记录
    conn.execute('''
        INSERT INTO purchase_records (child_id, item_id, quantity, total_price)
        VALUES (?, ?, ?, ?)
    ''', (child['id'], item_id, quantity, total_price))
    
    # 如果是消耗品，直接增加宠物属性
    if item['category'] in ['food', 'cleaning', 'mood']:
        pet = conn.execute('''
            SELECT * FROM pets 
            WHERE child_id = ? AND is_active = 1 
            ORDER BY created_at DESC LIMIT 1
        ''', (child['id'],)).fetchone()
        
        if pet:
            stat_map = {
                'food': 'hunger',
                'cleaning': 'cleanliness',
                'mood': 'mood'
            }
            stat_name = stat_map[item['category']]
            new_value = min(100, pet[stat_name] + item['effect_value'])
            
            conn.execute(f'''
                UPDATE pets 
                SET {stat_name} = ?
                WHERE id = ?
            ''', (new_value, pet['id']))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': '购买成功！',
        'data': {
            'total_price': total_price,
            'new_total_stars': child['total_stars'] - total_price
        }
    })

# ==================== 愿望单相关 ====================

@bp.route('/wishlists', methods=['GET'])
def get_wishlists():
    """获取愿望单列表"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    conn = get_db_connection()
    child = conn.execute('''
        SELECT c.* FROM children c 
        JOIN users u ON c.user_id = u.id 
        WHERE u.id = ?
    ''', (session['user_id'],)).fetchone()
    
    if not child:
        conn.close()
        return jsonify({'success': False, 'message': '未找到儿童信息'}), 404
    
    wishlists = conn.execute('''
        SELECT * FROM wishlists 
        WHERE child_id = ? 
        ORDER BY is_completed, created_at DESC
    ''', (child['id'],)).fetchall()
    
    conn.close()
    
    return jsonify({'success': True, 'data': [dict(w) for w in wishlists]})

@bp.route('/wishlists/update-progress', methods=['POST'])
def update_wishlist_progress():
    """更新愿望单进度"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    data = request.json
    wishlist_id = data.get('wishlist_id')
    progress = data.get('progress', 0)
    
    conn = get_db_connection()
    child = conn.execute('''
        SELECT c.* FROM children c 
        JOIN users u ON c.user_id = u.id 
        WHERE u.id = ?
    ''', (session['user_id'],)).fetchone()
    
    if not child:
        conn.close()
        return jsonify({'success': False, 'message': '未找到儿童信息'}), 404
    
    wishlist = conn.execute('''
        SELECT * FROM wishlists 
        WHERE id = ? AND child_id = ?
    ''', (wishlist_id, child['id'])).fetchone()
    
    if not wishlist:
        conn.close()
        return jsonify({'success': False, 'message': '愿望不存在'}), 404
    
    if wishlist['is_completed']:
        conn.close()
        return jsonify({'success': False, 'message': '愿望已完成'}), 400
    
    # 更新进度
    conn.execute('''
        UPDATE wishlists 
        SET current_progress = ?
        WHERE id = ?
    ''', (progress, wishlist_id))
    
    # 检查是否完成
    if progress >= wishlist['target_stars']:
        conn.execute('''
            UPDATE wishlists 
            SET is_completed = 1, completed_at = ?
            WHERE id = ?
        ''', (datetime.now(), wishlist_id))
        
        # 奖励星星
        conn.execute('''
            UPDATE children 
            SET total_stars = total_stars + ?
            WHERE id = ?
        ''', (wishlist['target_stars'], child['id']))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': '进度更新成功'})
