import random

from faker import Faker
from sqlalchemy.exc import IntegrityError

from fuck_papers.extensions import db
from fuck_papers.models import User, Category, Paper


fake = Faker()


def fake_users(count=10):
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
    # 为每个用户添加基础分类
    for i in range(1, user_count + 1):
        recently_category = Category(
            name='最近阅读',
            user=User.query.get(i)
        )
        star_category = Category(
            name='收藏',
            user=User.query.get(i),
        )
        read_category = Category(
            name='已读',
            user=User.query.get(i)
        )
        comment_category = Category(
            name='已评论',
            user=User.query.get(i)
        )
        db.session.add(star_category)
        db.session.add(read_category)
        db.session.add(comment_category)
        db.session.add(recently_category)
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
        paper = Paper(
            url=fake.url(),
            title=fake.word(),
            author=fake.user_name(),
            abstract=fake.text(1000),
            subjects=fake.word(),

            add_timestamp=fake.date_time_this_year(),
            last_read_timestamp=fake.date_time_this_year(),
            star=random.choice([True, False]),
            comment=fake.sentence(),

            category=Category.query.get(random.randint(1, Category.query.count())),
            user=User.query.get(random.randint(1, User.query.count()))
        )
        db.session.add(paper)
    db.session.commit()
