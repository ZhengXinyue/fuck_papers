from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, SubmitField, SelectField, TextAreaField, ValidationError, HiddenField, \
    BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Optional, URL, EqualTo, NoneOf

from fuck_papers.models import Category


class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(6, 20, message='用户名长度必须在6-20之间')])
    password = PasswordField('密码', validators=[DataRequired(), Length(6, 128, message='密码长度必须在6-128之间')])
    remember = BooleanField('记住我')
    submit = SubmitField('登录')


class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(6, 20, message='用户名长度必须在6-20之间')])
    password = PasswordField('密码', validators=[DataRequired(), Length(6, 128, message='密码长度必须在6-128之间')])
    confirm_password = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('注册')


class CommentForm(FlaskForm):
    commented = StringField('评论', validators=[Length(0, 200, message='请保持评论不超过200字')])
    submit = SubmitField('提交')


class EditPaperForm(FlaskForm):
    url = StringField('url', [Length(0, 200, message='"url"过长')])
    title = StringField('标题', [Length(0, 200, message='"标题"过长')])
    author = StringField('作者', [Length(0, 300, message='"作者"过长')])
    abstract = StringField('摘要', [Length(0, 2000, message='"摘要"过长')])
    subjects = StringField('领域', [Length(0, 200, message='"领域"过长')])
    submit_time = StringField('提交时间', [Length(0, 20, message='"提交时间"过长')])
    category = SelectField('分类', coerce=int)

    submit = SubmitField('提交')

    def __init__(self, *args, **kwargs):
        super(EditPaperForm, self).__init__(*args, **kwargs)
        self.category.choices = [(category.id, category.name)
                                 for category in Category.query.filter_by(user=current_user).all()]


class EditCategoryForm(FlaskForm):
    new_category_name = StringField('分类',
                                    [DataRequired(),
                                     Length(1, 20, message='请将分类名限制在1-20字内'),
                                     NoneOf('未分类', message='无法创建该分类')])
    submit = SubmitField('提交')


class UrlForm(FlaskForm):
    url = StringField('论文Url', validators=[DataRequired(), URL(message='请输入正确的url')])
    submit = SubmitField('开始解析')


class NewCategoryForm(FlaskForm):
    new_category_name = StringField('分类',
                                    [DataRequired(),
                                     Length(1, 20, message='请将分类名限制在1-20字内'),
                                     NoneOf('未分类', message='无法创建该分类')])
    submit = SubmitField('提交')
