from . import db
import flask_login


# Define an association table for the many-to-many relationship between Recipe and QIngredients
recipe_ingredients = db.Table('recipe_ingredients',
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id')),
    db.Column('ingredient_id', db.Integer, db.ForeignKey('qingredient.id'))
)
#I am a little confused on what exactly should occur between our tables. Can someone 
#talk with him during lab about exactly what tables should backpopulate what and why? 
# Also why do we need an ingredients and qingredients table? Can we not define the ingredient 
# with a quantity each time? 



class User(flask_login.UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    recipes = db.relationship('Recipe', back_populates='user')

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='recipes')
    description = db.Column(db.String(512), nullable=False)
    cooking_time = db.Column(db.Integer, nullable=False)
    number_people = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime(), nullable=False)
 
   #Need to add relationship to QIngredients and Steps 

class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(512), nullable=False)

#We either need to add a relationship where recipe_id backpopulates recipe with a column involving the quantity
#or we use a nice query later on. Something like SELECT * FROM QIngredient WHERE recipe_id == Recipe.id (my preference) 


class QIngredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(512), nullable=False)
    recipe_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(512), nullable=False)

class Step(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(512), nullable=False)
    recipe_id = db.Column(db.Integer, nullable=False)
    position = db.Column(db.Integer, nullable=False)

#If we are supposed to see a User's ratings on their profile page, we should backpopulate 
#the User with the rating ID.  

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    value = db.Column(db.Integer, nullable=False)
#Let's not worry about the photo table for now. 

    