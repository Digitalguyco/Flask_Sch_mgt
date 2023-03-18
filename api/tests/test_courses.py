import unittest
from .. import create_app
from ..config.config import config_dict
from ..utils import db
from ..models import Course


class TestCourse(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config=config_dict['test'])

        self.appctx = self.app.app_context()

        self.appctx.push()

        self.client = self.app.test_client()

        db.create_all()



    def tearDown(self):
        db.drop_all()

        self.appctx.pop()

        self.app = None

        self.client = None


    def test_create_course(self):
        data = {
            "name": "Test Course",
            "description": "Test Course Description",
            "credit": 3,
            "lecturer": "Test Lecturer",
        }

        response = self.client.post('/courses/', json=data)

        self.assertEqual(response.status_code, 201)

        self.assertEqual(response.json['message'], 'Course created successfully')

        course = Course.query.filter_by(name=data['name']).first()

        self.assertIsNotNone(course)

    def test_get_courses(self):
        response = self.client.get('/courses/')

        self.assertEqual(response.status_code, 200)


        self.assertEqual(len(response.json['courses']), 1)

    def test_get_course(self):
        response = self.client.get('/courses/course/1')

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.json['course']['name'], 'Test Course')