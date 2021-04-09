from exts import db

# 多对多：商品和用户 此时需要创建一个新的表 第三张表描述其之间的关系
class Goods(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    gname = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    # 反向查找  Goods.users
    # user.goodslist
    # secondary表示去user_goods表中找外键关系(多对多表)
    users = db.relationship('User', backref='goodslist', secondary='user_goods')
    def __str__(self):
        return self.gname

# 关系表：user与goods之间的关系，使用外键表示
class User_goods(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    goods_id = db.Column(db.Integer, db.ForeignKey('goods.id'))
    number = db.Column(db.Integer, default=1)
