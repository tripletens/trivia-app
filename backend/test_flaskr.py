import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import setup_db, Question, Category
from settings import DB_NAME, DB_USER, DB_PASSWORD


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(DB_USER, DB_PASSWORD, 'localhost:5432', self.database_name)
        # self.database_path = "postgres://{}/{}".format('localhost:5432', )
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    
    def test_paginate_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        

    def test_404_invalid_page_numbers(self):
        res = self.client().get('/questions?page=10000')
        data = json.loads(res.data)
        
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "unprocessable entity")
        self.assertEqual(res.status_code, 422)
       
    
    def test_delete_questions(self):
        res = self.client().delete('questions/17')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question_id'], 17)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['question'])
        
    def test_404_question_deletion_error(self):
        res = self.client().delete('questions/98888')
        data = json.loads(res.data)
        
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")
        self.assertEqual(res.status_code, 404)
        
        
    def test_404_question_search_parameter_doesnt_exist(self):
        res = self.client().delete('questions/search', json={"searchTerm": ""})
        data = json.loads(res.data)
        
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")
        self.assertEqual(res.status_code, 404)
        
    def search_question(self):
        res = self.client().post('questions/search', json={"searchTerm": "title"})
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_404_invalid_search_input(self):
        res = self.client().post('questions/search', json={"searchTerm": "Juice"})
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], "resource not found")

    def test_create_question(self):
        new_question = {
        'question': 'What is the color of rice logo?',
        'answer': 'red and yellow',
        'category': "1",
        'difficulty': "2",
        }

        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        
    
    def test_422_cannot_create_question(self):
        bad_question = {
        'question': 'What is the day after Sunday?',
        'category': '1',
        'answer':'',
        'difficulty': 1,
        }

        res = self.client().post('/questions', json=bad_question)
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], "unprocessable entity")

    def test_404_category_input_out_of_range(self):
        res = self.client().get('categories/100/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    def test_play_quiz(self):
        input_data = {
            'previous_questions':[2, 6],
            'quiz_category': {
                'id': 5,
                'type': 'Entertainment'
            }
        }
        res = self.client().post('/quizzes', json=input_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

        self.assertNotEqual(data['question']['id'], 2)
        self.assertNotEqual(data['question']['id'], 6)

        self.assertEqual(data['question']['category'], 5)



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()