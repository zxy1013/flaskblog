from datetime import datetime
from exts import db

# 一对多 user和article
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    pdatetime = db.Column(db.DateTime, default=datetime.now)
    click_num = db.Column(db.Integer, default=0) # 点击量-阅读量
    save_num = db.Column(db.Integer, default=0) # 收藏
    love_num = db.Column(db.Integer, default=0) # 点赞
    # 外键 同步到数据库的外键关系 参照用户主键 通过article.user.*取user内容，
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # 通过自定义表名找
    type_id = db.Column(db.Integer, db.ForeignKey('type.id'), default=0)
    # 找评论
    comments = db.relationship('Comment', backref='article')


# 评论表，对user和article的评论
class Comment(db.Model):
    __tablename__ = 'comment' # 自定义表的名字
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    comment = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # 外键
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))
    cdatetime = db.Column(db.DateTime, default=datetime.now)
    user = db.relationship('User', backref='comment')
    def __str__(self):
        return self.comment

# 文章分类
class Article_type(db.Model):
    __tablename__ = 'type'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type_name = db.Column(db.String(20), nullable=False)
    # 找文章
    articles = db.relationship('Article', backref='articletype')