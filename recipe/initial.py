import datetime, dateutil
from recipe import db, model, create_app

app = create_app()
with app.app_context():
    user = model.User(
        name='brady',
        email='brady@example.com',
        password='brady',
        timestamp=datetime.datetime.now(dateutil.tz.tzlocal()),
    )
    db.session.add(user)
    db.session.commit()
    test_recipe = model.Recipe(
        user_id=user.id,
        user=user,
        name='Dummy Recipe',
        description='This is a dummy recipe for testing purposes.',
        cooking_time=30,
        number_people=4,
        timestamp=datetime.datetime.now(dateutil.tz.tzlocal()),
        ingredients=[],
        steps=[],
    )
    db.session.add(test_recipe)
    db.session.commit()
    step1 = model.Step(
                text='Step 1: Do something',
                position=1,
                recipe_id=test_recipe.id,
                recipe=test_recipe,
                )
    step2 = model.Step(
                text='Step 1: Do something',
                position=2,
                recipe_id=test_recipe.id,
                recipe=test_recipe,
                )
    db.session.add(step1)
    db.session.add(step2)
    db.session.commit()
