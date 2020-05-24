import os
import logging
from logging.handlers import RotatingFileHandler

import click
from flask import Flask, render_template, request
from flask_wtf.csrf import CSRFError
from flask_sqlalchemy import get_debug_queries
from flask_login import current_user, login_required

from fuck_papers.extensions import bootstrap, db, login_manager, csrf, moment, toolbar, migrate, cache, mail
from fuck_papers.settings import config
from fuck_papers.fakes import fake_users, fake_categories, fake_papers, fake_messages
from fuck_papers.models import User, Category, Paper, Message
from celery import Celery
from fuck_papers.celeryconfig import *


basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def register_logging(app):
    class RequestFormatter(logging.Formatter):

        def format(self, record):
            record.url = request.url
            record.remote_addr = request.remote_addr
            return super(RequestFormatter, self).format(record)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = RotatingFileHandler(os.path.join(basedir, 'logs/fuck_papers.logs'),
                                       maxBytes=10 * 1024 * 1024, backupCount=10)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    request_formatter = RequestFormatter(
        '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
        '%(levelname)s in %(module)s: %(message)s'
    )

    # mail_handler = SMTPHandler(
    #     mailhost=app.config['MAIL_SERVER'],
    #     fromaddr=app.config['MAIL_USERNAME'],
    #     toaddrs=['ADMIN_EMAIL'],
    #     subject='F-Papers Application Error',
    #     credentials=(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD']))
    # mail_handler.setLevel(logging.ERROR)
    # mail_handler.setFormatter(request_formatter)


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_processor():
        return dict(db=db, User=User, Category=Category, Paper=Paper)


def register_template_context(app):
    @app.context_processor
    def make_template_context():
        if current_user.is_authenticated:
            categories = Category.query.filter_by(user=current_user)
            all_papers = Paper.query.filter_by(user=current_user).all()
            stared_papers = Paper.query.filter_by(user=current_user).filter_by(stared=True).all()
            readed_papers = Paper.query.filter_by(user=current_user).filter_by(readed=True).all()
            commented_papers = Paper.query.filter_by(user=current_user).filter(Paper.commented != '').all()
            messages = Message.query.filter_by(user=current_user).all()
        else:
            categories = None
            all_papers = None
            stared_papers = None
            readed_papers = None
            commented_papers = None
            messages = None
        return dict(categories=categories, all_papers=all_papers, stared_papers=stared_papers,
                    readed_papers=readed_papers, commented_papers=commented_papers, messages=messages)


def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('errors/400.html', description=e.description), 400


def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop')
    def init(drop):
        """Initialize the database."""
        if drop:
            click.confirm('This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')

    @app.cli.command()
    @click.option('--user', default=5, help='Quantity of users, default is 10')
    @click.option('--category', default=50, help='Quantity of posts, default is 50')
    @click.option('--paper', default=400, help='Quantity of papers, default is 400')
    @click.option('--message', default=50, help='Quantity of messages, default is 50')
    @click.option('--username', default='default_user', help='Your username')
    @click.option('--password', default='123456', help='Your password')
    def forge(user, category, paper, message, username, password):
        """Generate fake data."""

        db.drop_all()
        db.create_all()

        click.echo('Generating %d users' % user)
        fake_users(username, password, user)

        click.echo('Generating %d categories' % category)
        fake_categories(category)

        click.echo('Generating %d papers' % paper)
        fake_papers(paper)

        click.echo('Generating %d messages' % message)
        fake_messages(message)

        click.echo('Done.')


def register_request_handlers(app):
    @app.after_request
    def query_profiler(response):
        for q in get_debug_queries():
            if q.duration >= app.config['FP_SLOW_QUERY_THRESHOLD']:
                app.logger.warning(
                    'Slow query: Duration: %fs\n Context: %s\nQuery: %s\n '
                    % (q.duration, q.context, q.statement)
                )
        return response


def register_celery(app):
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask


celery = Celery(include=['fuck_papers.spider'], broker=BROKER_URL)
celery.config_from_object('fuck_papers.celeryconfig')

config_name = os.getenv('FLASK_CONFIG', 'development')
flask_app = Flask('fuck_papers')
flask_app.config.from_object(config[config_name])

register_celery(flask_app)
db.init_app(flask_app)
bootstrap.init_app(flask_app)
login_manager.init_app(flask_app)
csrf.init_app(flask_app)
moment.init_app(flask_app)
migrate.init_app(flask_app, db)
cache.init_app(flask_app)
mail.init_app(flask_app)
# toolbar.init_app(flask_app)
# assets.init_app(flask_app)

register_errors(flask_app)
register_commands(flask_app)
register_shell_context(flask_app)
register_template_context(flask_app)
register_request_handlers(flask_app)
register_logging(flask_app)


@flask_app.route('/about')
# @cache.cached(timeout=10 * 60)
def about():
    cache.clear()
    return render_template('about.html')


from fuck_papers.blueprints.auth import auth_bp
from fuck_papers.blueprints.paper import paper_bp
from fuck_papers.blueprints.manage import manage_bp


# 先视图保护，再注册。
@paper_bp.before_request
@login_required
def login_protect():
    pass


@manage_bp.before_request
@login_required
def login_protect():
    pass


flask_app.register_blueprint(auth_bp, url_prefix='/auth')
flask_app.register_blueprint(manage_bp, url_prefix='/manage')
flask_app.register_blueprint(paper_bp)


