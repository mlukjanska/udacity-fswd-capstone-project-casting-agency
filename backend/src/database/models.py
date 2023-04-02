import os
from sqlalchemy import Column, String, Integer
from flask_sqlalchemy import SQLAlchemy
import json
from dotenv import load_dotenv
from flask_migrate import Migrate

load_dotenv()

database_name = os.getenv('DATABASE_NAME')
database_username = os.getenv('DATABASE_USERNAME')
database_password = os.getenv('DATABASE_PASSWORD')
database_host = os.getenv('DATABASE_HOST')
database_port = os.getenv('DATABASE_PORT')
database_path = "postgresql://{}:{}@{}/{}".format(
    database_username, database_password, database_host + ":" + database_port, database_name
)

db = SQLAlchemy()
migrate = Migrate()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''

def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.app_context().push()
    db.app = app
    db.init_app(app)
    migrate.init_app(app, db)
    db.create_all()

'''
db_drop_and_create_all()
    drops the database tables and starts fresh
    can be used to initialize a clean database
    !!NOTE you can change the database_filename variable to have multiple verisons of a database
'''


# def db_drop_and_create_all():
#     db.drop_all()
#     db.create_all()
#     # add one demo row which is helping in POSTMAN test
#     # drink = Drink(
#     #     title='water',
#     #     recipe='[{"name": "water", "color": "blue", "parts": 1}]'
#     # )


#     # drink.insert()

''' Movie
a persistent movie entity, extends the base SQLAlchemy Model
'''

class Movie(db.Model):
    __tablename__ = 'Movie'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    release_date = db.Column(db.Date, nullable=False)

    '''
    repr()
        representation of the Movie model
    '''

    def repr(self):
        return {
            'id': self.id,
            'title': self.title,
            'release_date': self.release_date.strftime("%m-%d-%Y")
        }

    '''
    insert()
        inserts a new model into a database
        the model must have a title and release_date
        the model must have a unique id (is automatically incremented)
        EXAMPLE
            movie = Movie(title=req_title, release_date=req_release_date)
            movie.insert()
    '''

    def insert(self):
        db.session.add(self)
        db.session.commit()

    '''
    delete()
        deletes a new model from a database
        the model must exist in the database
        EXAMPLE
            movie = Movie(id=req_id)
            movie.delete()
    '''

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    '''
    update()
        updates a new model in a database
        the model must exist in the database
        EXAMPLE
            movie = Movie.query.filter(Movie.id == id).one_or_none()
            movie.title = 'Coffee and Cigarettes'
            movie.update()
    '''

    def update(self):
        db.session.commit()

    def __repr__(self):
        return json.dumps(self.repr())

''' Actor
a persistent actor entity, extends the base SQLAlchemy Model
'''

class Actor(db.Model):
    __tablename__ = 'Actor'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String, nullable=False)

    '''
    repr()
        representation of the Actor model
    '''

    def repr(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender
        }

    '''
    insert()
        inserts a new model into a database
        the model must have a name, age, gender
        the model must have a unique id (is automatically incremented)
        EXAMPLE
            actor = Actor(name=req_name, age=req_age, gender=req_gender)
            actor.insert()
    '''

    def insert(self):
        db.session.add(self)
        db.session.commit()

    '''
    delete()
        deletes a new model from a database
        the model must exist in the database
        EXAMPLE
            actor = Actor(id=req_id)
            actor.delete()
    '''

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    '''
    update()
        updates a new model in a database
        the model must exist in the database
        EXAMPLE
            actor = Actor.query.filter(Actor.id == id).one_or_none()
            actor.name = 'John Doe'
            actor.age = 32
            actor.gener = 'male'
            actor.update()
    '''

    def update(self):
        db.session.commit()

    def __repr__(self):
        return json.dumps(self.repr())

class Catalog(db.Model):
  __tablename__ = 'Catalog'

  id = db.Column(db.Integer, primary_key=True)
  actor_id = db.Column(db.Integer, db.ForeignKey('Actor.id'), nullable=False)
  movie_id = db.Column(db.Integer, db.ForeignKey('Movie.id'), nullable=False)
  actor = db.relationship('Actor', backref=db.backref('catalog_actor'), cascade='all, delete')
  movies = db.relationship('Movie', backref=db.backref('catalog_movie'), cascade='all, delete')