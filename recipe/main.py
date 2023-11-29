import datetime, dateutil.tz, flask_login, pathlib
from flask import request, current_app, Blueprint, render_template, redirect, url_for, abort
from . import db, model

bp = Blueprint("main", __name__)

@bp.route("/", methods=["GET"])
def index():
    choice = request.args.get("selection")
    
    if choice == 'Rating Highest To Lowest':
        order_by = model.Recipe.average_rating.desc()
    elif choice == 'Rating Lowest To Highest':
        order_by = model.Recipe.average_rating
    elif choice == 'Cook Time Fastest To Slowest':
        order_by = model.Recipe.cooking_time
    elif choice == 'Cook Time Slowest To Fastest':
        order_by = model.Recipe.cooking_time.desc()
    elif choice == 'Newest':
        order_by = model.Recipe.timestamp.desc()
    elif choice == 'Oldest':
        order_by = model.Recipe.timestamp
    else:
        order_by = model.Recipe.timestamp.desc()

    query = db.select(model.Recipe).order_by(order_by).limit(10)
    recipes = db.session.execute(query).scalars().all()

    return render_template("main/index.html", recipes=recipes)

# Potential function to append recipe for infinite scroll

# We will need user, recipes, ratings, and bookmarked
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
    rates =[] 
    for i in ratings:
        rates.append(i.recipe)

    query = db.select(model.Bookmark).where(model.Bookmark.user_id == user_id)
    bookmarks = db.session.execute(query).scalars().all()
    books =[] 
    for i in bookmarks:
        books.append(i.recipe)

    return render_template('main/profile.html',user=user, recipes=recipes, ratings=rates, bookmarks=books)

# We will need recipes, steps, photos, ingredients, and ratings
@bp.route("/recipe/<int:recipe_id>")
def recipe(recipe_id):
    recipe = db.session.get(model.Recipe, recipe_id)
    if not recipe:
        abort(404, "Recipe id {} doesn't exist.".format(recipe_id))
    query = db.select(model.Step).where(model.Step.recipe_id == recipe_id).order_by(model.Step.position)
    steps = db.session.execute(query).scalars().all()
    if not steps:
        abort(410, "Recipe steps for {} doesn't exist.".format(recipe_id))
    query = db.select(model.QIngredient).where(model.QIngredient.recipe_id == recipe_id)
    ingredients = db.session.execute(query).scalars().all()
    if not ingredients:
        abort(410, "Recipe ingredients for {} doesn't exist.".format(recipe_id))
    query = db.select(model.Rating).where(model.Rating.recipe_id == recipe_id).order_by(model.Rating.timestamp.desc())
    ratings = db.session.execute(query).scalars().all()
    query = db.select(model.Photo).where(model.Photo.recipe_id == recipe_id).order_by(model.Photo.timestamp.desc())
    photos = db.session.execute(query).scalars().all()

    # TODO fix flask login to check authentication before pulling rating
   # if current_user.is_authenticated():
   #     query = db.select(model.Rating).where(model.Rating.recipe_id == recipe_id).where(model.Rating.user_id == flask_login.current_user.id)
   #     rating = db.session.execute(query).scalars().first()
   # else:
   #     rating = None
    query = db.select(model.Rating).where(model.Rating.recipe_id == recipe_id).where(model.Rating.user_id == flask_login.current_user.id)
    rating = db.session.execute(query).scalars().first()
    return render_template("main/recipe.html", recipe=recipe, steps=steps, ingredients=ingredients, ratings=ratings, photos=photos, rating=rating)

