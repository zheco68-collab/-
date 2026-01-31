from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import time
from datetime import datetime

app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'xyq'
}

# 数据库连接函数
def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

# API端点：获取帖子列表
@app.route('/api/posts', methods=['GET'])
def get_posts():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        # 获取查询参数
        show_all = request.args.get('show_all', 'false').lower() == 'true'
        search = request.args.get('search', '').strip()
        
        # 构建查询SQL
        where_conditions = []
        params = []
        
        if not show_all:
            where_conditions.append('p.status = 1')
        
        if search:
            where_conditions.append('p.content LIKE %s')
            params.append(f'%{search}%')
        
        # 构建完整SQL
        where_clause = 'WHERE ' + ' AND '.join(where_conditions) if where_conditions else ''
        
        cursor.execute(f'''
            SELECT p.*, u.nickname, u.avatar 
            FROM wall_post p 
            LEFT JOIN sys_user u ON p.user_id = u.id 
            {where_clause} 
            ORDER BY p.created_time DESC
        ''', params)
        posts = cursor.fetchall()
        
        # 处理帖子数据
        result = []
        for post in posts:
            # 处理图片URL
            image_urls = post['image_urls'].split(',') if post['image_urls'] else []
            image_urls = [url.strip() for url in image_urls if url.strip()]
            
            # 构建帖子数据
            post_data = {
                'id': post['id'],
                'user_id': post['user_id'],
                'nickname': post['nickname'] or '匿名同学',
                'avatar': post['avatar'] or 'https://api.dicebear.com/7.x/identicon/svg?seed=anon',
                'content': post['content'],
                'image_urls': image_urls,
                'anonymous': post['anonymous'],
                'status': post['status'],
                'like_count': post['like_count'],
                'comment_count': post['comment_count'],
                'view_count': post['view_count'],
                'created_time': post['created_time'].strftime('%Y-%m-%d %H:%M:%S')
            }
            result.append(post_data)
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'code': 200,
            'message': '获取帖子列表成功',
            'data': result
        })
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

# API端点：获取帖子详情
@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post_detail(post_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        # 查询帖子
        cursor.execute('''
            SELECT p.*, u.nickname, u.avatar 
            FROM wall_post p 
            LEFT JOIN sys_user u ON p.user_id = u.id 
            WHERE p.id = %s AND p.status = 1
        ''', (post_id,))
        post = cursor.fetchone()
        
        if not post:
            cursor.close()
            connection.close()
            return jsonify({'code': 404, 'message': '帖子不存在或已被删除'}), 404
        
        # 处理图片URL
        image_urls = post['image_urls'].split(',') if post['image_urls'] else []
        image_urls = [url.strip() for url in image_urls if url.strip()]
        
        # 构建帖子数据
        post_data = {
            'id': post['id'],
            'user_id': post['user_id'],
            'nickname': post['nickname'] or '匿名同学',
            'avatar': post['avatar'] or 'https://api.dicebear.com/7.x/identicon/svg?seed=anon',
            'content': post['content'],
            'image_urls': image_urls,
            'anonymous': post['anonymous'],
            'status': post['status'],
            'like_count': post['like_count'],
            'comment_count': post['comment_count'],
            'view_count': post['view_count'],
            'created_time': post['created_time'].strftime('%Y-%m-%d %H:%M:%S')
        }
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'code': 200,
            'message': '获取帖子详情成功',
            'data': post_data
        })
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

