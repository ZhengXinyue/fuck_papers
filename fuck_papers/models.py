from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from fuck_papers.extensions import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password_hash = db.Column(db.String(128))

    papers = db.relationship('Paper', back_populates='user')
    categories = db.relationship('Category', back_populates='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    papers = db.relationship('Paper', back_populates='category')
    user = db.relationship('User', back_populates='categories')

    def delete(self):
        default_category = Category.query.get(1)
        papers = self.papers[:]
        for paper in papers:
            paper.category = default_category
        db.session.delete(self)
        db.session.commit()


class Paper(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(200))
    title = db.Column(db.String(200))
    author = db.Column(db.String(300))
    abstract = db.Column(db.Text)
    subjects = db.Column(db.String(200))

    add_timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    last_read_timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    star = db.Column(db.Boolean, default=False)
    comment = db.Column(db.String(300))

    user_id = db.Column(db.Integer, db.ForeignKye('user.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    category = db.relationship('Category', back_populates='papers')
    user = db.relationship('User', back_populates='papers')


