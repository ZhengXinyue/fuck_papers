from faker import Faker
from sqlalchemy.exc import IntegrityError

from husky.extensions import db
from husky.models import Post, User


fake = Faker()


def fake_posts(count=50):
    for i in range(count):
        post = Post(
            title=fake.sentence(),
            body=fake.text(2000),
            timestamp=fake.date_time_this_year()
        )
        db.session.add(post)
    db.session.commit()


def fake_users(count=10):
    for i in range(count):
        password = fake.password()
        user = User(username=fake.name(),
                    password_hash=password)
        user.set_password(password)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
