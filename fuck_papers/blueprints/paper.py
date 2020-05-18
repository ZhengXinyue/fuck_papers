from flask import render_template, flash, redirect, url_for, Blueprint, current_app
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import and_

from fuck_papers.forms import LoginForm, RegisterForm
from fuck_papers.models import User, Paper, Category
from fuck_papers.utils import redirect_back
from fuck_papers.extensions import db

paper_bp = Blueprint('paper', __name__)


@paper_bp.route('/index', defaults={'page': 1})
@paper_bp.route('/index/<int:page>', )
def index(page):
    categories = Category.query.filter_by(user=current_user)
    per_page = current_app.config['FP_PAPER_PER_PAGE']
    pagination = Paper.query.filter_by(user=current_user).order_by(
        Paper.add_timestamp.desc()).paginate(page, per_page=per_page)
    papers = pagination.items
    total = pagination.total
    return render_template('content/index.html', pagination=pagination, papers=papers, total=total,
                           curr_category=None, categories=categories)


@paper_bp.route('/category/<int:category_id>', defaults={'page': 1})
@paper_bp.route('/category/<int:category_id>/<int:page>')
def by_category(category_id, page):
    categories = Category.query.filter_by(user=current_user)
    curr_category = categories.filter_by(id=category_id).first_or_404()

    per_page = current_app.config['FP_PAPER_PER_PAGE']
    if curr_category.name == '最近阅读':
        pagination = Paper.query.filter_by(category=curr_category).order_by(
            Paper.last_read_timestamp.desc()).paginate(page, per_page=per_page)
    else:
        pagination = Paper.query.filter_by(category=curr_category).order_by(
            Paper.add_timestamp.desc()).paginate(page, per_page=per_page)
    papers = pagination.items
    total = pagination.total
    return render_template('content/index.html', pagination=pagination, papers=papers, total=total,
                           curr_category=curr_category, categories=categories)


@paper_bp.route('/paper/<int:paper_id>')
def show_paper(paper_id):
    return render_template('content/paper.html')


@paper_bp.route('/about')
def about():
    return render_template('content/about.html')
