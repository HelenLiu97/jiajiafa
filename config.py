from datetime import timedelta
from flask import Flask
from flask_cache import Cache


app = Flask(__name__)


cache = Cache(app, config={'CACHE_TYPE': 'redis',
                           'CACHE_REDIS_HOST': '127.0.0.1',
                           'CACHE_REDIS_PORT': 6379,
                           'CACHE_REDIS_DB': '',
                           'CACHE_REDIS_PASSWORD': ''}, with_jinja2_ext=False)

app.config['SECRET_KEY'] = 'NEWBENTO2020'

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=60*60*6)

app.app_context().push()

# 注册路由,以url_prefix区分功能(蓝图)

from admin import admin_blueprint

app.register_blueprint(admin_blueprint)
