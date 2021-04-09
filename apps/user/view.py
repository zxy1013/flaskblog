import os
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from apps.article.models import Article_type, Article
from apps.user.util.test_up_down import upload_qiniu, delete_qiniu
from apps.user.util.util import user_type
from settings import Config
from apps.user.models import *
from exts import db
from apps.user.util.message_send import send_sms


user_bp = Blueprint('user', __name__)

# /login set_cookie  / 获取cookie  /logout delete_cookie()

# 自定义过滤器
@user_bp.app_template_filter('cdecode')
def content_decode(content):
    content = content.decode('utf-8')
    return content[:200]

# 首页
@user_bp.route('/')
def index():
    # # cookie获取方式
    # uid = request.cookies.get('uid', None)

    # session的获取,session底层默认获取
    # 接收页码数
    page = int(request.args.get('page', 1))
    # 判断是否存在检索词汇
    search = request.args.get('search', '')
    # paginate分页 page表示第几页 per_page表示每页几个
    if search:
        # 进行检索contains
        pagination = Article.query.filter(Article.title.contains(search)).order_by(-Article.pdatetime).paginate(
            page=page, per_page=3)
    else:
        # 获取文章列表   7 6 5  |  4 3 2 | 1
        pagination = Article.query.order_by(-Article.pdatetime).paginate(page=page, per_page=3)

    user, types = user_type( )
    params = {
        'user': user,
        'types': types,
        'pagination': pagination,
        'search': search
    }
    # print(pagination.items)  # [<Article 1>, <Article 2>, <Article 3>]
    # print(pagination.page)  # 当前的页码数 1
    # print(pagination.prev_num)  # 当前页的前一个页码数 None
    # print(pagination.next_num)  # 当前页的后一页的页码数 2
    # print(pagination.has_next)  # True
    # print(pagination.has_prev)  # False
    # print(pagination.pages)  # 总共有几页 2
    # print(pagination.total)  # 总的记录条数 5
    # 判断用户是否登录
    return render_template('user/index.html', **params)

# 注册
@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        repassword = request.form.get('repassword')
        phone = request.form.get('phone')
        email = request.form.get('email')
        if password == repassword:
            # 注册用户
            user = User()
            user.username = username
            # 使用自带的函数实现加密：generate_password_hash 94 char
            # print(generate_password_hash(password))
            user.password = generate_password_hash(password)
            user.phone = phone
            user.email = email
            # 添加并提交
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("user.index"))
        else:
            return render_template('user/register.html',msg='两次密码不一致')
    return render_template('user/register.html')

# 手机号码验证
@user_bp.route('/checkphone', methods=['GET', 'POST'])
def check_phone():
    phone = request.args.get('phone')
    user = User.query.filter(User.phone == phone).all()
    # print(user)
    # code: 400 不能用 200 可以用
    if len(user) > 0:
        return jsonify(code=400, msg='此号码已被注册')
    else:
        return jsonify(code=200, msg='此号码可用')

# 用户登录
@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        f = request.args.get('f')
        if f == '1':  # 用户名或者密码
            username = request.form.get('username')
            password = request.form.get('password')
            users = User.query.filter(User.username == username).all()
            for user in users:
                # 如果flag = True表示匹配，否则密码不匹配
                flag = check_password_hash(user.password, password)
                if flag:
                    # # cookie实现机制
                    # response = redirect(url_for('user.index'))
                    # # 最长保存多久，登录多久后失效 key，value
                    # response.set_cookie('uid', str(user.id), max_age=1800)
                    # return response

                    # session机制,session当成字典使用
                    session[ 'uid' ] = user.id
                    return redirect(url_for('user.index'))
            else:
                return render_template('user/login.html', msg='用户名或者密码有误')
        elif f == '2':  # 手机号码与验证码
            mobile = request.form.get('phone')
            code = request.form.get('code')
            # 先验证验证码
            valid_code = session.get(mobile)
            # print(valid_code)
            if code == valid_code:
                # 查询数据库
                user = User.query.filter(User.phone == mobile).first( )
                if user:
                    # 登录成功
                    session[ 'uid' ] = user.id
                    return redirect(url_for('user.index'))
                else:
                    return render_template('user/login.html', msg='此号码未注册')
            else:
                return render_template('user/login.html', msg='验证码有误！')
    return render_template('user/login.html')


