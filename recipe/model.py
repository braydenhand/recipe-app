import flask_login
from . import db

class User(flask_login.UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime(), nullable=False)
    recipes = db.relationship('Recipe', back_populates='user')
    ratings = db.relationship('Rating', back_populates='user')
    photos = db.relationship('Photo', back_populates='user')
    bookmarks = db.relationship('Bookmark', back_populates='user')

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='recipes')
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=False)
    cooking_time = db.Column(db.Integer, nullable=False)
    number_people = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime(), nullable=False)
    qingredients = db.relationship('QIngredient', back_populates='recipe')
    average_rating = db.Column(db.Integer, nullable=False)
    ratings = db.relationship('Rating', back_populates='recipe')
    steps = db.relationship('Step', back_populates='recipe')
    photos = db.relationship('Photo', back_populates='recipe')
    bookmarks = db.relationship('Bookmark', back_populates='recipe')

class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(512), nullable=False)
    qingredients = db.relationship('QIngredient', back_populates='ingredient')

class QIngredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(32), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    recipe = db.relationship('Recipe', back_populates='qingredients')
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), nullable=False)
    ingredient = db.relationship('Ingredient', back_populates='qingredients')

class Step(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    position = db.Column(db.Integer, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    recipe = db.relationship('Recipe', back_populates='steps')

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    recipe = db.relationship('Recipe', back_populates='ratings')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='ratings')
    value = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime(), nullable=False)

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    recipe = db.relationship('Recipe', back_populates='photos')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='photos')
    file_extension = db.Column(db.String(8), nullable=False)  
    timestamp = db.Column(db.DateTime(), nullable=True)

class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='bookmarks')
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    recipe = db.relationship('Recipe', back_populates='bookmarks')
