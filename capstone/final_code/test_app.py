import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, Movies, Actors

class CastingAgencyTestCase(unittest.TestCase):
    # Class represents the  Casting Agency Test Case.

    def setUp(self):
        # Define test variables & initialise the app.

        self.ASSISTANT_TOKEN = os.environ['ASSISTANT_TOKEN']
        self.DIRECTOR_TOKEN = os.environ['DIRECTOR_TOKEN']
        self.PRODUCER_TOKEN = os.environ['PRODUCER_TOKEN']

        self.token_assistant = {'Content-Type': 'application/json', 'Authorization': 'Bearer{}'.format(self.ASSISTANT_TOKEN)}
        self.token_director = {'Content-Type': 'application/json', 'Authorization': 'Bearer{}'.format(self.DIRECTOR_TOKEN)}
        self.token_producer = {'Content-Type': 'application/json', 'Authorization': 'Bearer{}'.format(self.PRODUCER_TOKEN)}
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "agency_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format('postgres', 'ph33rth33v1l','localhost:5432', self.database_name)

        setup_db(self.app, self.database_path)

        # Binds the app to the current context.
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # Create all tables.
            self.db.create_all()

    def tearDown(self):
        # Executed after each test.
        pass

    # Movie endpoints.
    # Test created for get_movies.
    def test_get_movies(self):
        movie = Movies(title='Akira', release_date='25-01-1991')
        movie.insert()
        res = self.client().get('/movies', headers=self.token_producer)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movies'])
    
    # Test created for get_movies failure.
    def test_get_movies_fail(self):
        res = self.client().get('/movies')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)

    # Test created for post_movie.
    def test_post_movie(self):
        res = self.client().post('/movies', headers=self.token_producer, json={'title': 'The Matrix', 'release_date': '11-06-1999'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movies'])
    
    # Test created for post_movie failure.
    def test_post_movie_failure(self):
        res = self.client().post('/movies', headers=self.token_assistant, json={'title': 'The Matrix', 'release_date': '11-06-1999'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
    
    # Test created for edit_movie
    def test_edit_movie(self):
        movie = Movies(title='Star Wars', release_date='27-12-77 12:00 pm')
        movie.insert()
        movie_id = movie.id
        res = self.client().patch('/movies/'+str(movie_id) + '', headers=self.token_director, json={'title': 'Star Wars: A New Hope', 'release_date': '27-12-1977'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movies'])
    
    # Test created for edit_movie failure.
    def test_edit_movie_failure(self):
        movie = Movies(title='Star Wars', release_date='27-12-77 12:00 pm')
        movie.insert()
        movie_id = movie.id
        res = self.client().patch('/movies/'+str(movie_id) + '', headers=self.token_assistant, json={'title': 'Star Wars: A New Hope', 'release_date': '27-12-1977'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movies'])
    
    # Test created for delete_movie.
    def test_delete_movie(self):
        movie = Movies(title='Akira', release_date='25-01-1991')
        movie.insert()
        movie_id = movie.id
        res = self.client().delete('/movies/'+str(movie_id) + '', headers=self.token_producer)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['delete'])
    
    # Test for delete_movie failure.
    def test_delete_movie_failure(self):
        res = self.client().delete('/movies/1234', headers=self.token_producer)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    # Actor Endpoints
    # Test created for get_actors.
    def test_get_actors(self):
        actor = Actors(name='Keanu Reeves', age=57, gender='Male')
        actor.insert()
        res = self.client().get('/actors', headers=self.token_producer)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actors'])
    
    # Test created for get_actors failure.
    def test_get_actors_fail(self):
        res = self.client().get('/actors')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)

    # Test created for post_actor.
    def test_post_actor(self):
        res = self.client().post('/actors', headers=self.token_producer, json={'name': 'Hugo Weaving', 'age': 61, 'gender': 'Male'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actors'])
    
    # Test created for post_actor failure.
    def test_post_actor_failure(self):
        res = self.client().post('/actors', headers=self.token_assistant, json={'name': 'Hugo Weaving', 'age': 61, 'gender': 'Male'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
    
    # Test created for edit_actor
    def test_edit_actor(self):
        actor = Actors(name='Scarlett Johansson', age=36, gender='Female')
        actor.insert()
        actor_id = actor.id
        res = self.client().patch('/actors/'+str(actor_id) + '', headers=self.token_director, json={'name': 'Scarlett Johansson', 'age': 36, 'gender': 'Female'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actors'])
    
    # Test created for edit_actor failure.
    def test_edit_actor_failure(self):
        actor = Actors(name='Scarlett Johansson', age=36, gender='Female')
        actor.insert()
        actor_id = actor.id
        res = self.client().patch('/actors/'+str(actor_id) + '', headers=self.token_assistant, json={'name': 'Scarlett Johansson', 'age': 36, 'gender': 'Female'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actors'])
    
    # Test created for delete_actor.
    def test_delete_actor(self):
        actor = Actors(name='Scarlett Johansson', age=36, gender='Female')
        actor.insert()
        actor_id = actor.id
        res = self.client().patch('/actors/'+str(actor_id) + '', headers=self.token_producer)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['delete'])
    
    # Test for delete_actor failure.
    def test_delete_actor_failure(self):
        res = self.client().delete('/actors/1234', headers=self.token_producer)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)


if __name__ == "__main__":
    unittest.main()