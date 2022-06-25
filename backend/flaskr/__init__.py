from crypt import methods
from inspect import Parameter
import os
import random
from sre_constants import SUCCESS
from tkinter import EXCEPTION
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS


from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app, resources={r"/*": {"origins": "*"}})
    
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    """
    
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def fetch_all_categories():
        try:
            categories = Category.query.all()
            all_categories = {
                category.id: category.type for category in categories}

            return jsonify({
                'success': True,
                'categories': all_categories
            })
        except EXCEPTION:
            abort(500)
    
    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
    """
    
    @app.route('/questions', methods=['GET'])
    def get_questions():
        try:
            page = request.args.get('page', 1, type=int)
            questions = Question.query.all()
            total_questions = len(questions)
        
            start = (page - 1) * 10
            end = start + 10
            formatted_questions = [question.format() for question in questions]

            # if the page number is not found
            if (len(formatted_questions[start:end]) == 0):
                abort(404)

            categories = Category.query.all()
            formatted_category = [singleCat.type for singleCat in categories]
            current_category = None

            if (len(formatted_category) == 0):
                abort(404)

            return jsonify({
                'success': True,
                'questions': formatted_questions[start:end],
                'total_questions':  total_questions,
                'categories': formatted_category,
                'current_category': current_category,
            }), 200

        except Exception as e:
            print(e)
            abort(422)
    """
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        try:
            question = Question.query.filter(
                Question.id == id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            questions = Question.query.all()
            total_questions = len(questions)

            return jsonify({
                'success': True,
                'question_id': id,
                'total_questions': total_questions,
                'question': question.format(),
            })
        except:
            abort(404)
    """
    @DONE:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def create_question():
        # load request body and data
        body = request.get_json()

        if not ('question' in body and 'answer' in body and
                'difficulty' in body and 'category' in body):
            abort(422)

        question_title = body.get('question')
        question_answer = body.get('answer')
        question_difficulty = body.get('difficulty')
        question_category = body.get('category')
        
        
        # ensure all fields are filled
        if ((question_title is None) or (question_answer is None) or
                (question_difficulty is None) or (question_category is None)):
            abort(422)

        # create new question
        question = Question(
            question=question_title,
            answer=question_answer,
            difficulty=question_difficulty,
            category=question_category
        )

        question.insert()

        # get all questions and paginate
        questions = Question.query.all()
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * 10
        end = start + 10
        formatted_questions = [question.format() for question in questions]
        total_questions = len(questions)

        if(len(formatted_questions[start:end]) == 0):
            abort(404)
                
        return jsonify({
            'success': True,
            'question_id': question.id,
            'question_created': question.question,
            'questions': formatted_questions[start:end],
            'total_questions': total_questions
        })
       
    """
    @DONE:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        # Get user input
        body = request.get_json()
        search_parameter = body.get('searchTerm')

        # If a search term has been entered, apply filter for question string
        # and check if there are results
        try:
            if search_parameter:
                search_results = Question.query.filter(Question.question.ilike
                                                       (f'%{search_parameter}%')).all()

                page = request.args.get('page', 1, type=int)
                start = (page - 1) * 10
                end = start + 10
                questions = Question.query.all()
                formatted_questions = [question.format()
                                       for question in search_results]
                if (len(formatted_questions[start:end]) == 0):
                    abort(404)
                
                return jsonify({
                    'success': True,
                    'questions':  formatted_questions[start:end],
                    'total_questions': len(questions),
                    'current_category': None
                })
            else:
                abort(422)
        except:
            abort(404)

    """
    @DONE:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:id>/questions')
    def get_category_questions(id):
        # Get category by id, try get questions from matching category
        category = Category.query.filter_by(id=id).one_or_none()

        try:
            # get questions matching the category
            result = Question.query.filter_by(category=category.id).all()
            # print({result})
            # paginate the result questions
            page = request.args.get('page', 1, type=int)
            start = (page - 1) * 10
            end = start + 10
            questions = Question.query.all()
            formatted_questions = [question.format() for question in result]

            return jsonify({
                'success': True,
                'questions': formatted_questions[start:end],
                'total_questions': len(questions),
                'current_category': category.type
            })
        except:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def get_quiz_questions():
        # Get user input
        body = request.get_json()
        previous_questions = body.get('previous_questions')
        quiz_category = body.get('quiz_category')
        questions = Question.query.all()

        # If a category has been selected, get questions from matching category
        # If no category has been selected, get all questions
        try:
            if quiz_category:
                result = Question.query.filter_by(category=quiz_category['id']).filter(
                    Question.id.notin_(previous_questions)).all()
            else:
                result = Question.query.filter(
                    Question.id.notin_(previous_questions)).all()

            # get a random question from the result
            next_question = random.choice(result)
            # check if we have exhausted the questions
            # next_question = get_random_question()

            # used = False
            # if next_question['id'] in previous_questions:
            #     used = True

            # while used:
            #     next_question = random.choice(questions).format()

            #     if (len(previous_questions) == len(questions)):
            #         return jsonify({
            #             'success': True,
            #             'message': "game over"
            #         }), 200

            return jsonify({
                'success': True,
                'question': next_question.format()
            })
        # if user selected a category
        # if previous_questions['id'] != 0:
        #     questions = Question.query.filter_by(
        #         category=previous_questions['id']).all()
        # # if user selected "All"
        # else:
        #     questions = Question.query.all()

        # def get_random_question():
        #     next_question = random.choice(questions).format()
        #     return next_question

        # next_question = get_random_question()

        # used = False
        # if next_question['id'] in previous_questions:
        #     used = True

        # while used:
        #     next_question = random.choice(questions).format()

        #     if (len(previous_questions) == len(questions)):
        #         return jsonify({
        #             'success': True,
        #             'message': "game over"
        #         }), 200

        # return jsonify({
        #     'success': True,
        #     'question': next_question
        # }), 200
        # except:
        #     abort(400)

        except:
            abort(400)
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": 'unprocessable entity'
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500
    return app