# API端点：获取帖子评论
@app.route('/api/posts/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        # 查询评论
        cursor.execute('''
            SELECT c.*, u.nickname, u.avatar 
            FROM wall_comment c 
            LEFT JOIN sys_user u ON c.user_id = u.id 
            WHERE c.post_id = %s AND c.status = 1 
            ORDER BY c.created_time ASC
        ''', (post_id,))
        comments = cursor.fetchall()
        
        # 处理评论数据
        result = []
        for comment in comments:
            comment_data = {
                'id': comment['id'],
                'post_id': comment['post_id'],
                'user_id': comment['user_id'],
                'nickname': comment['nickname'] or '匿名同学',
                'avatar': comment['avatar'] or 'https://api.dicebear.com/7.x/identicon/svg?seed=anon',
                'content': comment['content'],
                'anonymous': comment['anonymous'],
                'created_time': comment['created_time'].strftime('%Y-%m-%d %H:%M:%S')
            }
            result.append(comment_data)
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'code': 200,
            'message': '获取评论成功',
            'data': result
        })
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

# API端点：发表评论
@app.route('/api/posts/<int:post_id>/comments', methods=['POST'])
def add_comment(post_id):
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        content = data.get('content')
        anonymous = data.get('anonymous', 0)
        
        if not user_id or not content:
            return jsonify({'code': 400, 'message': '用户ID和评论内容不能为空'}), 400
        
        # 连接数据库
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 检查帖子是否存在
        cursor.execute('SELECT id FROM wall_post WHERE id = %s', (post_id,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({'code': 404, 'message': '帖子不存在'}), 404
        
        # 插入评论
        comment_id = int(time.time() * 1000)
        # 简化SQL语句，只插入必要的字段
        cursor.execute('''
            INSERT INTO wall_comment (id, post_id, user_id, content, anonymous, status, created_time)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        ''', (comment_id, post_id, user_id, content, anonymous, 1))
        
        # 更新帖子评论数
        cursor.execute('UPDATE wall_post SET comment_count = comment_count + 1 WHERE id = %s', (post_id,))
        
        # 获取用户信息
        cursor.execute('SELECT nickname, avatar FROM sys_user WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        nickname = user[0] if user else '匿名同学'
        avatar = user[1] if user else 'https://api.dicebear.com/7.x/identicon/svg?seed=anon'
        
        connection.commit()
        cursor.close()
        connection.close()
        
        # 构建评论数据
        comment_data = {
            'id': comment_id,
            'post_id': post_id,
            'user_id': user_id,
            'nickname': nickname,
            'avatar': avatar,
            'content': content,
            'anonymous': anonymous,
            'created_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return jsonify({
            'code': 200,
            'message': '评论发表成功',
            'data': comment_data
        })
        
    except Exception as e:
        # 打印详细错误信息到控制台
        print(f"发表评论错误: {str(e)}")
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

# API端点：更新帖子浏览量
@app.route('/api/posts/<int:post_id>/view', methods=['POST'])
def update_view_count(post_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 更新浏览量
        cursor.execute('UPDATE wall_post SET view_count = view_count + 1 WHERE id = %s', (post_id,))
        connection.commit()
        
        # 获取最新浏览量
        cursor.execute('SELECT view_count FROM wall_post WHERE id = %s', (post_id,))
        view_count = cursor.fetchone()[0]
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'code': 200,
            'message': '更新浏览量成功',
            'data': {'view_count': view_count}
        })
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

# API端点：举报帖子
@app.route('/api/posts/<int:post_id>/report', methods=['POST'])
def report_post(post_id):
    try:
        data = request.get_json()
        reason = data.get('reason')
        report_user_id = data.get('user_id')
        
        if not reason:
            return jsonify({'code': 400, 'message': '举报原因不能为空'}), 400
        
        if not report_user_id:
            return jsonify({'code': 400, 'message': '用户ID不能为空'}), 400
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 插入举报记录
        report_id = int(time.time() * 1000)
        cursor.execute('''
            INSERT INTO wall_report (id, post_id, report_user_id, reason)
            VALUES (%s, %s, %s, %s)
        ''', (report_id, post_id, report_user_id, reason))
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'code': 200,
            'message': '已收到举报，管理人员将尽快处理。'
        })
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

