from datetime import datetime

from flask import render_template, flash, Blueprint, current_app, abort, make_response
from flask_login import current_user

from fuck_papers.models import Paper, Category
from fuck_papers.utils import redirect_back
from fuck_papers.extensions import db

paper_bp = Blueprint('paper', __name__)


@paper_bp.route('/category/<int:category_id>', defaults={'page': 1})
@paper_bp.route('/category/<int:category_id>/<int:page>')
def by_category(category_id, page):
    categories = Category.query.filter_by(user=current_user)
    category = categories.filter_by(id=category_id).first_or_404()

    per_page = current_app.config['FP_PAPER_PER_PAGE']
    pagination = Paper.query.filter_by(category=category).order_by(
        Paper.add_timestamp.desc()).paginate(page, per_page=per_page)
    papers = pagination.items
    return render_template('content/index.html', pagination=pagination, papers=papers, category_name=category.name)


@paper_bp.route('/index', defaults={'page': 1})
@paper_bp.route('/index/<int:page>', )
def index(page):
    per_page = current_app.config['FP_PAPER_PER_PAGE']
    pagination = Paper.query.filter_by(user=current_user).order_by(
        Paper.add_timestamp.desc()).paginate(page, per_page=per_page)
    papers = pagination.items
    return render_template('content/index.html', pagination=pagination, papers=papers, category_name='所有')


@paper_bp.route('/recently', defaults={'page': 1})
@paper_bp.route('/recently/<int:page>')
def recently(page):
    per_page = current_app.config['FP_PAPER_PER_PAGE']
    pagination = Paper.query.filter_by(user=current_user).order_by(
        Paper.last_read_timestamp.desc()).paginate(page, per_page=per_page)
    papers = pagination.items
    return render_template('content/index.html', pagination=pagination, papers=papers, category_name='最近阅读')


@paper_bp.route('/stared', defaults={'page': 1})
@paper_bp.route('/stared/<int:page>')
def stared(page):
    per_page = current_app.config['FP_PAPER_PER_PAGE']
    pagination = Paper.query.filter_by(user=current_user).filter_by(stared=True).order_by(
        Paper.add_timestamp.desc()).paginate(page, per_page=per_page)
    papers = pagination.items
    return render_template('content/index.html', pagination=pagination, papers=papers, category_name='收藏')


@paper_bp.route('/readed', defaults={'page': 1})
@paper_bp.route('/readed/<int:page>')
def readed(page):
    per_page = current_app.config['FP_PAPER_PER_PAGE']
    pagination = Paper.query.filter_by(user=current_user).filter_by(readed=True).order_by(
        Paper.add_timestamp.desc()).paginate(page, per_page=per_page)
    papers = pagination.items
    return render_template('content/index.html', pagination=pagination, papers=papers, category_name='已读')


@paper_bp.route('/commented', defaults={'page': 1})
@paper_bp.route('/commented/<int:page>')
def commented(page):
    per_page = current_app.config['FP_PAPER_PER_PAGE']
    pagination = Paper.query.filter_by(user=current_user).filter(Paper.commented != '').order_by(
        Paper.add_timestamp.desc()).paginate(page, per_page=per_page)
    papers = pagination.items
    return render_template('content/index.html', pagination=pagination, papers=papers, category_name='已评论')


@paper_bp.route('/paper/<int:paper_id>', methods=['GET', 'POST'])
def show_paper(paper_id):
    paper = Paper.query.filter_by(user=current_user).filter_by(id=paper_id).first_or_404()
    paper.last_read_timestamp = datetime.utcnow()
    db.session.commit()
    return render_template('content/paper.html', paper=paper)


@paper_bp.route('/star/<int:paper_id>', methods=['POST'])
def star(paper_id):
    paper = Paper.query.filter_by(user=current_user).filter_by(id=paper_id).first_or_404()
    if paper.star is True:
        paper.star = False
        flash('取消收藏成功')
    else:
        paper.star = True
        flash('收藏成功')
    db.session.commit()
    return redirect_back()


@paper_bp.route('/change_theme<theme_name>')
def change_theme(theme_name):
    if theme_name not in current_app.config['FP_THEMES'].keys():
        abort(404)

    response = make_response(redirect_back())
    response.set_cookie('theme', theme_name, max_age=30 * 24 * 60 * 60)
    return response
