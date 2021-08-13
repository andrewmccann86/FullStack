import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [questions.format() for questions in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # Create and configure the app.
    app = Flask(__name__)
    setup_db(app)


    '''
    DONE: Set up CORS. Allow '*' for origins.
    Delete the sample route after completing the TODOs
    '''

    # Set up CORS. Allow '*' for origins.
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    '''
    DONE: Use the after_request decorator to set Access-Control-Allow
    '''

    # After_request decorator setup for GET, POST, PATCH, DELETE & OPTIONS methods.


    @app.after_request
    def after_request(response):
      response.headers.add(
        'Access-Control-Allow-Headers',
        'Content-Type, Authorisation, true')
      response.headers.add(
        'Access-Control-Allow-Methods',
        'GET, POST, PATCH, DELETE, OPTIONS')
      return response

    '''
    DONE: Create an endpoint to handle GET requests for all available categories.
    '''


    # Categorires endpoint for get requests.
    # Method not specified as GET is used by default.
    @app.route('/categories')
    def retrieve_categories():
      categories = Category.query.order_by(Category.id).all()
    
      return jsonify({
        'success': True,
        # Ensure correct formatting for categories to match front end.
        'categories': {category.id: category.type for category in categories}
        }), 200

    '''
    DONE:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    10 questions per page & pagination at the bottom of the screen for 3 pages.
    Clicking on the page numbers should update the questions.
    '''

    # Questions endpoint for get requests.
    # Method not specified as GET is used by default.


    @app.route('/questions')
    def retrieve_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        categories = Category.query.order_by(Category.id).all()

        # Return a 404 error if there are no questions for the page number.
        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(Question.query.all()),
            # Ensure correct formatting for categories to match front end.
            'categories': {category.id: category.type for category in categories},
            'current_category': None
            }), 200

    '''
    DONE:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, it will be removed.
    This removal will persist in the database and when you refresh the page.
    '''

    # Endpoint created to handle DELETE requests
    # by using the ID given as a URL parameter with the DELETE method specified.


    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):

        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
              'success': True,
              'deleted': question_id,
              'questions': current_questions,
              'total_questions': len(Question.query.all())
              }), 200

        except:
            abort(422)

    '''
    DONE:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    '''

    # Post endpoint created to handle posting a new question.
    # POST method specified.


    @app.route('/questions', methods=['POST'])
    def create_question():

        # Get json data from request.
        data = request.get_json()

        # Get individual data pieces from the json data.
        new_question = data.get('question', None)
        new_answer = data.get('answer', None)
        new_category = data.get('category', None)
        new_difficulty = data.get('difficulty', None)

        try:
            # Create a new question instance.
            question = Question(
                question=new_question, answer=new_answer,
                category=new_category, difficulty=new_difficulty)
            # Insert question into the DB.
            question.insert()

            return jsonify({
                'success': True,
                'created': question.id,
                'total_questions': len(Question.query.all())
              }), 200

        except:
            abort(422)

    '''
    DONE:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    '''


    @app.route('/questions/search', methods=['POST'])
    def search_questions():

        # Get the search term.
        data = request.get_json()
        search_term = data.get('searchTerm', '')

        # Abort & return a 422 status code if an empty search term is used.
        if search_term == '':
            abort(422)

        try:
            results = Question.query.filter(
                Question.question.ilike('%{}%'.format(search_term))).all()

            # If there are no questions returned from the search
            # Abort & return a 404 error.
            if len(results) == 0:
                abort(404)

            paginated_questions = paginate_questions(request, results)

            # Response return on success.
            return jsonify({
                'success': True,
                'questions': paginated_questions,
                'total_questions': len(results),
                'current_category': None
                }), 200

        except:
            abort(404)

    '''
    DONE: Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''

    # Method not specified as GET is used by default.


    @app.route('/categories/<int:category_id>/questions')
    def questions_by_category(category_id):

        # Get the category by id
        category = Category.query.get(category_id)
        # Abort & return a 422 status code if category id is not found.
        if category is None:
            abort(422)

        try:
            # Get questions where cateogry id's match between tables.
            questions = Question.query.filter(
                Question.category == category_id).all()
            paginated_questions = paginate_questions(request, questions)

            return jsonify({
                'success': True,
                'questions': paginated_questions,
                'total_questions': len(questions),
                'category': category_id
                }), 200

        except:
            abort(404)

    '''
    DONE:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    '''


    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        data = request.get_json()
        quiz_category = data.get('quiz_category', None)
        previous_questions = data.get('previous_questions', None)

        #  if there are no questions returned from the search
        # Abort & return a 404 error.
        if ((quiz_category is None) or (previous_questions is None)):
            abort(404)

        try:
            # If default value of category is given
            # return all questions not in previous questions.
            # Else return questions filtered by category
            # that are not in previous questions.
            if quiz_category['id'] == 0:
                questions_query = Question.query.filter(
                    Question.id.notin_(previous_questions)).all()
            else:
                questions_query = Question.query.filter(
                    Question.category == quiz_category['id'],
                    Question.id.notin_(previous_questions)).all()

            questions = [question.format() for question in questions_query]

            if len(questions) == 0:
                return jsonify({
                    'success': True,
                    'question': None
                    }), 200

            # Selects a random question from the questions logic above
            random_question = random.choice(questions)

            if random_question:
                return jsonify({
                    'success': True,
                    'question': random_question
                    }), 200

        except:
            abort(422)

    '''
    DONE:
    Create error handlers for all expected errors
    including 404 and 422.
    '''

    # Error code 400 handler created.


    @app.errorhandler(400)
    def bad_request(error):

        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad request.'
            }), 400

    # Error code 404 handler created.


    @app.errorhandler(404)
    def not_found(error):

        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Not found.'
            }), 404

    # Error code 422 handler created.


    @app.errorhandler(422)
    def unprocessable(error):

        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable entity.'
            }), 422

    return app
