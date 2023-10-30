import datetime
import dateutil.tz
import flask_login
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from . import db, bcrypt
from . import model

bp = Blueprint("main", __name__)


@bp.route("/")
@flask_login.login_required
def index():
    followers = db.aliased(model.User)
    query = (
    db.select(model.Message)
    .join(model.User)
    .join(followers, model.User.followers)
    .where(followers.id == flask_login.current_user.id)
    .where(model.Message.response_to == None)
    .order_by(model.Message.timestamp.desc())
    .limit(10)
)
    
    posts = db.session.execute(query).scalars().all()
    return render_template("main/index.html", posts=posts)


@bp.route('/profile/<int:user_id>')
@flask_login.login_required
def profile(user_id):
    user = db.session.get(model.User, user_id)
    query = db.select(model.Message).where(model.Message.response_to == None).where(model.Message.user_id == user_id).order_by(model.Message.timestamp.desc()).limit(10)
    posts = db.session.execute(query).scalars().all()
    if not user:
        abort(404, "User id {} doesn't exist.".format(user_id))
    if flask_login.current_user.id == user_id:
        followValue=None
    elif flask_login.current_user in user.followers:
        followValue="unfollow"
    else:
        followValue="follow"
    following = user.following
    followers = user.followers
    return render_template('main/profile.html',user=user, posts=posts,follow_button=followValue, followers=followers, following=following)

@bp.route("/post/<int:message_id>")
@flask_login.login_required
def post(message_id):
    message = db.session.get(model.Message, message_id)
    if not message:
        abort(404, "Post id {} doesn't exist.".format(message_id))
    if message.response_to != None:
        abort(403)
    query = db.select(model.Message).where(model.Message.response_to_id == message_id).order_by(model.Message.timestamp.desc())
    replies = db.session.execute(query).scalars().all()
    return render_template("main/posts.html", post=message, posts=replies)


@bp.route("/new_post", methods=["POST"])
@flask_login.login_required
def new_post():
    if not request.form.get("response_to"):
        message = model.Message(
        text = request.form.get("new_post"),
        user = flask_login.current_user,
        timestamp=datetime.datetime.now(dateutil.tz.tzlocal()),
        response_to=None)
        db.session.add(message)
        db.session.commit()
        return redirect(url_for("main.post", message_id=message.id))
    else:
        message = model.Message(
        text = request.form.get("new_post"),
        user = flask_login.current_user,
        timestamp=datetime.datetime.now(dateutil.tz.tzlocal()),
        response_to=db.session.get(model.Message, request.form.get("response_to")),
        response_to_id=request.form.get("response_to"))
        db.session.add(message)
        db.session.commit()
        return redirect(url_for("main.post", message_id=request.form.get("response_to")))

    
@bp.route("/follow/<int:user_id>", methods=["POST"])
@flask_login.login_required
def follow(user_id):
    user = db.session.get(model.User, user_id)
    if not user:
        abort(404, "User id {} doesn't exist.".format(user_id))
    if flask_login.current_user in user.followers:
        abort(403, "Already following user.")
    user.followers.append(flask_login.current_user)
    query = db.select(model.Message).where(model.Message.response_to == None).where(model.Message.user_id == user_id).order_by(model.Message.timestamp.desc()).limit(10)
    posts = db.session.execute(query).scalars().all()
    db.session.commit()
    following = user.following
    followers = user.followers
    return render_template('main/profile.html',user=user, posts=posts,follow_button="unfollow",followers=followers, following=following)
    
@bp.route("/unfollow/<int:user_id>", methods=["POST"])
@flask_login.login_required
def unfollow(user_id):
    user = db.session.get(model.User, user_id)
    if not user:
        abort(404, "User id {} doesn't exist.".format(user_id))
    if flask_login.current_user not in user.followers:
        abort(403, "Not following user.")
    user.followers.remove(flask_login.current_user)
    query = db.select(model.Message).where(model.Message.response_to == None).order_by(model.Message.timestamp.desc()).limit(10)
    posts = db.session.execute(query).scalars().all()
    db.session.commit()
    return render_template("main/index.html", posts=posts)
    