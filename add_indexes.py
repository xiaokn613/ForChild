"""
数据库性能优化脚本
为现有数据库添加索引以提升查询速度
"""
import sqlite3
import os

def get_db_connection():
    """获取数据库连接"""
    db_path = os.path.join(os.path.dirname(__file__), 'forchild.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def add_indexes():
    """为任务模板表添加索引"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("开始为 task_templates 表添加索引...")
    
    try:
        # 创建索引
        indexes = [
            ('idx_task_templates_parent_id', 'task_templates', 'parent_id'),
            ('idx_task_templates_child_id', 'task_templates', 'child_id'),
            ('idx_task_templates_task_type', 'task_templates', 'task_type'),
            ('idx_task_templates_is_deleted', 'task_templates', 'is_deleted'),
            ('idx_task_templates_created_at', 'task_templates', 'created_at'),
        ]
        
        for index_name, table_name, column_name in indexes:
            try:
                sql = f'CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column_name})'
                cursor.execute(sql)
                print(f"✓ 索引 {index_name} 创建成功")
            except Exception as e:
                print(f"✗ 索引 {index_name} 创建失败：{e}")
        
        conn.commit()
        print("\n所有索引创建完成！数据库性能已优化。")
        
    except Exception as e:
        conn.rollback()
        print(f"错误：{e}")
    finally:
        conn.close()

if __name__ == '__main__':
    add_indexes()
