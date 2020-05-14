import os

import click
from flask import Flask, render_template
from flask_wtf.csrf import CSRFError

from fuck_papers.extensions import bootstrap, db, login_manager, csrf, ckeditor, mail, moment, toolbar, migrate
from fuck_papers.settings import config
from fuck_papers.blueprints.auth import auth_bp
from fuck_papers.blueprints.blog import blog_bp
from fuck_papers.models import User, Post


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

    return app


def register_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    ckeditor.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    toolbar.init_app(app)
    migrate.init_app(app, db)


def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(blog_bp, url_prefix='/blog')


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_processor():
        return dict(db=db, User=User, Post=Post)


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
    @click.option('--post', default=50, help='Quantity of posts, default is 50')
    @click.option('--user', default=10, help='Quantity of users, default is 10')
    def forge(post, user):
        """Generate fake data."""
        from fuck_papers.fakes import fake_posts
        from fuck_papers.fakes import fake_users

        db.drop_all()
        db.create_all()

        click.echo('Generating %d posts...' % post)
        fake_posts(post)
        click.echo('Generating %d users...' % user)
        fake_users(user)

        click.echo('Done.')
