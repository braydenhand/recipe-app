import datetime
import dateutil.tz

from flask import Blueprint, render_template


from . import model

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    user = model.User(email="mary@example.com", name="mary")
    posts = [
            model.Message(
        user=user,
        text="Test post 1",
        timestamp=datetime.datetime.now(dateutil.tz.tzlocal()),
    ),
    model.Message(
        user=user,
        text="Another post",
        timestamp=datetime.datetime.now(dateutil.tz.tzlocal()),
    ),
    ]
    return render_template("main/index.html", posts=posts)
@bp.route('/profile')
def profile():
    user = model.User(email="tom@example.com", name="tom")
    posts = [
        model.Message(
        user=user,
        text="Test post 1",
        timestamp=datetime.datetime.now(dateutil.tz.tzlocal()),
    ),
    model.Message(
        user=user,
        text="Another post",
        timestamp=datetime.datetime.now(dateutil.tz.tzlocal()),
    ),
    ]
    return render_template('main/profile.html', posts=posts)
@bp.route('/posts')
def posts():
    user = model.User(email="jason@example.com", name="jason")
    post = model.Message(
            user=user, text="Main Post", timestamp=datetime.datetime.now(dateutil.tz.tzlocal())
        )
    replies = [
        model.Message(
        user=user,
        text="Test post 1",
        timestamp=datetime.datetime.now(dateutil.tz.tzlocal()),
    ),
    model.Message(
        user=user,
        text="Another post",
        timestamp=datetime.datetime.now(dateutil.tz.tzlocal()),
    ),
    ]
    return render_template('main/posts.html', posts=replies, post=post)
