"""
本地化所有前端资源
将 CDN 资源复制到 static 目录
"""
import os
import shutil
import urllib.request

def copy_npm_packages():
    """从 node_modules 复制 npm 包到 static 目录"""
    
    # 确保 static 目录存在
    if not os.path.exists('static'):
        os.makedirs('static')
        print("✓ 创建 static 目录")
    
    # 定义需要复制的文件
    files_to_copy = [
        # jQuery
        ('node_modules/jquery/dist/jquery.min.js', 'static/jquery.min.js'),
        ('node_modules/jquery/dist/jquery.min.map', 'static/jquery.min.map'),
        
        # Bootstrap JS
        ('node_modules/bootstrap/dist/js/bootstrap.bundle.min.js', 'static/bootstrap.bundle.min.js'),
        ('node_modules/bootstrap/dist/js/bootstrap.bundle.min.js.map', 'static/bootstrap.bundle.min.js.map'),
        
        # Bootstrap CSS
        ('node_modules/bootstrap/dist/css/bootstrap.min.css', 'static/bootstrap.min.css'),
        ('node_modules/bootstrap/dist/css/bootstrap.min.css.map', 'static/bootstrap.min.css.map'),
        
        # ECharts
        ('node_modules/echarts/dist/echarts.common.min.js', 'static/echarts.min.js'),
        ('node_modules/echarts/dist/echarts.common.min.js.map', 'static/echarts.min.js.map'),
    ]
    
    print("\n开始复制 npm 包...")
    for src, dst in files_to_copy:
        try:
            if os.path.exists(src):
                shutil.copy2(src, dst)
                print(f"✓ {src} → {dst}")
            else:
                print(f"✗ {src} 不存在")
        except Exception as e:
            print(f"✗ 复制失败 {src}: {e}")

def download_layer():
    """下载 Layer.js 和 Font Awesome 字体"""
    
    print("\n下载 Layer.js...")
    layer_url = 'https://cdn.bootcdn.net/ajax/libs/layer/3.5.1/layer.js'
    layer_path = 'static/layer.js'
    
    try:
        if os.path.exists(layer_path):
            print(f"✓ Layer.js 已存在")
        else:
            urllib.request.urlretrieve(layer_url, layer_path)
            print(f"✓ Layer.js 下载成功")
    except Exception as e:
        print(f"✗ Layer.js 下载失败：{e}")
    
    # 下载 Layer CSS
    print("\n下载 Layer CSS...")
    layer_css_url = 'https://cdn.bootcdn.net/ajax/libs/layer/3.5.1/theme/default/layer.css'
    layer_css_path = 'static/layer.css'
    
    try:
        if os.path.exists(layer_css_path):
            print(f"✓ Layer.css 已存在")
        else:
            urllib.request.urlretrieve(layer_css_url, layer_css_path)
            print(f"✓ Layer.css 下载成功")
    except Exception as e:
        print(f"✗ Layer.css 下载失败：{e}")
    
    # 下载 Font Awesome 字体
    print("\n下载 Font Awesome 字体...")
    webfonts_dir = 'static/webfonts'
    if not os.path.exists(webfonts_dir):
        os.makedirs(webfonts_dir)
        print(f"✓ 创建 webfonts 目录")
    
    font_files = [
        'fa-solid-900.woff2',
        'fa-solid-900.ttf',
        'fa-regular-400.woff2',
        'fa-regular-400.ttf',
        'fa-brands-400.woff2',
        'fa-brands-400.ttf',
    ]
    
    for font_file in font_files:
        font_url = f'https://cdn.bootcdn.net/ajax/libs/font-awesome/6.4.0/webfonts/{font_file}'
        font_path = os.path.join(webfonts_dir, font_file)
        
        try:
            if os.path.exists(font_path):
                print(f"  ✓ {font_file} 已存在")
            else:
                urllib.request.urlretrieve(font_url, font_path)
                print(f"  ✓ {font_file} 下载成功")
        except Exception as e:
            print(f"  ✗ {font_file} 下载失败：{e}")

if __name__ == '__main__':
    print("=" * 60)
    print("📦 本地化前端资源")
    print("=" * 60)
    
    copy_npm_packages()
    download_layer()
    
    print("\n" + "=" * 60)
    print("✅ 所有资源本地化完成！")
    print("=" * 60)
    
    # 显示 static 目录内容
    if os.path.exists('static'):
        print("\n📁 static 目录文件:")
        for f in os.listdir('static'):
            size = os.path.getsize(os.path.join('static', f))
            print(f"   - {f} ({size:,} bytes)")
