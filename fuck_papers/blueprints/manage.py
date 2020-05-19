from flask import render_template, flash, redirect, url_for, Blueprint
from flask_login import login_user, logout_user, login_required, current_user

from fuck_papers.forms import CommentForm, EditPaperForm, UrlForm
from fuck_papers.models import User, Paper, Category
from fuck_papers.utils import redirect_back
from fuck_papers.extensions import db

manage_bp = Blueprint('manage', __name__)


@manage_bp.route('/new_paper', methods=['GET', 'POST'])
def new_paper():
    form = UrlForm()
    if form.validate_on_submit():
        url = form.url.data
        ############################
        flash('正在采集', 'success')
        return redirect(url_for('paper.index'))
    return render_template('manage/new_paper.html', form=form)


@manage_bp.route('/edit_paper<int:paper_id>', methods=['GET', 'POST'])
def edit_paper(paper_id):
    paper = Paper.query.filter_by(user=current_user).filter_by(id=paper_id).first_or_404()
    form = EditPaperForm()
    if form.validate_on_submit():
        paper.url = form.url.data
        paper.title = form.title.data
        paper.author = form.author.data
        paper.abstract = form.abstract.data
        paper.subjects = form.subjects.data
        paper.submit_time = form.submit_time.data
        paper.category = Category.query.get(form.category.data)
        db.session.commit()
        flash('修改成功', 'success')
        return redirect(url_for('paper.show_paper', paper_id=paper.id))
    form.url.data = paper.url
    form.title.data = paper.title
    form.author.data = paper.author
    form.abstract.data = paper.abstract
    form.subjects.data = paper.subjects
    form.submit_time.data = paper.submit_time
    form.category.data = paper.category.id
    return render_template('manage/edit_paper.html', form=form, paper=paper)


@manage_bp.route('/add_comment/<int:paper_id>', methods=['GET', 'POST'])
def add_comment(paper_id):
    paper = Paper.query.filter_by(user=current_user).filter_by(id=paper_id).first_or_404()
    form = CommentForm()
    if form.validate_on_submit():
        commented = form.commented.data
        paper.commented = commented
        db.session.commit()
        flash('评注成功', 'success')
        return redirect(url_for('paper.show_paper', paper_id=paper.id))
    form.commented.data = paper.commented
    return render_template('manage/edit_comment.html', form=form, paper=paper)


@manage_bp.route('/edit_paper/<int:paper_id>', methods=['POST'])
def delete_paper(paper_id):
    paper = Paper.query.filter_by(user=current_user).filter_by(id=paper_id).first_or_404()
    db.session.delete(paper)
    db.session.commit()
    flash('删除成功', 'success')
    return redirect_back()


@manage_bp.route('/star_paper/<int:paper_id>', methods=['POST'])
def star_paper(paper_id):
    paper = Paper.query.filter_by(user=current_user).filter_by(id=paper_id).first_or_404()
    if paper.stared:
        paper.stared = False
        flash('取消收藏成功', 'success')
    else:
        paper.stared = True
        flash('收藏成功', 'success')
    db.session.commit()
    return redirect_back()


@manage_bp.route('/read_paper/<int:paper_id>', methods=['POST'])
def read_paper(paper_id):
    paper = Paper.query.filter_by(user=current_user).filter_by(id=paper_id).first_or_404()
    if paper.readed:
        paper.readed = False
        flash('成功从已读列表中删除', 'success')
    else:
        paper.readed = True
        flash('成功加入到已读列表', 'success')
    db.session.commit()
    return redirect_back()


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



