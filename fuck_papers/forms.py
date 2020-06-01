from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, SubmitField, SelectField, BooleanField, PasswordField
from wtforms import ValidationError
from wtforms.validators import DataRequired, Length, URL, NoneOf, EqualTo

from fuck_papers.models import Category, User


class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(6, 20, message='用户名长度必须在6-20之间')])
    password = PasswordField('密码', validators=[DataRequired(), Length(6, 128, message='密码长度必须在6-128之间')])
    remember = BooleanField('记住我')
    submit = SubmitField('登录')


class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(6, 20, message='用户名长度必须在6-20之间')])
    password = PasswordField('密码', validators=[
        DataRequired(), Length(6, 128, message='密码长度必须在6-128之间'), EqualTo('confirm_password', message='密码不一致')])
    confirm_password = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名已被注册')


class CommentForm(FlaskForm):
    commented = StringField('评论', validators=[Length(0, 200, message='请保持评论不超过200字')])
    submit = SubmitField('提交')


class EditPaperForm(FlaskForm):
    url = StringField('url', [Length(0, 200, message='"url"应在0-200字之间')])
    title = StringField('标题', [Length(0, 200, message='"标题"应在0-200字之间')])
    author = StringField('作者', [Length(0, 200, message='"作者"应在0-200字之间')])
    abstract = StringField('摘要', [Length(0, 2000, message='"摘要"应在0-200字之间')])
    subjects = StringField('领域', [Length(0, 200, message='"领域"应在0-200字之间')])
    submit_time = StringField('提交时间', [Length(0, 200, message='"提交时间"应在0-200字之间')])
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
                                     NoneOf('未分类', message='已有该分类')])
    submit = SubmitField('提交')


class UrlForm(FlaskForm):
    url = StringField('论文Url', validators=[DataRequired(), URL(message='请输入正确的url')])
    category = SelectField('分类', coerce=int)
    submit = SubmitField('开始解析')

    def __init__(self, *args, **kwargs):
        super(UrlForm, self).__init__(*args, **kwargs)
        self.category.choices = [(category.id, category.name)
                                 for category in Category.query.filter_by(user=current_user).all()]


class NewCategoryForm(FlaskForm):
    new_category_name = StringField('分类',
                                    [DataRequired(),
                                     Length(1, 50, message='请将分类名限制在1-20字内'),
                                     NoneOf('未分类', message='无法创建该分类')])
    submit = SubmitField('提交')
