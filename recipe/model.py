from . import db
import flask_login


# Define an association table for the many-to-many relationship between Recipe and QIngredients
'''
recipe_ingredients = db.Table('recipe_ingredients',
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id')),
    db.Column('ingredient_id', db.Integer, db.ForeignKey('qingredient.id'))
)
'''



class User(flask_login.UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    recipes = db.relationship('Recipe', back_populates='user')
    ratings = db.relationship('Rating', back_populates='user')
    photos = db.relationship('Photo', back_populates='user')
    bookmarks = db.relationship('Bookmark', back_populates='user')

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='recipes')
    description = db.Column(db.String(512), nullable=False)
    cooking_time = db.Column(db.Integer, nullable=False)
    number_people = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime(), nullable=False)
    ingredients = db.relationship('Ingredient', back_populates='recipe')
    ratings = db.relationship('Rating', back_populates='recipe')
    steps = db.relationship('Step', back_populates='recipe')
    photos = db.relationship('Photo', back_populates='recipe')
    bookmarks = db.relationship('Bookmark', back_populates='recipe')

class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(512), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    recipe = db.relationship('Recipe', back_populates='ingredients')
    qingredients = db.relationship('QIngredient', back_populates='ingredient')


class QIngredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(512), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), nullable=False)
    ingredient = db.relationship('Ingredient', back_populates='qingredients')

class Step(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(512), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    recipe = db.relationship('Recipe', back_populates='steps')

#If we are supposed to see a User's ratings on their profile page, we should backpopulate 
#the User with the rating ID.  

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
    #need to determine how to store photo
    value = db.Column(db.Integer, nullable=False)    
    timestamp = db.Column(db.DateTime(), nullable=False)


#need to add bookmarked entities
class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    recipe = db.relationship('Recipe', back_populates='bookmarks')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='bookmarks')
    value = db.Column(db.Integer, nullable=False)