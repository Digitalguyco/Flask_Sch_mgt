from flask import request
from flask_restx import Namespace, Resource, fields, reqparse
from http import HTTPStatus
from ..models import Admin, Course, Enrollment, Student
from ..utils import db
from flask_jwt_extended import jwt_required, get_jwt_identity

#  Enrollments API endpoints


# Enrollment namespace
enrollment_namespace = Namespace('enrollments', description='Enrollment operations')

# Grade model or Enrollment model
grade_model = enrollment_namespace.model('Grade', {
    'id': fields.Integer(readOnly=True),
    'student_id': fields.Integer(required=True),
    'course_id': fields.Integer(required=True),
    'grade': fields.Float(required=True),
})

#  add_grade_parser is used to parse the request body
add_grade_parser = reqparse.RequestParser()
add_grade_parser.add_argument('student_id', type=int, required=True, location='json')
add_grade_parser.add_argument('course_id', type=int, required=True, location='json')
add_grade_parser.add_argument('grade', type=float, required=True, location='json')


#  Enroll a student to a course API endpoint can be accessed by a particular student or admin
@enrollment_namespace.route('/enroll/<int:student_id>/<int:course_id>')
@enrollment_namespace.response(HTTPStatus.NO_CONTENT, 'Enrolled')
class EnrollCourse(Resource):
    def post(self, student_id, course_id):
        '''
        Enroll a student to a course

        '''

        # Check if student and course exist
        student = Student.query.filter_by(id=student_id).first()
        course = Course.query.filter_by(id=course_id).first()

        if not student or not course:
            return {'message': 'Student or course not found'}, HTTPStatus.NOT_FOUND

        # Check if student is already enrolled in the course
        if student in course.students:
            return {'message': 'Student is already enrolled in the course'}, HTTPStatus.CONFLICT

        # Enroll student to course
        course.students.append(student)
        db.session.commit()

        # create enrollment
        enrollment = Enrollment(student_id=student_id, course_id=course_id)
        db.session.add(enrollment)
        db.session.commit()

      
        return {'message': 'Student enrolled in the course successfully'}, HTTPStatus.OK




# Unenroll a student from a course API endpoint can be accessed by a particular student or admin
@enrollment_namespace.route('/unenroll/<int:student_id>/<int:course_id>')
@enrollment_namespace.response(HTTPStatus.NO_CONTENT, 'Unenrolled')
class UnEnroll(Resource):
    def delete(self, student_id, course_id):
        '''
        Unenroll a student from a course

        '''

        # Check if student and course exist
        student = Student.query.filter_by(id=student_id).first()
        course = Course.query.filter_by(id=course_id).first()

        if not student or not course:
            return {'message': 'Student or course not found'}, HTTPStatus.NOT_FOUND

        # Check if student is enrolled in the course
        if student in [enrollment.student for enrollment in course.enrollments]:
            return {'message': 'Student is not enrolled in the course'}, HTTPStatus.CONFLICT

        # Unenroll student from course
        course.students.remove(student)
        db.session.commit()

        # delete enrollment
        enrollment = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
        db.session.delete(enrollment)
        db.session.commit()


        return {'message': 'Student unenrolled from the course successfully'}, HTTPStatus.OK 
    

# Add grade to a student API endpoint can be accessed by admin only
@enrollment_namespace.route('/add-grade')
class AddGradeResource(Resource):
    @enrollment_namespace.expect(add_grade_parser)
    @enrollment_namespace.response(HTTPStatus.OK, 'Grade added')
    @jwt_required()
    def post(self):
        """
        Add grade to a student
            by admin only
        """
        args = add_grade_parser.parse_args()
        student_id = args['student_id']
        course_id = args['course_id']
        grade = args['grade']

        # Check if admin
        admin_id = get_jwt_identity()

        admin = Admin.query.filter_by(id=admin_id).first()

        if not admin:
            return {'message': 'Admin not found'}, HTTPStatus.NOT_FOUND
        
        if not admin.is_active:
            return {'message': 'Admin is not active'}, HTTPStatus.FORBIDDEN
        


        # Check if student and course exist
        enrollment = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()


    

        if not enrollment:
            return {'message': 'Student is not enrolled in the course'}, HTTPStatus.NOT_FOUND

        if grade < 0.0 or grade > 5.0:
            return {'message': 'Invalid grade'}, HTTPStatus.BAD_REQUEST

        enrollment.grade = grade
        db.session.commit()

        return {"message": "graded added"}, HTTPStatus.OK
    