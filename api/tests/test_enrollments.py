import unittest
from .. import create_app
from ..config.config import config_dict
from ..utils import db
from ..models import Enrollment

#  Code For Testing Enrollments

class TestEnrollment(unittest.TestCase):

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


    def test_create_enrollment(self):

        '''
        Test for creating an enrollment
        
        '''
        data = {
            "course_id": 1,
            "student_id": 1,
        }

        response = self.client.post('/enrollments/enroll/{}/{}'.format(data['student_id'], data['course_id']))

        self.assertEqual(response.status_code, 201)


        enrollment = Enrollment.query.filter_by(course_id=data['course_id']).first()

        self.assertIsNotNone(enrollment)
        
    def test_get_enrollments(self):

        '''
            Test for getting all enrollments
        '''
        response = self.client.get('/enrollments/')

        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.json['enrollments']), 1)

    def test_unenroll(self):
        '''
            Test for unenrolling a student from a course
        '''
        response = self.client.delete('/enrollments/unenroll/1/1')

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.json['message'], 'Unenrolled successfully')

        enrollment = Enrollment.query.filter_by(course_id=1).first()

        self.assertIsNone(enrollment)


    