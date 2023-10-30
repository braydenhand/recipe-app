from . import db
import flask_login


class FollowingAssociation(db.Model):
    follower_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), primary_key=True, nullable=False
    )
    followed_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), primary_key=True, nullable=False
    )

class User(flask_login.UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    recipes = db.relationship('Recipe', back_populates='user')
    following = db.relationship(
    "User",
    secondary=FollowingAssociation.__table__,
    primaryjoin=FollowingAssociation.follower_id == id,
    secondaryjoin=FollowingAssociation.followed_id == id,
    back_populates="followers",
    )
    followers = db.relationship(
        "User",
        secondary=FollowingAssociation.__table__,
        primaryjoin=FollowingAssociation.followed_id == id,
        secondaryjoin=FollowingAssociation.follower_id == id,
        back_populates="following",
    )

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='recipes')
    description = db.Column(db.String(512), nullable=False)
    cooking_time = db.Column(db.Integer, nullable=False)
    number_people = db.Column(db.Integer, nullable=False)
 
   #Need to add relationship to QIngredients and Steps 
    response_to_id = db.Column(db.Integer, db.ForeignKey('message.id'))
    response_to = db.relationship('Message', back_populates='responses', remote_side=[id])
    responses = db.relationship('Message', back_populates='response_to', remote_side=[response_to_id])

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

    