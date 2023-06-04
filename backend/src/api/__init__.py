import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from database.models import setup_db, Actor, Movie, Catalog
from auth.auth import AuthError, requires_auth

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    """
    Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    """
    Use the after_request decorator to set Access-Control-Allow
    """
    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    # ROUTES

    # ---------------------------------------------
    #  Actors
    # ---------------------------------------------
    ''' GET /actors
        returns status code 200 and json {"success": True, "actors": actors} where actors is the list of actors
            or appropriate status code indicating reason for failure
    '''
    @app.route("/actors")
    @requires_auth('get:actors')
    def get_actors(payload):
        try:
            actors = Actor.query.order_by(Actor.id).all()
            repr_actors = [actor.repr() for actor in actors]
            if len(actors) == 0:
                abort(404)
            return jsonify(
                {
                    "success": True,
                    "actors": repr_actors,
                    "total_actors": len(Actor.query.all()),
                }
            )
        except Exception as e:
            if hasattr(e, 'code') and e.code == 404:
                abort(404)
            else:
                abort(422)

    '''
        POST /actors
            creates a new row in the actors table
            requires the 'post:actors' permission
        returns status code 200 and json {"success": True, "actors": actor} where actor an array containing only the newly created actor
            or appropriate status code indicating reason for failure
    '''
    @app.route("/actors", methods=["POST"])
    @requires_auth('post:actors')
    def create_actor(payload):
        try:
            body = request.get_json()
            new_actor_name = body.get("name", None)
            new_actor_gender = body.get("gender", None)
            new_actor_age = body.get("age", None)
            if new_actor_name is None or new_actor_name == "":
                abort(422)
            if new_actor_gender is None or new_actor_gender == "":
                abort(422)
            if new_actor_age is None or new_actor_age == "":
                abort(422)
            actor_entity = Actor(name=new_actor_name, gender=new_actor_gender, age=new_actor_age)
            actor_entity.insert()
            return jsonify(
                {
                    "success": True,
                    "actors": [actor_entity.repr()]
                }
            )
        except Exception as e:
            if hasattr(e, 'code') and e.code == 401:
                abort(401)
            if hasattr(e, 'code') and e.code == 404:
                abort(404)
            else:
                abort(422)

    ''' PATCH /actors/<id>
            where <id> is the existing model id
            responds with a 404 error if <id> is not found
            updates the corresponding row for <id>
            requires the 'patch:actors' permission
        returns status code 200 and json {"success": True, "actors": actor} where actor an array containing only the updated actor
             or appropriate status code indicating reason for failure
    '''
    @app.route("/actors/<actor_id>", methods=["PATCH"])
    @requires_auth('patch:actors')
    def update_actor(payload, actor_id):
    # def update_actor(actor_id):
        try:
            actor_id = int(actor_id)
            actor = Actor.query.filter(Actor.id == actor_id).one_or_none()
            if actor is None:
                abort(404)
            body = request.get_json()
            new_actor_name = body.get("name", None)
            new_actor_gender = body.get("gender", None)
            new_actor_age = body.get("age", None)
            if new_actor_name is None or new_actor_gender is None or new_actor_age is None:
                abort(422)
            if new_actor_name != "":
                actor.name = new_actor_name
            if new_actor_gender != "":
                actor.gender = new_actor_gender
            if new_actor_age != "":
                actor.age = new_actor_age
            actor.update()
            return jsonify(
                {
                    "success": True,
                    "actors": [actor.repr()]
                }
            )
        except Exception as e:
            if hasattr(e, 'code') and e.code == 401:
                abort(401)
            if hasattr(e, 'code') and e.code == 404:
                abort(404)
            else:
                abort(422)


    ''' DELETE /actors/<id>
            where <id> is the existing model id
            responds with a 404 error if <id> is not found
            deletes the corresponding row for <id>
            requires the 'delete:actors' permission
        returns status code 200 and json {"success": True, "deleted": id} where id is the id of the deleted record
             or appropriate status code indicating reason for failure
    '''
    @app.route("/actors/<actor_id>", methods=["DELETE"])
    @requires_auth('delete:actors')
    def delete_actor(payload, actor_id):
    # def delete_actor(actor_id):
        try:
            actor_id = int(actor_id)
            actor = Actor.query.filter(Actor.id == actor_id).one_or_none()
            if actor is None:
                abort(404)
            actor.delete()
            return jsonify(
                {
                    "success": True,
                    "deleted": actor_id,
                }
            )
        except Exception as e:
            if hasattr(e, 'code') and e.code == 404:
                abort(404)
            else:
                abort(422)


    # ---------------------------------------------
    #  Movies
    # ---------------------------------------------
    ''' GET /movies
        returns status code 200 and json {"success": True, "movies": movies} where movies is the list of movies
            or appropriate status code indicating reason for failure
    '''
    @app.route("/movies")
    @requires_auth('get:movies')
    def get_movies(payload):
        try:
            movies = Movie.query.order_by(Movie.id).all()
            repr_movies = [movie.repr() for movie in movies]
            if len(movies) == 0:
                abort(404)
            return jsonify(
                {
                    "success": True,
                    "movies": [repr_movies],
                    "total_movies": len(Movie.query.all()),
                }
            )
        except Exception as e:
            if hasattr(e, 'code') and e.code == 404:
                abort(404)
            else:
                abort(422)

    ''' POST /movies
            creates a new row in the movies table
            requires the 'post:movies' permission
        returns status code 200 and json {"success": True, "movies": movie} where movie an array containing only the newly created movie
            or appropriate status code indicating reason for failure
    '''
    @app.route("/movies", methods=["POST"])
    @requires_auth('post:movies')
    def create_movie(payload):
        try:
            body = request.get_json()
            new_movie_title = body.get("title", None)
            new_movie_release_date = body.get("release_date", None)
            if new_movie_title is None or new_movie_title == "":
                abort(422)
            if new_movie_release_date is None or new_movie_release_date == "":
                abort(422)
            movie_entity = Movie(title=new_movie_title, release_date=new_movie_release_date)
            movie_entity.insert()
            return jsonify(
                {
                    "success": True,
                    "movies": [movie_entity.repr()]
                }
            )
        except Exception as e:
            if hasattr(e, 'code') and e.code == 401:
                abort(401)
            if hasattr(e, 'code') and e.code == 404:
                abort(404)
            else:
                abort(422)

    ''' PATCH /movies/<id>
            where <id> is the existing model id
            responds with a 404 error if <id> is not found
            updates the corresponding row for <id>
            requires the 'patch:movies' permission
        returns status code 200 and json {"success": True, "movies": movie} where movie an array containing only the updated movie
             or appropriate status code indicating reason for failure
    '''
    @app.route("/movies/<movie_id>", methods=["PATCH"])
    @requires_auth('patch:movies')
    def update_movie(payload, movie_id):
    # def update_movie(movie_id):
        try:
            movie_id = int(movie_id)
            movie = Movie.query.filter(Movie.id == movie_id).one_or_none()
            if movie is None:
                abort(404)
            body = request.get_json()
            new_movie_title = body.get("title", None)
            new_movie_release_date = body.get("release_date", None)
            if new_movie_title is None or new_movie_release_date is None:
                abort(422)
            if new_movie_title != "":
                movie.title = new_movie_title
            if new_movie_release_date != "":
                movie.release_date = new_movie_release_date
            movie.update()
            return jsonify(
                {
                    "success": True,
                    "movies": [movie.repr()]
                }
            )
        except Exception as e:
            if hasattr(e, 'code') and e.code == 401:
                abort(401)
            if hasattr(e, 'code') and e.code == 404:
                abort(404)
            else:
                abort(422)


    ''' DELETE /movies/<id>
            where <id> is the existing model id
            responds with a 404 error if <id> is not found
            deletes the corresponding row for <id>
            requires the 'delete:movies' permission
        returns status code 200 and json {"success": True, "deleted": id} where id is the id of the deleted record
             or appropriate status code indicating reason for failure
    '''
    @app.route("/movies/<movie_id>", methods=["DELETE"])
    @requires_auth('delete:movies')
    def delete_movie(payload, movie_id):
    # def delete_movie(movie_id):
        try:
            movie_id = int(movie_id)
            movie = Movie.query.filter(Movie.id == movie_id).one_or_none()
            if movie is None:
                abort(404)
            movie.delete()
            return jsonify(
                {
                    "success": True,
                    "deleted": movie_id,
                }
            )
        except Exception as e:
            if hasattr(e, 'code') and e.code == 404:
                abort(404)
            else:
                abort(422)


    ''' error handlers
    using the @app.errorhandler(error) decorator
    each error handler returns (with approprate messages):
        jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
            }), 404

    '''
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(404)
    def resource_not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(AuthError)
    def auth_error(ex):
        print("AuthError was raised with", ex)
        return jsonify({
            "success": False,
            "error": ex.status_code,
            "message": ex.error['description']
        }), ex.status_code
    
    return app