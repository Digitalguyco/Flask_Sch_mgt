import unittest
from .. import create_app
from ..config.config import config_dict
from ..utils import db
from ..models import Student


class TestAuth(unittest.TestCase):
  
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

    def test_create_student(self):
        data = {
            "full_name": "Test Student",
            "email": "test@mail.com",
            "password": "test123"
        }

        response = self.client.post('/auth/register', json=data)

        self.assertEqual(response.status_code, 201)

        self.assertEqual(response.json['message'], 'User created successfully')

        student = Student.query.filter_by(email=data['email']).first()

        self.assertIsNotNone(student)

    
    def test_login_student(self):
        data = {
            "email": "test@mail.com",
            "password": "test123"
        }

        response = self.client.post('/auth/login', json=data)

        assert response.status_code == 200

    




