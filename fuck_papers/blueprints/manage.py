from flask import render_template, flash, redirect, url_for, Blueprint
from flask_login import login_user, logout_user, login_required, current_user

from fuck_papers.forms import LoginForm, RegisterForm
from fuck_papers.models import User
from fuck_papers.utils import redirect_back
from fuck_papers.extensions import db

manage_bp = Blueprint('manage', __name__)