# Will need recipe, steps, ingredients, and photo
@bp.route("/create_recipe", methods=["POST"])
@flask_login.login_required
def create_recipe():
    recipe = model.Recipe(
        name = request.form.get("name"),
        description = request.form.get("description"),
        user = flask_login.current_user,
        timestamp = datetime.datetime.now(dateutil.tz.tzlocal()),
        number_people = request.form.get("number_people"),
        cooking_time = request.form.get("cooking_time"),
        average_rating = 0,
    )
    db.session.add(recipe)
    db.session.commit()
    stepCount = int(request.form.get("stepCount"))
    
    for i in range(stepCount):
        i += 1
        name = "stepCount" + str(i)
        step = model.Step(
            text = request.form.get(name),
            position = i,
            recipe_id = recipe.id
        )
        db.session.add(step)   
    
    ingredientCount = int(request.form.get("ingredientCount"))
    for i in range(ingredientCount):
        i += 1
        name = "ingredientName" + str(i)
        ingredient = model.Ingredient(
            name = request.form.get(name)
        )
        db.session.add(ingredient)
        db.session.commit()
        q = "quantity" + str(i)
        u = "unit" + str(i)
        qIngredient = model.QIngredient(
            ingredient_id = ingredient.id,
            quantity = request.form.get(q),
            unit = request.form.get(u),
            recipe_id = recipe.id,
        )
        db.session.add(qIngredient)
    db.session.commit()
    
    return redirect(url_for("main.recipe", recipe_id=recipe.id))


@bp.route("/create_recipe", methods=["GET"])
@flask_login.login_required
def create_recipe_get():
    return render_template("main/create_recipe.html")

@bp.route("/rate/<int:recipe_id>/<int:value>", methods=["POST","GET"])
@flask_login.login_required
def rate(recipe_id, value):
   # value = request.form.get("star")
    query = db.select(model.Rating).where(model.Rating.recipe_id == recipe_id).where(model.Rating.user_id == flask_login.current_user.id)
    rating = db.session.execute(query).scalars().first()
    if not rating:
        rating = model.Rating(
            recipe = db.session.get(model.Recipe, recipe_id),
            user = flask_login.current_user,
            value = value,
            timestamp = datetime.datetime.now(dateutil.tz.tzlocal()),
        )
        db.session.add(rating)
    else:
        rating.value = value
    db.session.commit()
    #Not sure if a commit is needed before drawing but doing it just to be safe

    recipe = db.session.get(model.Recipe, recipe_id)
    counter = 0.0
    total = 0.0
    for rating in recipe.ratings:
        counter = counter + 1
        total  = total + rating.value
    #Rounding needs to allow for floats 
    #recipe.average_rating = round (total/counter, 1)
    recipe.average_rating = int (total/counter)

    db.session.commit()
    return redirect(url_for("main.recipe", recipe_id=recipe_id))

@bp.route("/recipe/<int:recipe_id>/bookmark", methods=["POST"])
@flask_login.login_required
def bookmark(recipe_id):
    query = db.select(model.Bookmark).where(model.Bookmark.recipe_id == recipe_id).where(model.Bookmark.user_id == flask_login.current_user.id)
    bookmark = db.session.execute(query).scalars().first()
    if not bookmark:
        bookmark = model.Bookmark(
        recipe = db.session.get(model.Recipe, recipe_id),
        user = flask_login.current_user,
        )
        db.session.add(bookmark)
    else:
        db.session.delete(bookmark)
    db.session.commit()
    return redirect(url_for("main.recipe", recipe_id=recipe_id))

# Photo submission controller
@bp.route('/recipe/<int:recipe_id>/upload_photo', methods=['POST'])
@flask_login.login_required
def upload_photo(recipe_id):
    uploaded_file = request.files['photo']

    content_type = uploaded_file.content_type
    if content_type == "image/png":
        file_extension = "png"
    elif content_type == "image/jpeg":
        file_extension = "jpg"
    else:
        abort(400, f"Unsupported file type {content_type}")

    if uploaded_file.filename != '':
        recipe = model.Recipe.query.get_or_404(recipe_id)
        photo = model.Photo(
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

    return redirect(url_for('main.recipe', recipe_id=recipe_id))
