from flask import render_template, flash, redirect, url_for, Blueprint
from flask_login import login_user, logout_user, login_required, current_user

from fuck_papers.forms import LoginForm, RegisterForm
from fuck_papers.models import User, Category
from fuck_papers.utils import redirect_back
from fuck_papers.extensions import db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('paper.index'))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data

        user = User.query.filter_by(username=username).first()
        if user and user.validate_password(password):
            login_user(user, remember)
            flash('欢迎, %s!' % user.username, 'info')
            return redirect(url_for('paper.index'))
        else:
            flash('用户名或密码不正确', 'warning')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('请先登出用户', 'warning')
        return redirect_back()

    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        confirm_password = form.confirm_password.data

        user = User.query.filter_by(username=username).first()
        if not user and password == confirm_password:
            new_user = User(username=username, password_hash=password)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            initialize_user(new_user)
            flash('注册成功', 'info')
            return redirect(url_for('auth.login'))
        elif user:
            flash('该用户名已被注册', 'warning')
        elif password != confirm_password:
            flash('密码不一致，请重新输入', 'warning')
    return render_template('auth/register.html', form=form)


def initialize_user(new_user):
    default_category = Category(name='未分类', user=new_user)
    db.session.add(default_category)
    db.session.commit()


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('登出成功', 'info')
    return redirect(url_for('auth.login'))
