from flask import render_template, flash, redirect, url_for, Blueprint, current_app
from flask_login import login_user, logout_user, login_required, current_user

from fuck_papers.forms import LoginForm, RegisterForm
from fuck_papers.models import User, Paper, Category
from fuck_papers.utils import redirect_back
from fuck_papers.extensions import db

paper_bp = Blueprint('paper', __name__)


@paper_bp.route('/index', defaults={'page': 1})
@paper_bp.route('/index/<int:page>')
def index(page):
    categories = Category.query.filter_by(user=current_user)
    per_page = current_app.config['FP_PAPER_PER_PAGE']
    pagination = Paper.query.filter_by(user=current_user).paginate(page, per_page=per_page)
    papers = pagination.items
    total = pagination.total
    curr_category = None
    return render_template('content/index.html', pagination=pagination, papers=papers, total=total, curr_category=curr_category, categories=categories)


@paper_bp.route('/category/<int:category_id>/<int:page>', defaults={'page': 1})
def by_category(category_id, page):
    categories = Category.query.filter_by(user=current_user)
    curr_category = Category.query.get_or_404(category_id)
    per_page = current_app.config['FP_PAPER_PER_PAGE']
    pagination = Paper.query.filter_by(category=curr_category).ordey_by(Paper.add_timestamp.desc()).paginate(page, per_page=per_page)
    papers = pagination.items
    total = pagination.total
    return render_template('content/index.html', pagination=pagination, papers=papers, total=total, curr_category=curr_category, categories=categories)





@paper_bp.route('/about')
def about():
    return render_template('about.html')

