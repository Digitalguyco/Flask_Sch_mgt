import unittest
from .. import create_app
from ..config.config import config_dict
from ..utils import db
from ..models import Admin



class TestAuthAdmin(unittest.TestCase):

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

        
    def test_login_admin(self):
        data = {
            "username": "Test Admin",
            "password": "test123",
        }

        response = self.client.post('/auth/login', json=data)

        assert response.status_code == 200

    