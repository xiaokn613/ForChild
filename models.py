#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库模型定义
包含：用户、宠物、任务、积分、商城、徽章、奖杯等表
"""

import sqlite3
from datetime import datetime, timedelta
import os

DATABASE = 'forchild.db'

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # 让结果可以通过列名访问
    return conn

def init_db():
    """初始化数据库，创建所有表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 1. 用户表（包含儿童和家长）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT CHECK(role IN ('child', 'parent')) NOT NULL,
                avatar TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # 2. 儿童详细信息表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS children (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                parent_id INTEGER,
                nickname TEXT NOT NULL,
                birthday DATE,
                avatar TEXT,
                total_stars INTEGER DEFAULT 0,
                total_badges INTEGER DEFAULT 0,
                total_trophies INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (parent_id) REFERENCES users(id) ON DELETE SET NULL
            )
        ''')
        
        # 3. 宠物表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                child_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                gender TEXT CHECK(gender IN ('male', 'female')) NOT NULL,
                color TEXT DEFAULT '',
                level INTEGER DEFAULT 1,
                exp INTEGER DEFAULT 0,
                hunger INTEGER DEFAULT 80,
                cleanliness INTEGER DEFAULT 80,
                mood INTEGER DEFAULT 80,
                status TEXT DEFAULT 'normal',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_feed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE
            )
        ''')
        
        # 4. 任务模板表（家长设定的任务）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_id INTEGER NOT NULL,
                child_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                task_type TEXT CHECK(task_type IN ('daily', 'pet', 'custom', 'reinforce', 'special')) NOT NULL,
                star_reward INTEGER DEFAULT 0,
                badge_reward INTEGER DEFAULT 0,
                trophy_reward INTEGER DEFAULT 0,
                schedule_time TIME,
                schedule_time_start TIME,
                schedule_time_end TIME,
                repeat_days TEXT,
                is_active BOOLEAN DEFAULT 1,
                is_deleted BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE
            )
        ''')
        
        # 为 task_templates 表创建索引以优化查询性能
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_templates_parent_id ON task_templates(parent_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_templates_child_id ON task_templates(child_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_templates_task_type ON task_templates(task_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_templates_is_deleted ON task_templates(is_deleted)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_templates_created_at ON task_templates(created_at)')
        
        # 5. 每日任务实例表（实际打卡的任务）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER NOT NULL,
                child_id INTEGER NOT NULL,
                task_date DATE NOT NULL,
                status TEXT CHECK(status IN ('pending', 'completed', 'expired')) DEFAULT 'pending',
                completed_at TIMESTAMP,
                stars_earned INTEGER DEFAULT 0,
                note TEXT,
                FOREIGN KEY (template_id) REFERENCES task_templates(id) ON DELETE CASCADE,
                FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
                UNIQUE(template_id, task_date)
            )
        ''')
        
        # 6. 星星积分记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS star_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                child_id INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                type TEXT CHECK(type IN ('earn', 'spend')) NOT NULL,
                source TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE
            )
        ''')
        
        # 7. 商城物品表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shop_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT NOT NULL,  -- 使用字典管理的类别（如：shop_category_1）
                price_stars INTEGER DEFAULT 0,
                real_price DECIMAL(10,2) DEFAULT 0,
                image TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 8. 购买记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchase_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                child_id INTEGER NOT NULL,
                item_id INTEGER NOT NULL,
                quantity INTEGER DEFAULT 1,
                total_price INTEGER NOT NULL,
                status TEXT CHECK(status IN ('pending', 'delivered')) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                delivered_at TIMESTAMP,
                FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
                FOREIGN KEY (item_id) REFERENCES shop_items(id) ON DELETE CASCADE
            )
        ''')
        
        # 9. 徽章表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS badges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                icon TEXT,
                requirement TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 10. 儿童获得徽章记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS child_badges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                child_id INTEGER NOT NULL,
                badge_id INTEGER NOT NULL,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
                FOREIGN KEY (badge_id) REFERENCES badges(id) ON DELETE CASCADE,
                UNIQUE(child_id, badge_id)
            )
        ''')
        
        # 11. 奖杯表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trophies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                icon TEXT,
                requirement TEXT,
                star_bonus INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 12. 儿童获得奖杯记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS child_trophies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                child_id INTEGER NOT NULL,
                trophy_id INTEGER NOT NULL,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                stars_awarded INTEGER DEFAULT 0,
                FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
                FOREIGN KEY (trophy_id) REFERENCES trophies(id) ON DELETE CASCADE,
                UNIQUE(child_id, trophy_id)
            )
        ''')
        
        # 13. 愿望单表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wishlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                child_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                type TEXT CHECK(type IN ('exchange', 'progress')) NOT NULL,
                target_stars INTEGER DEFAULT 0,
                current_progress INTEGER DEFAULT 0,
                description TEXT,
                is_completed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE
            )
        ''')
        
        # 14. 宠物互动记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pet_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id INTEGER NOT NULL,
                child_id INTEGER NOT NULL,
                interaction_type TEXT CHECK(interaction_type IN ('feed', 'clean', 'play', 'sleep')) NOT NULL,
                stars_cost INTEGER DEFAULT 0,
                effect_value INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE,
                FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE
            )
        ''')
        
        # 15. 统计数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                child_id INTEGER NOT NULL,
                stat_date DATE NOT NULL,
                tasks_completed INTEGER DEFAULT 0,
                stars_earned INTEGER DEFAULT 0,
                pet_status_avg INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
                UNIQUE(child_id, stat_date)
            )
        ''')
        
        # 16. 字典表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dictionaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dict_type TEXT NOT NULL,           -- 字典类型（如：shop_category）
                dict_value TEXT NOT NULL,          -- 字典值显示名称（如：食品）
                dict_key TEXT NOT NULL,            -- 字典键（自动生成，如：shop_category_1）
                sort_order INTEGER DEFAULT 0,      -- 排序
                is_active BOOLEAN DEFAULT 1,       -- 状态
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                remark TEXT,                       -- 备注
                UNIQUE(dict_type, dict_key)
            )
        ''')
        
        # 为 dictionaries 表创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_dictionaries_dict_type ON dictionaries(dict_type)')
        
        # 插入默认数据 - 示例用户
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            # 默认家长账号
            cursor.execute('''
                INSERT INTO users (username, password, role) 
                VALUES ('parent', '123456', 'parent')
            ''')
            
            # 默认儿童账号
            cursor.execute('''
                INSERT INTO users (username, password, role) 
                VALUES ('child', '123456', 'child')
            ''')
            
            # 获取刚插入的儿童用户 ID
            cursor.execute("SELECT id FROM users WHERE username='child'")
            child_user_id = cursor.fetchone()[0]
            
            # 插入儿童详细信息
            cursor.execute('''
                INSERT INTO children (user_id, nickname, total_stars) 
                VALUES (?, '小明', 100)
            ''', (child_user_id,))
            
            # 插入默认宠物
            cursor.execute('''
                INSERT INTO pets (child_id, name, type, gender, color) 
                VALUES (1, '哈士奇', 'dog', 'male', 'gray')
            ''')
            
            # 插入默认任务模板
            cursor.execute("SELECT id FROM users WHERE username='parent'")
            parent_id = cursor.fetchone()[0]
            
            # 分别插入每个任务模板
            task_templates = [
                ('早起打卡', '每天早上 8 点前起床', 'daily', 10, None),
                ('按时吃早餐', '早上 8:30 前吃完早餐', 'daily', 15, '08:30:00'),
                ('准时上学', '不迟到', 'daily', 20, '09:00:00'),
                ('完成作业', '按时完成当天作业', 'daily', 30, '20:00:00'),
                ('给宠物喂食', '照顾你的宠物', 'pet', 10, None),
                ('给宠物洗澡', '保持宠物清洁', 'pet', 15, None)
            ]
            
            for template in task_templates:
                cursor.execute('''
                    INSERT INTO task_templates (parent_id, child_id, name, description, task_type, star_reward, schedule_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (parent_id, child_user_id, template[0], template[1], template[2], template[3], template[4]))
            
            # 插入默认商城物品
            cursor.execute('''
                INSERT INTO shop_items (name, description, category, price_stars, real_price)
                VALUES 
                ('宠物粮食', '增加宠物饱腹度 30 点', 'shop_category_1', 10, 9.9),
                ('高级零食', '增加宠物饱腹度 50 点', 'shop_category_1', 20, 19.9),
                ('清洁泡泡', '增加宠物清洁度 30 点', 'shop_category_2', 15, 12.9),
                ('深度清洁', '增加宠物清洁度 60 点', 'shop_category_2', 30, 25.9),
                ('开心果', '增加宠物心情 30 点', 'shop_category_3', 20, 15.9),
                ('游乐园门票', '增加宠物心情 60 点', 'shop_category_3', 40, 35.9),
                ('小窝', '宠物休息用品', 'shop_category_4', 100, 89.9),
                ('玩具球', '宠物玩具', 'shop_category_4', 50, 45.9)
            ''')
            
            # 插入默认徽章
            cursor.execute('''
                INSERT INTO badges (name, description, icon, requirement)
                VALUES 
                ('早起小鸟', '连续 7 天早起打卡', '🐦', '连续 7 天早起'),
                ('卫生小卫士', '连续 10 天保持清洁', '✨', '连续 10 天清洁任务'),
                ('学习达人', '完成 30 次作业', '📚', '完成 30 次作业任务'),
                ('爱心天使', '照顾宠物 50 次', '❤️', '宠物互动 50 次')
            ''')
            
            # 插入默认奖杯
            cursor.execute('''
                INSERT INTO trophies (name, description, icon, requirement, star_bonus)
                VALUES 
                ('完美一周', '连续 7 天完成所有日常任务', '🏆', '7 天全满贯', 100),
                ('月度之星', '一个月内获得 1000 星星', '⭐', '月获 1000 星', 200),
                ('宠物大师', '将宠物培养到满级', '👑', '宠物满级', 500)
            ''')
            
            # 插入默认字典数据 - 商品类别
            cursor.execute('''
                INSERT INTO dictionaries (dict_type, dict_value, dict_key, sort_order, remark)
                VALUES 
                ('shop_category', '食品', 'shop_category_1', 1, '商品类型 - 食品'),
                ('shop_category', '清洁', 'shop_category_2', 2, '商品类型 - 清洁'),
                ('shop_category', '心情', 'shop_category_3', 3, '商品类型 - 心情'),
                ('shop_category', '装饰', 'shop_category_4', 4, '商品类型 - 装饰'),
                ('shop_category', '实物', 'shop_category_5', 5, '商品类型 - 实物')
            ''')
        
        conn.commit()
        print("✅ 数据库初始化成功！")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 数据库初始化失败：{e}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()
