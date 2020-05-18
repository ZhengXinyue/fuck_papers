from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, ValidationError, HiddenField, \
    BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Optional, URL, EqualTo


class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(6, 20, message='用户名长度必须在6-20之间')])
    password = PasswordField('密码', validators=[DataRequired(), Length(6, 128, message='密码长度必须在6-128之间')])
    remember = BooleanField('记住我')
    submit = SubmitField('登录')


class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 20, message='用户名长度必须在6-20之间')])
    password = PasswordField('密码', validators=[DataRequired(), Length(6, 128, message='密码长度必须在6-128之间')])
    confirm_password = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('注册')


class Comment(FlaskForm):
    comment = CKEditorField('评论', validators=[DataRequired(), Length(1, 300, message='请保持评论不超过300字')])
    submit = SubmitField('提交')


class UrlForm(FlaskForm):
    url = StringField('论文Url', validators=[DataRequired()])
    submit = SubmitField('开始解析')
