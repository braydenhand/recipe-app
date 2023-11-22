import datetime
import dateutil.tz
import flask_login
import pathlib
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from . import db, bcrypt
from . import model

bp = Blueprint("main", __name__)


@bp.route("/", methods=["GET"])
def index():
    choice = request.form.get("selection")
    if choice == 'Rating Highest to Lowest':
        query = (
        db.select(model.Recipe).order_by(model.Recipe.average_rating.desc())
        .limit(10)#can adjust this later
    )
        recipes = db.session.execute(query).scalars().all()
        return render_template("base.html", recipes=recipes)
    elif choice == 'Rating Lowest to Highest':
        query = (
        db.select(model.Recipe).order_by(model.Recipe.average_rating)
        .limit(10)#can adjust this later
    )
        recipes = db.session.execute(query).scalars().all()
        return render_template("base.html", recipes=recipes)
    elif choice == 'Cook Time Fastest To Slowest':
        query = (
        db.select(model.Recipe).order_by(model.Recipe.cooking_time)
        .limit(10)#can adjust this later
    )
        recipes = db.session.execute(query).scalars().all()
        return render_template("base.html", recipes=recipes)
    elif choice == 'Cook Time Slowest To Fastest':
        query = (
        db.select(model.Recipe).order_by(model.Recipe.cooking_time.desc())
        .limit(10)#can adjust this later
    )
        recipes = db.session.execute(query).scalars().all()
        return render_template("base.html", recipes=recipes)
    elif choice == 'Newest':
        query = (
        db.select(model.Recipe).order_by(model.Recipe.timestamp.desc())
        .limit(10)#can adjust this later
    )
        recipes = db.session.execute(query).scalars().all()
        return render_template("base.html", recipes=recipes)
    elif choice == 'Oldest':
        query = (
        db.select(model.Recipe).order_by(model.Recipe.timestamp)
        .limit(10)#can adjust this later
    )
        recipes = db.session.execute(query).scalars().all()
        return render_template("base.html", recipes=recipes)
    else:
        query = (
        db.select(model.Recipe).order_by(model.Recipe.timestamp.desc())
        .limit(10)#can adjust this later
    )
        recipes = db.session.execute(query).scalars().all()
        return render_template("base.html", recipes=recipes)

#potential function to append recipe for infinite scroll

@bp.route("/", methods=["POST"])
def recipe_post():
    name = request.form.get("name")
    description = request.form.get("description")
    number_people = request.form.get("number_people")
    email = request.form.get("email")
    cooking_time = request.form.get("cooking_time")

#we will need user, recipes, ratings, and bookmarked
@bp.route('/profile/<int:user_id>')
@flask_login.login_required
def profile(user_id):
    user = db.session.get(model.User, user_id)
    if not user:
        abort(404, "User id {} doesn't exist.".format(user_id))

    query = db.select(model.Recipe).where(model.Recipe.user_id == user_id).order_by(model.Recipe.timestamp.desc())
    recipes = db.session.execute(query).scalars().all()
    query = db.select(model.Rating).where(model.Rating.user_id == user_id)
    ratings = db.session.execute(query).scalars().all()
    query = db.select(model.Bookmark).where(model.Bookmark.user_id == user_id)
    bookmarks = db.session.execute(query).scalars().all()
    return render_template('main/profile.html',user=user, recipes=recipes, ratings=ratings, bookmarks=bookmarks)

#we will need recipes, steps, photos, ingredients, and ratings
@bp.route("/post/<int:recipe_id>")
def post(recipe_id):
    recipe = db.session.get(model.Recipe, recipe_id)
    if not recipe:
        abort(404, "Recipe id {} doesn't exist.".format(recipe_id))

    query = db.select(model.Step).where(model.Step.recipe_id == recipe_id).order_by(model.Step.position)
    steps = db.session.execute(query).scalars().all()
    if not steps:
        abort(410, "Recipe steps for {} doesn't exist.".format(recipe_id))
    query = db.select(model.Ingredient).where(model.Ingredient.recipe_id == recipe_id)
    ingredients = db.session.execute(query).scalars().all()
    if not ingredients:
        abort(410, "Recipe ingredients for {} doesn't exist.".format(recipe_id))
    query = db.select(model.Rating).where(model.Rating.recipe_id == recipe_id).order_by(model.Rating.timestamp.desc())
    ratings = db.session.execute(query).scalars().all()
    query = db.select(model.Photo).where(model.Photo.recipe_id == recipe_id).order_by(model.Photo.timestamp.desc())
    photos = db.session.execute(query).scalars().all()
    
    #not sure if the flask login query will auto fail if not logged in
    query = db.select(model.Bookmark).where(model.Bookmark.recipe_id == recipe_id).where(model.Bookmark.user_id == flask_login.current_user.id)
    bookmark = db.session.execute(query).scalars().all()
    query = db.select(model.Rating).where(model.Rating.recipe_id == recipe_id).where(model.Rating.user_id == flask_login.current_user.id)
    rating = db.session.execute(query).scalars().all()
    return render_template("main/posts.html", post=recipe, steps=steps, ingredients=ingredients, ratings=ratings, photos=photos, bookmark=bookmark, rating=rating)

