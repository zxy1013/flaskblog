from flask import session
from apps.article.models import Article_type
from apps.user.models import User

def user_type():
    # 获取文章分类
    types = Article_type.query.all()
    # 登录用户
    user = None
    user_id = session.get('uid', None)
    if user_id:
        user = User.query.get(user_id)
    return user, types