# 发送短信息
# https://user.ihuyi.com/new/sms/overview
@user_bp.route('/sendMsg')
def send_message():
    mobile = request.args.get('phone')
    import random
    r = str(int(random.random()*10000//1))
    text = "您的验证码是：%s。请不要把验证码泄露给其他人。"%r
    ret = send_sms(text, mobile)
    ret = eval(ret.decode('utf-8'))
    print(ret)
    if ret is not None:
        if ret[ "code" ] == 2:
            session[ mobile ] = str(r)
            return jsonify(code=2,msg='短信发送成功')
        else:
            return jsonify(code=0,msg='提交失败')
    # return jsonify(code=200, msg='短信发送成功')

# 用户退出
@user_bp.route('/logout')
def logout():
    # # 删除cookie，通过response对象的delete_cookie(key),key就是要删除的cookie的key
    # response = redirect(url_for('user.index'))
    # response.delete_cookie('uid')
    # return response

    # 删除session
    # del session['uid'] # 删除session中的这个键值对
    session.clear() # 删除session的内存空间和cookie 客户端和服务器都删除 (推荐使用)
    return redirect(url_for('user.index'))


# 钩子函数
# 要求登录的路由
required_login_list = ['/center', '/change','/publish','/upload_photo','/photo_del','/add_comment']

# # 只在第一次请求中执行
# @user_bp.before_app_first_request
# def first_request():
#     print('before_app_first_request')

# 在所有请求中执行
@user_bp.before_app_request
def before_request1():
    print('before_request1before_request1', request.path)
    if request.path in required_login_list:
        id = session.get('uid') # 验证用户登录
        if not id:
            return render_template('user/login.html')
        else:
            user = User.query.get(id)
            # g对象，本次请求的对象，flask.g中，往其中放一个user属性
            g.user = user

# # 处理完请求后 执行after_app_request 如果需要给response加cookie就可以用这个
# @user_bp.after_app_request
# def after_request_test(response):
#     response.set_cookie('a', 'bbbb', max_age=19)
#     print('after_request_test')
#     return response

# # 在after_app_request后执行
# @user_bp.teardown_app_request
# def teardown_request_test(response):
#     print('teardown_request_test')
#     return response

# 用户中心
@user_bp.route('/center')
def user_center(): # 取登陆后的g.user
    types = Article_type.query.all( )
    photo = Photo.query.filter(Photo.user_id == g.user.id).all()
    # print(photo)
    return render_template('user/center.html', user=g.user, types=types,photos = photo)

# 图片的扩展名
ALLOWED_EXTENSIONS = ['jpg', 'png', 'gif', 'bmp']
# 用户信息修改
# 照片存在本地
@user_bp.route('/change', methods=['GET', 'POST'])
def user_change():
    if request.method == 'POST':
        username = request.form.get('username')
        phone = request.form.get('phone')
        email = request.form.get('email')
        # 只要有文件，获取方式必须使用request.files.get(name) filename为文件名字 save为保存路径
        icon = request.files.get('icon')
        icon_name = icon.filename
        suffix = icon_name.rsplit('.')[ -1 ]
        if suffix in ALLOWED_EXTENSIONS:
            icon_name = secure_filename(icon_name)  # 保证文件名是符合python的命名规则
            file_path = os.path.join(Config.UPLOAD_ICON_DIR, icon_name)
            icon.save(file_path) # 绝对路径 保存在此目录下
            # 保存成功
            user = g.user
            user.username = username
            user.phone = phone
            user.email = email
            # 相对路径
            user.icon = 'upload/icon/'+icon_name
            db.session.commit( )
            return redirect(url_for('user.user_center'))
        else:
            return render_template('user/center.html', user=g.user, msg='必须是扩展名是：jpg,png,gif,bmp格式')
    return render_template('user/center.html', user=g.user)


# 上传照片到七牛云
@user_bp.route('/upload_photo', methods=['GET', 'POST'])
def upload_photo():
    # 获取上传的内容
    photo = request.files.get('photo')  # FileStorage
    # photo.filename,photo.save(path)
    # 工具模块中封装方法
    ret, info = upload_qiniu(photo)
    if info.status_code == 200:
        photo = Photo()
        photo.photo_name = ret['key']
        photo.user_id = g.user.id
        db.session.add(photo)
        db.session.commit()
        return '上传成功！'
    else:
        return '上传失败！'


# 删除相册图片
@user_bp.route('/photo_del')
def photo_del():
    pid = request.args.get('pid')
    photo = Photo.query.get(pid)
    filename = photo.photo_name
    # 封装好的一个删除七牛存储文件的函数
    info = delete_qiniu(filename)
    # 判断状态码
    if info.status_code == 200:
        # 删除数据库的内容
        db.session.delete(photo)
        db.session.commit()
        return redirect(url_for('user.user_center'))
    else:
        return ('删除相册图片失败！')



# 我的相册
@user_bp.route('/myphoto')
def myphoto():
    # 查询所有的照片内容
    page = int(request.args.get('page', 1))
    # 获取登录用户信息
    user_id = session.get('uid',None)
    types = Article_type.query.all( )
    user = User.query.get(user_id)
    # if user_id:
    #     user = User.query.get(user_id)
    #     photos = Photo.query.filter(Photo.user_id == user.id).paginate(page=page, per_page=3)
    # else:
    #     photos = Photo.query.paginate(page=page, per_page=3)
    photos = Photo.query.paginate(page=page, per_page=3)
    return render_template('user/myphoto.html', photos=photos, user=user,types=types)


# 留言板
@user_bp.route('/board', methods=['GET', 'POST'])
def show_board():
    # 获取登录用户信息
    uid = session.get('uid', None)
    # 查询所有的留言内容
    page = int(request.args.get('page', 1))
    types = Article_type.query.all( )
    # 判断请求方式
    if request.method == 'POST':
        content = request.form.get('board')
        # 添加留言
        msg_board = MessageBoard()
        msg_board.content = content
        if uid:
            msg_board.user_id = uid
        db.session.add(msg_board)
        db.session.commit()
        return redirect(url_for('user.show_board'))

    # id = session.get('uid')  # 验证用户登录
    # if not id:
    #     boards = MessageBoard.query.order_by(-MessageBoard.mdatetime).paginate(page=page, per_page=5)
    #     return render_template('user/board.html', boards=boards,types=types)
    # else:
    #     user = User.query.get(id)
    #     boards = MessageBoard.query.filter(MessageBoard.user_id == user.id).paginate(page=page, per_page=5)
    #     # g对象，本次请求的对象，flask.g中，往其中放一个user属性
    #     return render_template('user/board.html', user=user,boards=boards,types=types)
    user = User.query.get(uid)
    boards = MessageBoard.query.order_by(-MessageBoard.mdatetime).paginate(page=page, per_page=5)
    return render_template('user/board.html', boards=boards,types=types,user=user)


# 留言删除
@user_bp.route('/board_del')
def delete_board():
    bid = request.args.get('bid')
    if bid:
        msgboard = MessageBoard.query.get(bid)
        db.session.delete(msgboard)
        db.session.commit()
        return redirect(url_for('user.user_center'))

