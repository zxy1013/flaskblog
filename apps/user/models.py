from datetime import datetime
from exts import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(95), nullable=False)
    phone = db.Column(db.String(11), unique=True, nullable=False)
    email = db.Column(db.String(30))
    icon = db.Column(db.String(100)) # 头像
    isdelete = db.Column(db.Boolean, default=False)
    rdatetime = db.Column(db.DateTime, default=datetime.now)
    # 在一对多关系中，多的那个表加外键，一的那个表加relationship 用于反向查询
    # 通过user.articles取user的文章
    # 通过article.user.*取user内容，user为backref的名字
    articles = db.relationship('Article', backref='user')
    def __str__(self):
        return self.username

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    photo_name = db.Column(db.String(50), nullable=False)
    photo_datetime = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __str__(self):
        return self.photo_name

class MessageBoard(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String(255), nullable=False)
    mdatetime = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # 关系：
    user = db.relationship('User', backref='messages')

