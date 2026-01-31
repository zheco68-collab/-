# 校园墙管理系统项目文档

## 1. 项目概述

校园墙管理系统是一个基于Web的社交平台，旨在为在校学生提供一个发布信息、交流互动的空间。系统支持用户发布帖子、上传图片、评论、点赞等功能，采用现代化的前端设计和稳定的后端架构。

### 1.1 核心功能

- 用户认证：登录、注册
- 帖子管理：发布、浏览、搜索
- 互动功能：点赞、评论
- 媒体功能：头像上传、帖子图片上传
- 内容审核：帖子状态管理

### 1.2 技术特色

- 现代化前端设计：Vue 3 + Tailwind CSS
- 响应式布局：适配不同设备屏幕
- 实时交互：无需页面刷新
- 安全可靠：文件上传验证、用户认证
- 高性能：优化的API设计和数据处理

## 2. 技术栈

### 2.1 前端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| HTML5 | - | 页面结构 |
| CSS3 | - | 样式设计 |
| JavaScript | ES6+ | 交互逻辑 |
| Vue 3 | 3.5.13 | 前端框架 |
| Tailwind CSS | 3.4.0 | 响应式样式 |
| Lucide | 0.563.0 | 图标库 |

### 2.2 后端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.13.5 | 后端开发 |
| Flask | 3.0.3 | Web框架 |
| pymysql | 1.1.0 | 数据库连接 |
| flask-cors | 4.0.1 | 跨域支持 |

### 2.3 数据库

| 技术 | 版本 | 用途 |
|------|------|------|
| MySQL | 8.0+ | 数据存储 |

## 3. 项目结构

```
xyq_01/
├── avatar/               # 用户头像存储目录
├── image/                # 帖子图片存储目录
├── app.py                # 后端主应用
├── index.html            # 前端主页面
├── register.html         # 注册页面
└── 项目文档.md           # 项目文档
```

### 3.1 文件说明