# API端点：用户登录
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'code': 400, 'message': '用户名和密码不能为空'}), 400
        
        # 连接数据库
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        # 查询用户
        cursor.execute('SELECT * FROM sys_user WHERE username = %s', (username,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            connection.close()
            return jsonify({'code': 401, 'message': '用户不存在'}), 401
        
        # 简单验证密码（实际项目中应该使用密码哈希）
        if user['password'] != password:
            cursor.close()
            connection.close()
            return jsonify({'code': 401, 'message': '密码错误'}), 401
        
        # 构建用户信息
        user_info = {
            'id': user['id'],
            'username': user['username'],
            'nickname': user['nickname'],
            'avatar': user['avatar'] or 'https://api.dicebear.com/7.x/avataaars/svg?seed=' + user['username']
        }
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'code': 200,
            'message': '登录成功',
            'data': user_info
        })
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

# API端点：用户注册
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')  # 学号
        password = data.get('password')
        confirm_password = data.get('confirmPassword')
        email = data.get('email')
        
        if not username or not password or not confirm_password or not email:
            return jsonify({'code': 400, 'message': '学号、密码、确认密码和邮箱不能为空'}), 400
        
        # 验证学号只能为数字
        if not username.isdigit():
            return jsonify({'code': 400, 'message': '学号只能包含数字'}), 400
        
        # 验证密码长度
        if len(password) < 6:
            return jsonify({'code': 400, 'message': '密码长度至少为6个字符'}), 400
        
        # 验证两次密码是否一致
        if password != confirm_password:
            return jsonify({'code': 400, 'message': '两次输入的密码不一致'}), 400
        
        # 连接数据库
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 验证学号是否已存在
        cursor.execute('SELECT id FROM sys_user WHERE username = %s', (username,))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({'code': 400, 'message': '该学号已注册'}), 400
        
        # 验证邮箱是否已存在
        cursor.execute('SELECT id FROM sys_user WHERE email = %s', (email,))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({'code': 400, 'message': '该邮箱已注册'}), 400
        
        # 生成用户ID
        user_id = int(time.time() * 1000)
        
        # 生成昵称（使用学号作为默认昵称）
        nickname = f'同学{username[-4:]}'
        
        # 生成头像
        avatar = 'https://api.dicebear.com/7.x/avataaars/svg?seed=' + username
        
        # 插入用户数据
        cursor.execute('''
            INSERT INTO sys_user (id, username, password, nickname, avatar, email, role, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (user_id, username, password, nickname, avatar, email, 0, 1))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({
            'code': 200,
            'message': '注册成功'
        })
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

# API端点：上传头像
@app.route('/api/avatar/upload', methods=['POST'])
def upload_avatar():
    try:
        import os
        from werkzeug.utils import secure_filename
        
        # 获取用户ID
        user_id = request.form.get('user_id')
        if not user_id:
            return jsonify({'code': 400, 'message': '用户ID不能为空'}), 400
        
        # 检查是否有文件上传
        if 'avatar' not in request.files:
            return jsonify({'code': 400, 'message': '请选择要上传的头像'}), 400
        
        file = request.files['avatar']
        if file.filename == '':
            return jsonify({'code': 400, 'message': '请选择要上传的头像'}), 400
        
        # 验证文件类型
        if not file.content_type.startswith('image/'):
            return jsonify({'code': 400, 'message': '请选择图片文件'}), 400
        
        # 验证文件大小
        if file.content_length > 2 * 1024 * 1024:  # 2MB
            return jsonify({'code': 400, 'message': '图片大小不能超过2MB'}), 400
        
        # 创建头像存储目录
        avatar_dir = os.path.join(os.path.dirname(__file__), 'avatar')
        if not os.path.exists(avatar_dir):
            os.makedirs(avatar_dir)
        
        # 生成文件名
        filename = f'{user_id}_{int(time.time())}_{secure_filename(file.filename)}'
        filepath = os.path.join(avatar_dir, filename)
        
        # 保存文件
        file.save(filepath)
        
        # 先获取并删除旧头像
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 获取用户当前头像
        cursor.execute('SELECT avatar FROM sys_user WHERE id = %s', (user_id,))
        old_avatar = cursor.fetchone()
        
        # 构建头像URL
        avatar_url = f'/avatar/{filename}'
        
        # 更新数据库
        cursor.execute('UPDATE sys_user SET avatar = %s WHERE id = %s', (avatar_url, user_id))
        connection.commit()
        
        cursor.close()
        connection.close()
        
        # 删除旧头像文件
        if old_avatar and old_avatar[0] and old_avatar[0].startswith('/avatar/'):
            old_filename = old_avatar[0].replace('/avatar/', '')
            old_filepath = os.path.join(avatar_dir, old_filename)
            if os.path.exists(old_filepath):
                try:
                    os.remove(old_filepath)
                    print(f'旧头像已删除: {old_filepath}')
                except Exception as e:
                    print(f'删除旧头像失败: {str(e)}')
        
        return jsonify({
            'code': 200,
            'message': '头像上传成功',
            'data': {
                'avatar_url': avatar_url
            }
        })
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

# API端点：提供头像文件服务
@app.route('/avatar/<path:filename>')
def serve_avatar(filename):
    import os
    from flask import send_from_directory
    
    avatar_dir = os.path.join(os.path.dirname(__file__), 'avatar')
    return send_from_directory(avatar_dir, filename)

# API端点：点赞/取消点赞帖子
@app.route('/api/posts/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'code': 400, 'message': '用户ID不能为空'}), 400
        
        # 连接数据库
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 检查帖子是否存在
        cursor.execute('SELECT id FROM wall_post WHERE id = %s', (post_id,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({'code': 404, 'message': '帖子不存在'}), 404
        
        # 检查用户是否已经点赞
        cursor.execute('SELECT id FROM wall_like WHERE post_id = %s AND user_id = %s', (post_id, user_id))
        existing_like = cursor.fetchone()
        
        if existing_like:
            # 已点赞，执行取消点赞
            cursor.execute('DELETE FROM wall_like WHERE id = %s', (existing_like[0],))
            # 更新帖子点赞数
            cursor.execute('UPDATE wall_post SET like_count = GREATEST(0, like_count - 1) WHERE id = %s', (post_id,))
            message = '取消点赞成功'
            liked = False
        else:
            # 未点赞，执行点赞
            like_id = int(time.time() * 1000)
            cursor.execute('INSERT INTO wall_like (id, post_id, user_id, created_time) VALUES (%s, %s, %s, %s)', 
                          (like_id, post_id, user_id, datetime.now()))
            # 更新帖子点赞数
            cursor.execute('UPDATE wall_post SET like_count = like_count + 1 WHERE id = %s', (post_id,))
            message = '点赞成功'
            liked = True
        
        # 获取最新点赞数
        cursor.execute('SELECT like_count FROM wall_post WHERE id = %s', (post_id,))
        like_count = cursor.fetchone()[0]
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({
            'code': 200,
            'message': message,
            'data': {'like_count': like_count, 'liked': liked}
        })
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

# API端点：获取用户点赞状态
@app.route('/api/posts/<int:post_id>/like/status', methods=['GET'])
def get_like_status(post_id):
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'code': 400, 'message': '用户ID不能为空'}), 400
        
        # 连接数据库
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 检查用户是否已经点赞
        cursor.execute('SELECT id FROM wall_like WHERE post_id = %s AND user_id = %s', (post_id, user_id))
        liked = cursor.fetchone() is not None
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'code': 200,
            'message': '获取点赞状态成功',
            'data': {'liked': liked}
        })
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

# API端点：获取多个帖子的点赞状态
@app.route('/api/posts/like/statuses', methods=['GET'])
def get_like_statuses():
    try:
        user_id = request.args.get('user_id')
        post_ids = request.args.get('post_ids', '').split(',')
        
        if not user_id or not post_ids:
            return jsonify({'code': 400, 'message': '用户ID和帖子ID不能为空'}), 400
        
        # 过滤空字符串
        post_ids = [id.strip() for id in post_ids if id.strip()]
        
        if not post_ids:
            return jsonify({'code': 400, 'message': '帖子ID不能为空'}), 400
        
        # 连接数据库
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 构建查询
        placeholders = ','.join(['%s'] * len(post_ids))
        query = f'SELECT post_id FROM wall_like WHERE user_id = %s AND post_id IN ({placeholders})'
        cursor.execute(query, [user_id] + post_ids)
        
        # 获取点赞的帖子ID
        liked_posts = [str(row[0]) for row in cursor.fetchall()]
        
        # 构建结果
        statuses = {}
        for post_id in post_ids:
            statuses[post_id] = post_id in liked_posts
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'code': 200,
            'message': '获取点赞状态成功',
            'data': statuses
        })
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

# API端点：上传帖子图片
@app.route('/api/posts/images/upload', methods=['POST'])
def upload_post_images():
    try:
        import os
        from werkzeug.utils import secure_filename
        
        # 获取用户ID
        user_id = request.form.get('user_id')
        if not user_id:
            return jsonify({'code': 400, 'message': '用户ID不能为空'}), 400
        
        # 检查是否有文件上传
        if 'images' not in request.files:
            return jsonify({'code': 400, 'message': '请选择要上传的图片'}), 400
        
        files = request.files.getlist('images')
        if not files or all(file.filename == '' for file in files):
            return jsonify({'code': 400, 'message': '请选择要上传的图片'}), 400
        
        # 创建图片存储目录
        image_dir = os.path.join(os.path.dirname(__file__), 'image')
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)
        
        # 处理上传的图片
        image_urls = []
        for file in files:
            if file.filename == '':
                continue
            
            # 验证文件类型
            if not file.content_type.startswith('image/'):
                continue
            
            # 验证文件大小
            if file.content_length > 2 * 1024 * 1024:  # 2MB
                continue
            
            # 生成文件名
            filename = f'{user_id}_{int(time.time())}_{secure_filename(file.filename)}'
            filepath = os.path.join(image_dir, filename)
            
            # 保存文件
            file.save(filepath)
            
            # 构建图片URL
            image_url = f'/image/{filename}'
            image_urls.append(image_url)
        
        if not image_urls:
            return jsonify({'code': 400, 'message': '请选择有效的图片文件'}), 400
        
        return jsonify({
            'code': 200,
            'message': '图片上传成功',
            'data': {
                'image_urls': image_urls
            }
        })
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

# API端点：发布帖子
@app.route('/api/posts', methods=['POST'])
def create_post():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        content = data.get('content')
        image_urls = data.get('image_urls', [])
        anonymous = data.get('anonymous', 0)
        
        if not user_id or not content:
            return jsonify({'code': 400, 'message': '用户ID和帖子内容不能为空'}), 400
        
        # 连接数据库
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 生成帖子ID
        post_id = int(time.time() * 1000)
        
        # 处理图片URL
        image_urls_str = ','.join(image_urls) if image_urls else ''
        
        # 插入帖子
        cursor.execute('''
            INSERT INTO wall_post (id, user_id, content, image_urls, anonymous, status, created_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (post_id, user_id, content, image_urls_str, anonymous, 0, datetime.now()))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({
            'code': 200,
            'message': '发布成功，等待审核',
            'data': {
                'post_id': post_id
            }
        })
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

# API端点：提供帖子图片文件服务
@app.route('/image/<path:filename>')
def serve_post_image(filename):
    import os
    from flask import send_from_directory
    
    image_dir = os.path.join(os.path.dirname(__file__), 'image')
    return send_from_directory(image_dir, filename)

# API端点：健康检查
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3002, debug=True)
