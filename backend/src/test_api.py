import os
import unittest
import json
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv

from api import create_app
from database.models import setup_db, Actor, Movie


load_dotenv()


class CastingAgencyTestCase(unittest.TestCase):
    """This class represents the casting agency test cases"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        database_username = os.getenv('DATABASE_USERNAME')
        database_password = os.getenv('DATABASE_PASSWORD')
        database_host = os.getenv('DATABASE_HOST')
        database_port = os.getenv('DATABASE_PORT')
        self.database_name = os.getenv('TEST_DATABASE_NAME')
        self.database_path = "postgresql://{}:{}@{}/{}".format(database_username, database_password, database_host + ":" + database_port, self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
    
    def tearDown(self):
        """Executed after reach test"""
        # with self.app.app_context():
        #     self.db.session.commit()
        pass

    # ---------------------------------------------
    #  Actors
    # ---------------------------------------------

    def test_get_actors(self):
        actor = Actor(
            name='John Doe',
            age=27,
            gender='male')
        actor.insert()
        res = self.client().get("/actors")
        self.assertTrue(res)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_actors"])
        self.assertTrue(type(data['total_actors']) is int)
        self.assertTrue(len(data["actors"]))
        # Clean up
        actor.delete()

    def test_create_actor(self):
        new_actor = {
            "name": "Test Get Actor", 
            "age": 42, 
            "gender": "Male"
        }
        res = self.client().post("/actors", json=new_actor)
        self.assertTrue(res)
        self.assertEqual(res.status_code, 200)

        data = json.loads(res.data)
        self.assertEqual(data["success"], True)
        self.assertEqual(data['actors'][0]["name"], new_actor['name'])
        self.assertEqual(data['actors'][0]["age"], new_actor['age'])
        self.assertEqual(data['actors'][0]["gender"], new_actor['gender'])
        self.assertTrue(type(data['actors'][0]["id"]) is int)
        # Clean up
        actor = Actor.query.filter(Actor.id == data['actors'][0]["id"]).one_or_none()
        actor.delete()

    def test_create_422_new_actor(self):
        new_actor = {
            "name": "Test Get Actor", 
            "age": 42
        }
        res = self.client().post("/actors", json=new_actor)
        self.assertTrue(res)
        self.assertEqual(res.status_code, 422)

        data = json.loads(res.data)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_delete_actor(self):
        actor = Actor(
            name='John Doe',
            age=27,
            gender='male')
        actor.insert()
        res = self.client().delete("/actors/" + str(actor.id))
        self.assertTrue(res)
        self.assertEqual(res.status_code, 200)

        data = json.loads(res.data)
        deleted_actor = Actor.query.filter(Actor.id == actor.id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], actor.id)
        self.assertEqual(deleted_actor, None)

    def test_update_actor(self):
        actor = Actor(
            name='John Doe',
            age=27,
            gender='male')
        actor.insert()
        patch_actor = {
            "name": "Updated Test Actor", 
            "age": 11, 
            "gender": "Female"
        }
        res = self.client().patch("/actors/" + str(actor.id), json=patch_actor)
        self.assertTrue(res)
        self.assertEqual(res.status_code, 200)
        updated_data = json.loads(res.data)
        self.assertEqual(updated_data["success"], True)
        self.assertEqual(updated_data['actors'][0]["name"], patch_actor['name'])
        self.assertEqual(updated_data['actors'][0]["age"], patch_actor['age'])
        self.assertEqual(updated_data['actors'][0]["gender"], patch_actor['gender'])
        self.assertEqual(updated_data['actors'][0]["id"], actor.id)
        # Clean up
        actor.delete()

    # ---------------------------------------------
    #  Movies
    # ---------------------------------------------

    def test_get_movies(self):
        movie = Movie(
          title='Test Movie',
          release_date='11-12-2023')
        movie.insert()
        res = self.client().get("/movies")
        self.assertTrue(res)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_movies"])
        self.assertTrue(type(data['total_movies']) is int)
        self.assertTrue(len(data["movies"]))
        # Clean up
        movie.delete()

    def test_create_movie(self):
        new_movie = {
            "title": "Test Get Movie", 
            "release_date": '11-12-2023', 
        }
        res = self.client().post("/movies", json=new_movie)
        self.assertTrue(res)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["success"], True)
        self.assertEqual(data['movies'][0]["title"], new_movie['title'])
        self.assertEqual(data['movies'][0]["release_date"], new_movie['release_date'])
        self.assertTrue(type(data['movies'][0]["id"]) is int)
        # Clean up
        movie = Movie.query.filter(Movie.id == data['movies'][0]["id"]).one_or_none()
        movie.delete()

    def test_create_422_new_movie(self):
        new_movie = {
            "title": "Test Get Movie - 422", 
        }
        res = self.client().post("/movies", json=new_movie)
        self.assertTrue(res)
        self.assertEqual(res.status_code, 422)

        data = json.loads(res.data)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_delete_movie(self):
        movie = Movie(
          title='Test Movie',
          release_date='11-12-2023')
        movie.insert()
        res = self.client().delete("/movies/" + str(movie.id))
        self.assertTrue(res)
        self.assertEqual(res.status_code, 200)

        data = json.loads(res.data)
        deleted_movie = Movie.query.filter(Movie.id == movie.id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], movie.id)
        self.assertEqual(deleted_movie, None)

    def test_update_movie(self):
        movie = Movie(
          title='Test Movie',
          release_date='11-12-2023')
        movie.insert()
        patch_movie = {
            "title": "Test Get Movie - 422", 
            "release_date": '11-12-2023', 
        }
        res = self.client().patch("/movies/" + str(movie.id), json=patch_movie)
        self.assertTrue(res)
        self.assertEqual(res.status_code, 200)
        updated_data = json.loads(res.data)
        self.assertEqual(updated_data["success"], True)
        self.assertEqual(updated_data['movies'][0]["title"], patch_movie['title'])
        self.assertEqual(updated_data['movies'][0]["release_date"], patch_movie['release_date'])
        self.assertEqual(updated_data['movies'][0]["id"], movie.id)
        # Cleanup
        movie.delete()

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()