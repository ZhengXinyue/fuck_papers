import os

import click
from flask import Flask, render_template
from flask_wtf.csrf import CSRFError
from flask_sqlalchemy import get_debug_queries
from flask_login import current_user

from fuck_papers.extensions import bootstrap, db, login_manager, csrf, ckeditor, moment, toolbar, migrate, cache, assets
from fuck_papers.settings import config
from fuck_papers.blueprints.auth import auth_bp
from fuck_papers.blueprints.paper import paper_bp
from fuck_papers.blueprints.manage import manage_bp
from fuck_papers.fakes import fake_users, fake_categories, fake_papers

from fuck_papers.models import User, Category, Paper


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
    app = Flask('fuck_papers')
    app.config.from_object(config[config_name])

    register_extensions(app)
    register_blueprints(app)
    register_errors(app)
    register_commands(app)
    register_shell_context(app)

    @app.route('/')
    def home():
        return render_template('base.html')

    @app.route('/test')
    def test():
        return render_template('test.html')

    return app


def register_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    ckeditor.init_app(app)
    moment.init_app(app)
    toolbar.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    assets.init_app(app)


def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(manage_bp, url_prefix='/manage')
    app.register_blueprint(paper_bp)


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_processor():
        return dict(db=db, User=User, Category=Category, Paper=Paper)


# def register_template_context(app):
#     @app.context_processor
#     def make_template_context():
#         if current_user.is_authenticated:
#             categories = Category.query.filter_by(user=current_user)
#         else:
#             categories = None
#         return dict(categories=categories)


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
    @click.option('--user', default=10, help='Quantity of users, default is 10')
    @click.option('--category', default=50, help='Quantity of posts, default is 50')
    @click.option('--paper', default=400, help='Quantity of papers, default is 400')
    def forge(user, category, paper):
        """Generate fake data."""

        db.drop_all()
        db.create_all()

        click.echo('Generating %d users' % user)
        fake_users(user)

        click.echo('Generating %d categories' % category)
        fake_categories(category)

        click.echo('Generating %d papers' % paper)
        fake_papers(paper)

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