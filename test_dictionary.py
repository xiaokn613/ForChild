"""
测试字典管理功能
"""
import requests

BASE_URL = 'http://127.0.0.1:5000'

def login():
    """登录获取 session"""
    session = requests.Session()
    
    # 家长登录
    login_data = {
        'username': 'parent',
        'password': '123456'
    }
    response = session.post(f'{BASE_URL}/login', data=login_data, allow_redirects=False)
    
    if response.status_code in [200, 302]:
        print("✅ 登录成功")
        return session
    else:
        print(f"❌ 登录失败：{response.status_code}")
        return None

def test_get_dictionaries(session):
    """测试获取字典列表"""
    print("\n📋 测试：获取字典列表")
    
    # 获取所有字典
    response = session.get(f'{BASE_URL}/api/dictionaries')
    result = response.json()
    
    if result['success']:
        print(f"✅ 获取成功，共 {len(result['data'])} 条记录")
        for item in result['data']:
            print(f"   - {item['dict_type']}: {item['dict_value']} (排序：{item['sort_order']})")
    else:
        print(f"❌ 获取失败：{result['message']}")
    
    # 按字典类型过滤
    print("\n📋 测试：按字典类型过滤（shop_category）")
    response = session.get(f'{BASE_URL}/api/dictionaries?dict_type=shop_category')
    result = response.json()
    
    if result['success']:
        print(f"✅ 获取成功，共 {len(result['data'])} 条记录")
        for item in result['data']:
            print(f"   - {item['dict_value']} (排序：{item['sort_order']}, 备注：{item['remark'] or '无'})")
    else:
        print(f"❌ 获取失败：{result['message']}")

def test_add_dictionary(session):
    """测试新增字典项"""
    print("\n📋 测试：新增字典项")
    
    new_item = {
        'dict_type': 'task_type',
        'dict_value': 'study|学习任务',
        'sort_order': 1,
        'remark': '测试添加的任务类型',
        'is_active': True
    }
    
    response = session.post(
        f'{BASE_URL}/api/dictionaries/add',
        json=new_item,
        headers={'Content-Type': 'application/json'}
    )
    result = response.json()
    
    if result['success']:
        print(f"✅ 添加成功，ID: {result['data']['id']}")
        return result['data']['id']
    else:
        print(f"❌ 添加失败：{result['message']}")
        return None

def test_update_dictionary(session, item_id):
    """测试更新字典项"""
    print(f"\n📋 测试：更新字典项（ID: {item_id}）")
    
    update_data = {
        'dict_type': 'task_type',
        'dict_value': 'study|学习',
        'sort_order': 2,
        'is_active': True,
        'remark': '更新后的备注'
    }
    
    response = session.put(
        f'{BASE_URL}/api/dictionaries/{item_id}',
        json=update_data,
        headers={'Content-Type': 'application/json'}
    )
    result = response.json()
    
    if result['success']:
        print(f"✅ 更新成功")
    else:
        print(f"❌ 更新失败：{result['message']}")

def test_delete_dictionary(session, item_id):
    """测试删除字典项"""
    print(f"\n📋 测试：删除字典项（ID: {item_id}）")
    
    response = session.delete(f'{BASE_URL}/api/dictionaries/{item_id}')
    result = response.json()
    
    if result['success']:
        print(f"✅ 删除成功")
    else:
        print(f"❌ 删除失败：{result['message']}")

def main():
    print("=" * 60)
    print("🧪 字典管理功能测试")
    print("=" * 60)
    
    # 登录
    session = login()
    if not session:
        return
    
    # 测试获取字典
    test_get_dictionaries(session)
    
    # 测试新增
    new_id = test_add_dictionary(session)
    
    if new_id:
        # 测试更新
        test_update_dictionary(session, new_id)
        
        # 再次获取查看更新结果
        print("\n📋 验证更新结果:")
        response = session.get(f'{BASE_URL}/api/dictionaries?dict_type=task_type')
        result = response.json()
        if result['success'] and result['data']:
            item = result['data'][0]
            print(f"   - {item['dict_value']} (排序：{item['sort_order']}, 备注：{item['remark'] or '无'})")
        
        # 测试删除
        test_delete_dictionary(session, new_id)
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成！")
    print("=" * 60)

if __name__ == '__main__':
    main()
