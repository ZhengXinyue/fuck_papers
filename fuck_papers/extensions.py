from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_debugtoolbar import DebugToolbarExtension
from flask_migrate import Migrate
from flask_caching import Cache
from flask_assets import Environment, Bundle
from flask_mail import Mail


bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
moment = Moment()
toolbar = DebugToolbarExtension()
migrate = Migrate()
cache = Cache()
assets = Environment()
mail = Mail()      # TODO: 实现邮箱注册登录


@login_manager.user_loader
def load_user(user_id):
    from fuck_papers.models import User
    user = User.query.get(int(user_id))
    return user


login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录'
login_manager.login_message_category = 'warning'


js = Bundle('js/bootstrap.bundle.js',
            'js/bootstrap.bundle.min.js',
            'js/bootstrap.js',
            'js/bootstrap.min.js',
            'js/jquery-3.2.1.slim.min.js',
            'js/moment-with-locales.min.js',
            'js/popper.min.js',
            filters='jsmin', output='gen/packed.js')

css = Bundle('css/black_swan.min.css',
             'css/bootstrap.css',
             'css/bootstrap.min.css',
             'css/bootstrap-grid.css',
             'css/bootstrap-grid.min.css',
             'css/bootstrap-reboot.css',
             'css/bootstrap-reboot.min.css',
             'css/perfect_blue.min.css',
             'css/style.css',
             filters='cssmin', output='gen/packed.css')

assets.register('js_all', js)
assets.register('css_all', css)
