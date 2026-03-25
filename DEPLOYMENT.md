# 🚀 部署指南

## 项目结构

```
ForChild/
├── app.py                      # Flask 应用主入口
├── models.py                   # 数据库模型
├── requirements.txt            # Python 依赖
├── start.py                    # 一键启动脚本
├── start.sh                    # Mac/Linux 启动脚本
├── start.bat                   # Windows 启动脚本
├── README.md                   # 项目说明文档
├── routes/                     # 路由模块
│   ├── api_routes.py          # API 接口
│   ├── child_routes.py        # 儿童端路由
│   └── parent_routes.py       # 家长端路由
├── templates/                  # HTML 模板
│   ├── child/                 # 儿童端页面
│   │   ├── login.html
│   │   ├── home.html
│   │   ├── tasks.html
│   │   ├── pets.html
│   │   ├── shop.html
│   │   ├── badges.html
│   │   ├── trophies.html
│   │   └── wishlists.html
│   └── parent/                # 家长端页面
│       ├── login.html
│       ├── dashboard.html
│       ├── tasks.html
│       ├── shop.html
│       ├── pets.html
│       ├── statistics.html
│       └── wishlists.html
└── forchild.db                 # SQLite 数据库文件（运行时生成）
```

## 快速开始

### Mac / Linux 用户

1. 打开终端
2. 进入项目目录
3. 运行：
```bash
chmod +x start.sh
./start.sh
```

### Windows 用户

1. 双击 `start.bat` 文件
2. 或在命令行中运行：
```cmd
start.bat
```

### 使用 Python 直接启动

```bash
python start.py
```

## 访问地址

启动成功后，在浏览器中访问：

- **儿童端**: http://localhost:5001/child/login
- **家长端**: http://localhost:5001/parent/login

## 默认账号

**儿童端：**
- 用户名：`child`
- 密码：`123456`

**家长端：**
- 用户名：`parent`
- 密码：`123456`

## 跨平台部署说明

### Windows 部署

1. 确保已安装 Python 3.8+
2. 将项目文件夹复制到目标机器
3. 双击运行 `start.bat`
4. 首次运行会自动安装依赖并初始化数据库

### Mac 部署

1. 确保已安装 Python 3.8+
2. 将项目文件夹复制到目标机器
3. 终端运行 `./start.sh`
4. 首次运行会自动安装依赖并初始化数据库

### Linux 部署

同 Mac 部署步骤。

## 数据备份

所有数据存储在 `forchild.db` 文件中。

**备份方法：**
- 直接复制 `forchild.db` 文件到其他位置

**恢复方法：**
- 停止应用
- 将备份的 `forchild.db` 文件放回项目目录
- 重新启动应用

## 自定义配置

### 修改端口

编辑 `app.py` 文件，找到：
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```
修改 `port=5001` 为你需要的端口号。

### 修改默认账号

编辑 `models.py` 文件，找到 `init_db()` 函数中的默认用户插入语句：
```python
cursor.execute('''
    INSERT INTO users (username, password, role) 
    VALUES ('parent', '123456', 'parent')
''')
```
修改用户名和密码。

## 常见问题

### 端口被占用

如果看到 "Port 5001 is in use" 错误：
1. 修改 `app.py` 中的端口号
2. 或者关闭占用该端口的程序

### Python 版本过低

确保 Python 版本 >= 3.8：
```bash
python --version
```

### 依赖安装失败

尝试手动安装依赖：
```bash
pip install -r requirements.txt
```

### 数据库初始化失败

删除旧的数据库文件后重新启动：
```bash
rm forchild.db
python start.py
```

## 性能优化建议

1. **生产环境部署**：
   - 关闭 debug 模式：`debug=False`
   - 使用 Gunicorn 或 uWSGI 作为 WSGI 服务器
   - 使用 Nginx 作为反向代理

2. **数据库优化**：
   - 定期清理过期数据
   - 添加索引优化查询

3. **前端优化**：
   - 压缩静态资源
   - 启用浏览器缓存

## 安全建议

1. 修改默认账号密码
2. 不要将数据库文件放在公开可访问的位置
3. 如果在局域网使用，确保防火墙设置正确
4. 定期备份数据

## 技术支持

如遇到问题，请检查：
1. Python 版本是否符合要求
2. 依赖包是否正确安装
3. 端口是否被占用
4. 查看终端输出的错误信息

---

**祝使用愉快！** 🎉
