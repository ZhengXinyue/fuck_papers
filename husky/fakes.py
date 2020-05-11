from faker import Faker

from husky.extensions import db
from husky.models import Post


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
