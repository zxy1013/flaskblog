from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache

# database
db = SQLAlchemy()
# 配置模板
bootstrap = Bootstrap()
# 配置缓存
cache = Cache()