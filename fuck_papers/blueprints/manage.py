from flask import render_template, flash, redirect, url_for, Blueprint
from flask_login import login_user, logout_user, login_required, current_user

from fuck_papers.forms import LoginForm, RegisterForm
from fuck_papers.models import User
from fuck_papers.utils import redirect_back
from fuck_papers.extensions import db

manage_bp = Blueprint('manage', __name__)


@manage_bp.route('/new_paper')
def new_paper():
    pass


@manage_bp.route('/edit_paper')
def edit_paper():
    pass


@manage_bp.route('/papers')
def manage_paper():
    pass


@manage_bp.route('/new_category')
def new_category():
    pass


@manage_bp.route('/edit_category')
def edit_category():
    pass


@manage_bp.route('/categories')
def manage_category():
    pass


@manage_bp.route('/change_theme')
def change_theme(theme):
    pass
