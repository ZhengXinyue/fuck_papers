import random

from flask import current_app
from faker import Faker
from sqlalchemy.exc import IntegrityError

from fuck_papers.extensions import db
from fuck_papers.models import User, Category, Paper


fake = Faker()


def fake_users(count=5):
    for i in range(count):
        user = User(
            username=fake.user_name(),
            password_hash=fake.password()
        )
        user.set_password(user.password_hash)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.rollback()
    user = User(
        username='zhengxinyue',
        password_hash='123456'
    )
    user.set_password(user.password_hash)
    db.session.add(user)
    db.session.commit()


def fake_categories(count=50):
    user_count = User.query.count()
    for i in range(1, user_count + 1):
        default_category = Category(
            name='未分类',
            user=User.query.get(i)
        )
        db.session.add(default_category)
    db.session.commit()

    # 为每个用户添加个人分类
    for i in range(count):
        category = Category(
            name=fake.word(),
            user=User.query.get(random.choice(list(range(1, user_count+1))))
        )
        db.session.add(category)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_papers(count=400):
    for i in range(count):
        url = fake.url()
        title = fake.word()
        author = fake.user_name()
        abstract = fake.text(1000)
        subjects = fake.word()
        submit_time = fake.word()

        add_timestamp = fake.date_time_this_year()
        last_read_timestamp = fake.date_time_this_year()
        if random.random() < 0.5:
            stared = True
        else:
            stared = False
        if random.random() < 0.5:
            readed = True
        else:
            readed = False
        if random.random() < 0.5:
            commented = fake.sentence()
        else:
            commented = None
        user = User.query.get(random.randint(1, User.query.count()))

        paper = Paper(
            url=url,
            title=title,
            author=author,
            abstract=abstract,
            subjects=subjects,
            submit_time=submit_time,

            add_timestamp=add_timestamp,
            last_read_timestamp=last_read_timestamp,
            stared=stared,
            readed=readed,
            commented=commented,

            user=user,
            category=random.choice(user.categories))

        db.session.add(paper)
    db.session.commit()
