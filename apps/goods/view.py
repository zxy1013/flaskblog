from flask import Blueprint, render_template, request
from apps.goods.models import Goods, User_goods
from apps.user.models import User
from exts import db

# url加前缀/goods
goods_bp = Blueprint('goods', __name__,url_prefix='/goods')

# (某用户买了哪些商品) 多对多
@goods_bp.route('/findgoods')
def find_goods():
    user_id = request.args.get('uid')
    user = User.query.get(user_id)
    return render_template('goods/findgoods.html', user=user)

# (某个商品哪些人买了) 多对多
@goods_bp.route('/finduser')
def find_user():
    goods_id = request.args.get('gid')
    goods = Goods.query.get(goods_id)
    return render_template('goods/finduser.html', goods=goods)

# 用户买商品页面
@goods_bp.route('/show')
def show():
    users = User.query.filter(User.isdelete == False).all()
    goods_list = Goods.query.all()
    return render_template('goods/show.html', users=users, goods_list=goods_list)

# 多对多表添加：向第三张表添加数据
@goods_bp.route('/buy')
def buy():
    uid = request.args.get('uid')
    gid = request.args.get('gid')
    ug = User_goods()
    ug.user_id = uid
    ug.goods_id = gid
    db.session.add(ug)
    db.session.commit()
    return '购买成功！'