#will need recipe, steps, ingredients, and photo
@bp.route("/new_post", methods=["POST"])
@flask_login.login_required
def new_post():
    recipe = model.Recipe(
        description = request.form.get("description"),
        user = flask_login.current_user,
        timestamp = datetime.datetime.now(dateutil.tz.tzlocal()),
        number_people = request.form.get("number_people"),
        cooking_time = request.form.get("cooking_time"),
        average_rating = 0,
    )
    stepCount = request.form.get("stepCount")
    for i in range(stepCount):
        i += 1
        name = "stepCount" + i
        step = model.Step(
            text = request.form.get(name),
            position = i,
            position = i + 1,
            recipe_id = recipe.id
        )
        db.session.add(step)   
    
    db.session.add(recipe)
    db.session.commit()
    return redirect(url_for("main.post", recipe_id=recipe.id))

@bp.route("/post/<int:recipe_id>/upload_rating", methods=["POST"])
@flask_login.login_required
def new_review(recipe_id):
    query = db.select(model.Rating).where(model.Rating.recipe_id == recipe_id).where(model.Rating.user_id == flask_login.current_user.user_id)
    rating = db.session.execute(query).scalars().all()
    
    data = request.get_json()
    rating_val = data.get('rating')
    
    if not rating:
        rating = model.Rating(
            recipe = db.session.get(model.Recipe, recipe_id),
            user = flask_login.current_user,
            value = rating_val,
            timestamp = datetime.datetime.now(dateutil.tz.tzlocal()),
        )
        db.session.add(rating)
    else:
        rating.value = rating_val
    db.session.commit()
    #not sure if a commit is needed before drawing but doing it just to be safe

    recipe = db.session.get(model.Recipe, recipe_id)
    counter = 0.0
    total = 0.0
    for rating in recipe.ratings:
        counter = counter + 1
        total  = total + rating.value
    recipe.average_rating = round (total/counter, 1)
    db.session.commit()
    return redirect(url_for("main.post", recipe_id=recipe_id))

@bp.route("/post/<int:recipe_id>/bookmark", methods=["POST"])
@flask_login.login_required
def bookmark(recipe_id):
    query = db.select(model.Bookmark).where(model.Bookmark.recipe_id == recipe_id).where(model.Bookmark.user_id == flask_login.current_user.id)
    bookmark = db.session.execute(query).scalars().all()
    if not bookmark:
        bookmark = model.Bookmark(
        recipe = db.session.get(model.Recipe, recipe_id),
        user = flask_login.current_user,
        value = 1,
        timestamp = datetime.datetime.now(dateutil.tz.tzlocal()),
        )
        db.session.add(bookmark)
    else:
        db.session.delete(bookmark)
    db.session.commit()
    return redirect(url_for("main.post", recipe_id=recipe_id))
'''
@bp.route('/recipe/<int:recipe_id>/upload_photo', methods=['POST'])
@flask_login.login_required
def upload_photo(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    uploaded_file = request.files['photo']

    if uploaded_file.filename != '':
        content_type = uploaded_file.content_type
        if content_type == "image/png":
            file_extension = "png"
        elif content_type == "image/jpeg":
            file_extension = "jpg"
        else:
            abort(400, f"Unsupported file type {content_type}")

        photo = Photo(
            user=flask_login.current_user,
            recipe=recipe,
            file_extension=file_extension
        )
        db.session.add(photo)
        db.session.commit()

        path = (
            pathlib.Path(current_app.root_path)
            / "static"
            / "photos"
            / f"photo-{photo.id}.{file_extension}"
        )
        uploaded_file.save(path)

        return redirect(url_for('recipe_view', recipe_id=recipe_id))

    abort(400, "No file uploaded")
'''