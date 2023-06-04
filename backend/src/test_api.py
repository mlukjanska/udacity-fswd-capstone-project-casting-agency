import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import json
import requests


from api import create_app
from database.models import setup_db, Actor, Movie


load_dotenv()

def memoize(function):
    memo = {}
    def wrapper(*args):
        if args in memo:
            return memo[args]
        else:
            rv = function(*args)
            memo[args] = rv
            return rv
    return wrapper

class CastingAgencyTestCase(unittest.TestCase):
    """This class represents the casting agency test cases"""

    # https://stackoverflow.com/questions/48552474/auth0-obtain-access-token-for-unit-tests-in-python/48554119#48554119
    def getUserToken(self, userName):
        # testing user (with the most permissions):
        testingUsers = {
            os.getenv('TEST_USERNAME'): os.getenv('TEST_PASSWORD'), 
        }
        # client id and secret come from LogIn (Test Client)! which has password enabled under "Client > Advanced > Grant Types > Tick Password"
        url = 'https://'+ os.getenv('AUTH0_DOMAIN') + '/oauth/token' 
        headers = {'content-type': 'application/json'}
        password = testingUsers[userName]
        parameter = { 
            "client_id": os.getenv('AUTH0_TEST_CLIENT_ID'), 
            "client_secret": os.getenv('AUTH0_TEST_CLIENT_SECRET'), 
            "audience": os.getenv('AUTH0_API_AUDIENCE'), 
            "grant_type": "password",
            "username": userName,
            "password": password, 
            "scope": "openid" 
        } 
        # do the equivalent of a CURL request from https://auth0.com/docs/quickstart/backend/python/02-using#obtaining-an-access-token-for-testing
        responseDICT = json.loads(requests.post(url, json=parameter, headers=headers).text)
        return responseDICT['access_token']

    @memoize # memoize code from: https://stackoverflow.com/a/815160
    def getUserTokenHeaders(self, userName='executive_producer@test.com'):
        return { 'authorization': "Bearer " + self.getUserToken(userName)} 


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

        self.authorization_header = self.getUserTokenHeaders()

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
        res = self.client().get("/actors", headers=self.authorization_header)
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
        res = self.client().post("/actors", json=new_actor, headers=self.authorization_header)
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
        res = self.client().post("/actors", json=new_actor, headers=self.authorization_header)
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
        res = self.client().delete("/actors/" + str(actor.id), headers=self.authorization_header)
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
        res = self.client().patch("/actors/" + str(actor.id), json=patch_actor, headers=self.authorization_header)
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
        res = self.client().get("/movies", headers=self.authorization_header)
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
        res = self.client().post("/movies", json=new_movie, headers=self.authorization_header)
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
        res = self.client().post("/movies", json=new_movie, headers=self.authorization_header)
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
        res = self.client().delete("/movies/" + str(movie.id), headers=self.authorization_header)
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
        res = self.client().patch("/movies/" + str(movie.id), json=patch_movie, headers=self.authorization_header)
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