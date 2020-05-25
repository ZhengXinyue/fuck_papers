from flask import render_template, flash, redirect, url_for, Blueprint, current_app
from flask_login import current_user

from fuck_papers.forms import CommentForm, EditPaperForm, UrlForm, NewCategoryForm, EditCategoryForm
from fuck_papers.models import Paper, Category, Message
from fuck_papers.utils import redirect_back
from fuck_papers.extensions import db
from fuck_papers.spider import create_and_notify


manage_bp = Blueprint('manage', __name__)


@manage_bp.route('/new_paper', methods=['GET', 'POST'])
def new_paper():
    form = UrlForm()
    if form.validate_on_submit():
        url = form.url.data
        category_id = form.category.data
        create_and_notify.delay(url, category_id, current_user.id)
        flash('正在解析，请稍后在通知栏中查看结果', 'info')
        return redirect_back()
    return render_template('manage/new_paper.html', form=form)


@manage_bp.route('/edit_paper/<int:paper_id>', methods=['GET', 'POST'])
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
        return redirect_back()
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
        return redirect_back()
    form.commented.data = paper.commented
    return render_template('manage/edit_comment.html', form=form, paper=paper)


@manage_bp.route('/delete_paper/<int:paper_id>', methods=['POST'])
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


@manage_bp.route('/papers', defaults={'page': 1})
@manage_bp.route('/papers/<int:page>')
def manage_paper(page):
    per_page = current_app.config['FP_MANAGE_PAPER_PER_PAGE']
    pagination = Paper.query.filter_by(user=current_user).order_by(
        Paper.add_timestamp.desc()).paginate(page, per_page=per_page)
    papers = pagination.items
    return render_template('manage/manage_paper.html', pagination=pagination, papers=papers, page=page)


@manage_bp.route('/new_category', methods=['GET', 'POST'])
def new_category():
    form = NewCategoryForm()
    if form.validate_on_submit():
        category = Category(
            name=form.new_category_name.data,
            user=current_user)
        db.session.add(category)
        db.session.commit()
        flash('创建成功', 'success')
        return redirect_back()
    return render_template('manage/new_category.html', form=form)


@manage_bp.route('/edit_category/<int:category_id>', methods=['GET', 'POST'])
def edit_category(category_id):
    own_category = Category.query.filter_by(user=current_user)
    target_category = own_category.filter_by(id=category_id).first_or_404()
    default_category = own_category.first()
    if default_category.id == target_category.id:
        flash('无法编辑默认分类', 'warning')
        return redirect(url_for('paper.index'))
    form = EditCategoryForm()
    if form.validate_on_submit():
        target_category.name = form.new_category_name.data
        db.session.commit()
        flash('修改成功', 'success')
        return redirect(url_for('manage.manage_category'))
    form.new_category_name.data = target_category.name
    return render_template('manage/edit_category.html', form=form, category=target_category)


@manage_bp.route('/categories', defaults={'page': 1})
@manage_bp.route('/categories/<int:page>')
def manage_category(page):
    default_category = Category.query.filter_by(user=current_user).first()
    per_page = current_app.config['FP_MANAGE_CATEGORY_PER_PAGE']
    pagination = Category.query.filter_by(user=current_user).paginate(page, per_page=per_page)
    categories = pagination.items
    return render_template('manage/manage_category.html', pagination=pagination, categories=categories,
                           page=page, default_category=default_category)


@manage_bp.route('/delete_category/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    own_category = Category.query.filter_by(user=current_user)
    target_category = own_category.filter_by(id=category_id).first_or_404()
    default_category = own_category.first()
    if default_category.id == target_category.id:
        flash('无法删除默认分类', 'warning')
        return redirect(url_for('paper.index'))
    target_category.delete()
    flash('删除成功', 'success')
    return redirect(url_for('manage.manage_category'))


@manage_bp.route('/delete_message/<int:message_id>', methods=['POST'])
def delete_message(message_id):
    message = Message.query.filter_by(user=current_user).filter_by(id=message_id).first_or_404()
    db.session.delete(message)
    db.session.commit()
    flash('删除成功', 'success')
    return redirect_back()