- **app.py**：Flask后端应用，包含所有API端点和业务逻辑
- **index.html**：校园墙主页面，实现帖子浏览、发布、评论等功能
- **register.html**：用户注册页面，实现新用户注册功能
- **avatar/**：存储用户上传的头像图片
- **image/**：存储用户发布帖子时上传的图片

## 4. 功能模块

### 4.1 用户认证模块

- **登录功能**：验证用户身份，生成会话状态
- **注册功能**：创建新用户账号，验证唯一性
- **头像管理**：上传、更新用户头像

### 4.2 帖子管理模块

- **发布帖子**：支持文本内容和图片上传
- **浏览帖子**：按时间顺序展示，支持分页
- **搜索帖子**：支持内容模糊查询
- **帖子状态**：待审核、已审核、已拒绝

### 4.3 互动功能模块

- **点赞功能**：支持点赞/取消点赞，防止重复点赞
- **评论功能**：支持对帖子发表评论，按时间顺序展示
- **举报功能**：支持用户举报违规内容

### 4.4 媒体管理模块

- **头像上传**：支持用户上传个人头像
- **图片上传**：支持发布帖子时上传多张图片
- **文件验证**：限制文件类型和大小

## 5. API接口

### 5.1 认证接口

| 接口 | 方法 | 功能 | 请求体 | 响应 |
|------|------|------|--------|------|
| `/api/login` | POST | 用户登录 | `{"username": "...", "password": "..."}` | `{"code": 200, "data": {"id": "...", "nickname": "...", "avatar": "..."}}` |
| `/api/register` | POST | 用户注册 | `{"username": "...", "password": "...", "confirmPassword": "...", "email": "..."}` | `{"code": 200, "message": "注册成功"}` |
| `/api/avatar/upload` | POST | 上传头像 | FormData: `avatar` (文件), `user_id` | `{"code": 200, "data": {"avatar_url": "..."}}` |

### 5.2 帖子接口

| 接口 | 方法 | 功能 | 请求体 | 响应 |
|------|------|------|--------|------|
| `/api/posts` | GET | 获取帖子列表 | 查询参数: `show_all`, `search` | `{"code": 200, "data": [{"id": "...", "content": "...", ...}]}` |
| `/api/posts` | POST | 发布帖子 | `{"user_id": "...", "content": "...", "image_urls": [], "anonymous": 0}` | `{"code": 200, "data": {"post_id": "..."}}` |
| `/api/posts/<id>` | GET | 获取帖子详情 | N/A | `{"code": 200, "data": {"id": "...", "content": "...", ...}}` |
| `/api/posts/images/upload` | POST | 上传帖子图片 | FormData: `images` (文件), `user_id` | `{"code": 200, "data": {"image_urls": [...]}}` |

### 5.3 互动接口

| 接口 | 方法 | 功能 | 请求体 | 响应 |
|------|------|------|--------|------|
| `/api/posts/<id>/like` | POST | 点赞/取消点赞 | `{"user_id": "..."}` | `{"code": 200, "data": {"like_count": 10, "liked": true}}` |
| `/api/posts/<id>/comments` | GET | 获取评论列表 | N/A | `{"code": 200, "data": [{"id": "...", "content": "...", ...}]}` |
| `/api/posts/<id>/comments` | POST | 发表评论 | `{"user_id": "...", "content": "...", "anonymous": 0}` | `{"code": 200, "data": {"id": "...", "content": "...", ...}}` |
| `/api/posts/<id>/report` | POST | 举报帖子 | `{"user_id": "...", "reason": "..."}` | `{"code": 200, "message": "已收到举报"}` |

## 6. 数据库设计

### 6.1 核心表结构

#### 6.1.1 系统用户表 (`sys_user`)

| 字段名 | 数据类型 | 约束 | 描述 |
|--------|----------|------|------|
| `id` | `BIGINT` | `PRIMARY KEY` | 用户ID |
| `username` | `VARCHAR(50)` | `UNIQUE NOT NULL` | 用户名（学号） |
| `password` | `VARCHAR(100)` | `NOT NULL` | 密码 |
| `nickname` | `VARCHAR(50)` | `NOT NULL` | 昵称 |
| `avatar` | `VARCHAR(255)` | | 头像URL |
| `email` | `VARCHAR(100)` | `UNIQUE NOT NULL` | 邮箱 |
| `role` | `INT` | `DEFAULT 0` | 角色（0:普通用户） |
| `status` | `INT` | `DEFAULT 1` | 状态（1:启用） |
| `created_at` | `DATETIME` | `DEFAULT CURRENT_TIMESTAMP` | 创建时间 |

#### 6.1.2 帖子表 (`wall_post`)

| 字段名 | 数据类型 | 约束 | 描述 |
|--------|----------|------|------|
| `id` | `BIGINT` | `PRIMARY KEY` | 帖子ID |
| `user_id` | `BIGINT` | `NOT NULL` | 发布用户ID |
| `content` | `TEXT` | `NOT NULL` | 帖子内容 |
| `image_urls` | `TEXT` | | 图片URL（逗号分隔） |
| `anonymous` | `TINYINT` | `DEFAULT 0` | 是否匿名（0:否） |
| `status` | `TINYINT` | `DEFAULT 0` | 状态（0:待审核, 1:已审核, 2:已拒绝） |
| `like_count` | `INT` | `DEFAULT 0` | 点赞数 |
| `comment_count` | `INT` | `DEFAULT 0` | 评论数 |
| `view_count` | `INT` | `DEFAULT 0` | 浏览数 |
| `created_time` | `DATETIME` | `DEFAULT CURRENT_TIMESTAMP` | 创建时间 |

#### 6.1.3 评论表 (`wall_comment`)

| 字段名 | 数据类型 | 约束 | 描述 |
|--------|----------|------|------|
| `id` | `BIGINT` | `PRIMARY KEY` | 评论ID |
| `post_id` | `BIGINT` | `NOT NULL` | 帖子ID |
| `user_id` | `BIGINT` | `NOT NULL` | 评论用户ID |
| `content` | `TEXT` | `NOT NULL` | 评论内容 |
| `anonymous` | `TINYINT` | `DEFAULT 0` | 是否匿名（0:否） |
| `status` | `TINYINT` | `DEFAULT 1` | 状态（1:正常） |
| `created_time` | `DATETIME` | `DEFAULT CURRENT_TIMESTAMP` | 创建时间 |

#### 6.1.4 点赞表 (`wall_like`)

| 字段名 | 数据类型 | 约束 | 描述 |
|--------|----------|------|------|
| `id` | `BIGINT` | `PRIMARY KEY` | 点赞ID |
| `post_id` | `BIGINT` | `NOT NULL` | 帖子ID |
| `user_id` | `BIGINT` | `NOT NULL` | 点赞用户ID |
| `created_time` | `DATETIME` | `DEFAULT CURRENT_TIMESTAMP` | 创建时间 |

#### 6.1.5 举报表 (`wall_report`)

| 字段名 | 数据类型 | 约束 | 描述 |
|--------|----------|------|------|
| `id` | `BIGINT` | `PRIMARY KEY` | 举报ID |
| `post_id` | `BIGINT` | `NOT NULL` | 帖子ID |
| `report_user_id` | `BIGINT` | `NOT NULL` | 举报用户ID |
| `reason` | `TEXT` | `NOT NULL` | 举报原因 |
| `created_time` | `DATETIME` | `DEFAULT CURRENT_TIMESTAMP` | 创建时间 |

## 7. 部署说明

### 7.1 环境要求

| 依赖 | 版本/要求 | 安装命令 |
|------|-----------|----------|
| Python | 3.8+ | 官网下载 |
| MySQL | 8.0+ | 官网下载 |
| pip | 最新版 | `python -m pip install --upgrade pip` |
| pymysql | 1.1.0+ | `pip install pymysql` |
| flask | 3.0.0+ | `pip install flask` |
| flask-cors | 4.0.0+ | `pip install flask-cors` |

### 7.2 数据库配置

1. **创建数据库**：
   ```sql
   CREATE DATABASE xyq CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

2. **创建表结构**：
   - 执行系统用户表、帖子表、评论表、点赞表、举报表的创建SQL

3. **配置用户权限**：
   ```sql
   CREATE USER 'root'@'%' IDENTIFIED BY '123456';
   GRANT ALL PRIVILEGES ON xyq.* TO 'root'@'%';
   FLUSH PRIVILEGES;
   ```

### 7.3 项目配置

1. **修改数据库连接**：
   - 编辑 `app.py` 文件中的 `DB_CONFIG` 配置

2. **修改API地址**：
   - 编辑 `index.html` 和 `register.html` 中的 `API_BASE_URL` 配置

### 7.4 启动服务

#### 7.4.1 启动后端服务

```bash
# 在项目目录下执行
python app.py
# 服务将运行在 http://0.0.0.0:3002
```

#### 7.4.2 启动前端服务

```bash
# 在项目目录下执行
python -m http.server 3000 --bind 0.0.0.0
# 服务将运行在 http://0.0.0.0:3000
```

### 7.5 访问项目

- **主页**：http://localhost:3000
- **注册页面**：http://localhost:3000/register.html
- **后端API**：http://localhost:3002/api

## 8. 使用说明

### 8.1 用户注册

1. 访问注册页面：http://localhost:3000/register.html
2. 填写注册信息：学号、密码、确认密码、邮箱
3. 点击注册按钮
4. 注册成功后自动跳转到登录页面

### 8.2 用户登录

1. 访问主页：http://localhost:3000
2. 点击右上角的登录按钮
3. 输入用户名和密码
4. 点击登录按钮
5. 登录成功后即可使用全部功能

### 8.3 发布帖子

1. 确保已登录
2. 在主页顶部的输入框中输入帖子内容
3. 点击图片图标可上传图片（最多9张）
4. 可选择是否匿名发布
5. 点击"发射信号"按钮发布帖子

### 8.4 互动操作

- **点赞**：点击帖子下方的爱心图标
- **评论**：点击帖子下方的评论图标，在弹出的评论框中输入内容
- **举报**：点击帖子右上角的盾牌图标，填写举报原因

### 8.5 头像设置

1. 点击右上角的头像
2. 在弹出的头像设置弹窗中点击"选择图片"
3. 选择一张本地图片
4. 点击"保存头像"按钮

## 9. 常见问题

### 9.1 登录失败

- 检查用户名和密码是否正确
- 检查后端服务是否运行
- 检查网络连接是否正常

### 9.2 图片上传失败

- 检查图片大小是否超过2MB
- 检查图片格式是否为支持的格式（JPG、PNG等）
- 检查后端服务是否运行

### 9.3 帖子不显示

- 检查帖子是否处于待审核状态
- 检查后端服务是否运行
- 检查数据库连接是否正常

### 9.4 跨域错误

- 确保后端服务已启用CORS支持
- 检查API地址是否正确

## 10. 维护与扩展

### 10.1 日志管理

- 后端服务日志：控制台输出
- 前端错误：浏览器控制台

### 10.2 性能优化

- 图片压缩：上传前对图片进行压缩
- 缓存策略：合理使用浏览器缓存
- 数据库索引：为常用查询字段添加索引

### 10.3 功能扩展

- 消息通知：添加评论、点赞通知
- 分类标签：为帖子添加分类
- 热门帖子：基于点赞和评论数的热门算法
- 管理员后台：内容审核、用户管理

## 11. 安全注意事项

### 11.1 前端安全

- 输入验证：对用户输入进行严格验证
- XSS防护：防止跨站脚本攻击
- CSRF防护：防止跨站请求伪造

### 11.2 后端安全

- SQL注入防护：使用参数化查询
- 密码安全：使用加密存储
- 文件上传安全：严格验证文件类型和大小
- API访问控制：验证用户权限

### 11.3 服务器安全

- 防火墙配置：限制不必要的端口访问
- 定期备份：定期备份数据库和文件
- 系统更新：及时更新系统和依赖包

## 12. 总结

校园墙管理系统是一个功能完善、界面美观的Web应用，为在校学生提供了一个便捷的交流平台。系统采用现代化的技术栈，具有良好的扩展性和可维护性。通过本系统，学生可以方便地发布信息、交流互动，促进校园内的信息流通和社交活动。

### 12.1 项目亮点

- 现代化前端设计，用户体验良好
- 完整的功能模块，满足用户需求
- 安全可靠的后端架构
- 灵活的部署配置，适应不同环境
- 详细的项目文档，便于维护和扩展

