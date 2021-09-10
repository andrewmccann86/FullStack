import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, Movies, Actors
from auth import AuthError, requires_auth, get_token_auth_header


def create_app(test_config=None):
  # create and configure the app.
  app = Flask(__name__)
  CORS(app)

  # After_request decorator setup for GET, POST, PATCH, DELETE & OPTIONS.
  @app.after_request
  def after_request(response):
    response.headers.add(
      'Access-Control-Allow-Headers',
      'Content-Type, Authorisation, true')
    response.headers.add(
      'Access-Control-Allow-Methods',
      'GET, POST, PATCH, DELETE, OPTIONS')
    return response
  
  # Home endpoint.
  @app.route('/')
  def welcome():
    return 'Welcome to the Casting Agency'
  
  # Movie endpoints.
  # Setup endpoint to handle the GET requests.
  # GET method not specified as it is the default method.
  @app.route('/movies')
  @requires_auth('get:movies')
  def get_movies(jwt):
    # Query to retrieve all movies.
    movies = Movies.query.order_by(Movies.id).all()

    # Format & return results on success
    try:
      return jsonify({
        'success': True,
        'movies': [movie.format() for movie in movies]
        }), 200
    except:
      abort(404)

  # Setup endpoint to handle the POST requests.
  # POST method specified.
  @app.route('/movies', methods=['POST'])
  @requires_auth('post:movies')
  def post_movie(jwt):

    # get response data
    data = request.get_json()
    title = data.get('title', None)
    release_date = data.get('release_date', None)

    # Insert new movie details to the DB.
    try:
      movie = Movies(title=title, release_date=release_date)
      movie.insert()
      return jsonify({
        'success': True,
        'movie': movie.format()
        }), 201
    except:
      abort(500)
  
  # Setup endpoint to hand the PATCH requests.
  # PATCH method specified.
  @app.route('/movies/<id>', methods=['PATCH'])
  @requires_auth('patch:movies')
  def patch_movie(jwt, id):

    data = request.get_json()
    title = data.get('title', None)
    release_date = data.get('release_date', None)

    movie = Movies.query.get(id)

    # Return a 404 error if no movie.
    if movie is None:
      abort(404)

    # Return a 400 error if there is no title or release date.
    if title is None or release_date is None:
      abort(400)

    movie.title = title
    movie.release_date = release_date

    # Try to update movie details in the DB.
    try:
      movie.update()
      return jsonify({
        'success': True,
        'movie': [movie.format()]
        }), 200
    except:
      abort(404)

  # Setup endpoint to hand the DELETE requests.
  # DELETE method specified.
  @app.route('/movies/<int:id>', methods=['DELETE'])
  @requires_auth('delete:movies')
  def delete_movie(jwt, id):

    movie = Movies.query.get(id)

    # Return a 404 error if no movie.
    if movie is None:
      abort(404)
    
    try:
      movie.delete()
      return jsonify({
        'success': True,
        'delete': movie.id
        }), 200
    except:
      abort(404)

  # Actor endpoints.
  # Setup endpoint to handle the GET requests.
  # GET method not specified as it is the default method.
  @app.route('/actors')
  @requires_auth('get:actors')
  def get_actors(jwt):

    # Query to retrieve all actors.
    actors = Actors.query.order_by(Actors.id).all()

    # Format & return results on success
    try:
      return jsonify({
        'success': True,
        'actors': [actor.format() for actor in actors]
        }), 200
    except:
      abort(404)

  # Setup endpoint to handle the POST requests.
  # POST method specified.
  @app.route('/actors', methods=['POST'])
  @requires_auth('post:actors')
  def post_actor(jwt):

    # get response data
    data = request.get_json()
    name = data.get('name', None)
    age = data.get('age', None)
    gender = data.get('gender', None)

    # Insert new actor details to the DB.
    try:
      actor = Actors(name=name, age=age, gender=gender)
      actor.insert()
      return jsonify({
        'success': True,
        'movie': actor.format()
        }), 201
    except:
      abort(500)
  
  # Setup endpoint to hand the PATCH requests.
  # PATCH method specified.
  @app.route('/actors/<id>', methods=['PATCH'])
  @requires_auth('patch:actors')
  def patch_movie(jwt, id):

    data = request.get_json()
    name = data.get('name', None)
    age = data.get('age', None)
    gender = data.get('gender', None)

    actor = Actors.query.get(id)

    # Return a 404 error if no actor.
    if actor is None:
      abort(404)
    
    # Return a 400 error if there is no name, age or gender.
    if name is None or age is None or gender is None:
      abort(400)
    
    actor.name = name
    actor.age = age
    actor.gender = gender

    # Try to update actor details in the DB.
    try:
      actor.update()
      return jsonify({
        'success': True,
        'movie': [actor.format()]
        }), 200
    except:
      abort(404)

  # Setup endpoint to hand the DELETE requests.
  # DELETE method specified.
  @app.route('/actors/<int:id>', methods=['DELETE'])
  @requires_auth('delete:actors')
  def delete_actor(jwt, id):

    actor = Actors.query.get(id)

    # Return a 404 error if no movie.
    if actor is None:
      abort(404)
    

    try:
      actor.delete()
      return jsonify({
        'success': True,
        'delete': actor.id
        }), 200
    except:
      abort(404)

  # Error Handling
  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message": "unprocessable"
      }), 422

  return app

APP = create_app()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)
