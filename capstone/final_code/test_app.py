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

        ASSISTANT_TOKEN = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InExeUFNVDZiMVJYcDVHVHdGU3B2eiJ9.eyJpc3MiOiJodHRwczovL2Rldi0wMmxucXV1dy5ldS5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjEzYjUyNjdjNTQzNTYwMDZiNTEzOWIzIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYzMTI3Nzg4NCwiZXhwIjoxNjMxMjg1MDg0LCJhenAiOiJTVEZVc1NUWmJPMFg2bXFZQ1VhbDVwbFhqTWlTNFJ6bSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiXX0.sRzRHD6ZkveM9aIMW_lB2LQZcsUpKfaSE94vKXaHm79iN5-FlO8cl6wAJW-8USq01flqHP_nEs4iA4AGLwebSXdGcnfSJMZih4n987_HloenJYc8hQcV547T8fIpYC62GIcqTlnP5inVzxxkLDymVFQjmBTcmrqi_TqvG5rGkb3zyPZw1WgHiYabQcS-r3gfKxlot-VJAGvKVl3hYZ8SqC_zoe44Yr2j2mAlypGyVvMnG7gRpVh_J4uoJyfN-u_cIekV5hpAf-o0yHrzvnoLFt3fW5w6Pzil8YcPlvoGGuF7PRVcp_XpBus-KbMNdFGKnLtlei_z8fh5EyAHQxNONg'
        DIRECTOR_TOKEN = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InExeUFNVDZiMVJYcDVHVHdGU3B2eiJ9.eyJpc3MiOiJodHRwczovL2Rldi0wMmxucXV1dy5ldS5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjEzYjUyOTFjNTQzNTYwMDZiNTEzOWM2IiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYzMTI3ODI5MCwiZXhwIjoxNjMxMjg1NDkwLCJhenAiOiJTVEZVc1NUWmJPMFg2bXFZQ1VhbDVwbFhqTWlTNFJ6bSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImdldDphY3RvcnMiLCJnZXQ6bW92aWVzIiwicGF0Y2g6YWN0b3JzIiwicGF0Y2g6bW92aWVzIiwicG9zdDphY3RvcnMiXX0.lalUTy1xeF71PBd4fM6CM1ub4MyQALx8NmahCW8xRQP6BCUvdZNNW-4RTMRPCUk1JOQfj-Jv8NuYnyugoBALTkywUnyIzZSY7FiWsk6m7MTYq1QjCEJIb8t_a2d3fNKaj62MFmxh4WN8E4LdWNkgfyjByb3aEUsNmuWJLP9z4COi7lMsuJ678nUGM8YQDq3QsncfoS2_f1rWjwSByFwf5UZHl-cSTc7qfoJSwEvkcO5m1vl47ubTFo9D7ZL9Ea17te9yzYB9TsaATTgP6Gc5V1RxOxOBmgaDyJwygRFJylexZjjjrbEr8550FqSruGsHR--c2Wov5Ich71AAu-yGrg'
        PRODUCER_TOKEN = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InExeUFNVDZiMVJYcDVHVHdGU3B2eiJ9.eyJpc3MiOiJodHRwczovL2Rldi0wMmxucXV1dy5ldS5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjEzYjUyYmFlZWMyZGMwMDY5MTA4NzBlIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYzMTI3ODQ4NiwiZXhwIjoxNjMxMjg1Njg2LCJhenAiOiJTVEZVc1NUWmJPMFg2bXFZQ1VhbDVwbFhqTWlTNFJ6bSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImRlbGV0ZTptb3ZpZXMiLCJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyIsInBhdGNoOmFjdG9ycyIsInBhdGNoOm1vdmllcyIsInBvc3Q6YWN0b3JzIiwicG9zdDptb3ZpZXMiXX0.rHW9p1kr-jgOIsRcCBLiUw4F3TPUyylJb98zyedvSxCNCVggvNGiMcXSXy_CNUHtFrfp9-ewY0CkRXRhtr0ix5GhMbRqKPfwIj6M3LZgFkrC5DrEh2Mhz22p_p2A3kMxwGG3oB2rQRB6QvRzav10Q3A02gQw_TunMG8cldCtzXhwc6EariWpkodlSumdgyrZU-ipG07cu4xcixqW4OymJjMVlD7sk0ElsisB8LG3lKq4NUMxz7Fs913Eqp6QUBN165ADwMGn2G15CpaSpeasu65IVuXF0UVXm2-EL2YoI1oTEcs7PxRabkQgQge7-YxoO47hZbn-u-A5D_R685RxdA'

        self.token_assistant = {'Content-Type': 'application/json', 'Authorization': ASSISTANT_TOKEN}
        self.token_director = {'Content-Type': 'application/json', 'Authorization': DIRECTOR_TOKEN}
        self.token_producer = {'Content-Type': 'application/json', 'Authorization': PRODUCER_TOKEN}
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
        movie = Movies(title='Akira', release_date='25-01-91 12:00 pm')
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
        res = self.client().get('/movies', headers=self.token_producer, json={'title': 'The Matrix', 'release_date': '11-06-99 12:00 pm'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movies'])
    
    # Test created for post_movie failure.
    def test_post_movie_failure(self):
        res = self.client().get('/movies', headers=self.token_assistant, json={'title': 'The Matrix', 'release_date': '11-06-99 12:00 pm'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
    
    # Test created for edit_movie
    def test_edit_movie(self):
        movie = Movies(title='Star Wars', release_date='27-12-77 12:00 pm')
        movie.insert()
        movie_id = movie.id
        res = self.client().patch('/movies/'+str(movie_id) + '', headers=self.token_director, json={'title': 'Star Wars: A New Hope', 'release_date': '27-12-77 12:00pm'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movies'])
    
    # Test created for edit_movie failure.
    def test_edit_movie_failure(self):
        movie = Movies(title='Star Wars', release_date='27-12-77 12:00 pm')
        movie.insert()
        movie_id = movie.id
        res = self.client().patch('/movies/'+str(movie_id) + '', headers=self.token_assistant, json={'title': 'Star Wars: A New Hope', 'release_date': '27-12-77 12:00pm'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movies'])
    
    # Test created for delete_movie.
    def test_delete_movie(self):
        movie = Movies(title='Akira', release_date='25-01-91 12:00 pm')
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
        res = self.client().get('/actors', headers=self.token_producer, json={'name': 'Hugo Weaving', 'age': 61, 'gender': 'Male'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actors'])
    
    # Test created for post_actor failure.
    def test_post_actor_failure(self):
        res = self.client().get('/actors', headers=self.token_assistant, json={'name': 'Hugo Weaving', 'age': 61, 'gender': 'Male'})
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