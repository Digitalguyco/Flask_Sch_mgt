from flask_restx import Namespace, Resource, fields
from ..models import Course, Admin
from ..utils import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import NotFound, MethodNotAllowed
from http import HTTPStatus

# Course Endpoint

# Course Namespace
course_namespace = Namespace('courses', description='Courses related operations')

# Course Model or Schema
course_model = course_namespace.model('Course', {
    'id': fields.String(required=True, description='Course id'),
    'name': fields.String(required=True, description='Course name'),
    'description': fields.String(required=True, description='Course description'),
    'credits': fields.Integer(required=True, description='Course credits'),
    'lecturer': fields.String(required=True, description='Course lecturer'),
    'students': fields.List(fields.String, required=True, description='Course students'),
})


# Course Get and Create to get all courses and create a new course 
@course_namespace.route('/')
class CourseGetCreate(Resource):
    # Get all courses
    @course_namespace.doc('get_courses')
    @course_namespace.marshal_list_with(course_model)
    @jwt_required()
    def get(self):
        '''
        Get all courses
        
        '''
        return Course.get_all(), HTTPStatus.OK
    
    # Create a new course by admin only
    @course_namespace.doc('create_course')
    @course_namespace.expect(course_model)
    @course_namespace.response(HTTPStatus.CREATED, 'Course created')
    @jwt_required()
    def post(self):
        '''
        
        Create a new course
            by admin only
        
        '''

        
        user_jwt = get_jwt_identity()


        current_user = Admin.query.filter_by(id=user_jwt).first()

        if not current_user:
            return{'message': 'You are not authorized to perform this action'},  HTTPStatus.UNAUTHORIZED


        
        data = course_namespace.payload
        new_course = Course(
            name=data['name'],
            description=data['description'],
            lecturer=data['lecturer'],
            credits=data['credits'],
        )


        new_course.save()

        return {'message': 'Course created successfully'}, HTTPStatus.CREATED


# Course Get, Update and Delete to get a course, update a course and delete 
@course_namespace.route('/course/<int:course_id>')
class CourseGetUpdateDelete(Resource):
    # Get a course by id
    @course_namespace.doc('get_course')
    @course_namespace.marshal_with(course_model)
    @jwt_required()
    def get(self, course_id):
        """
        Get a course
        """
        user_jwt = get_jwt_identity()
        
        if not user_jwt:
            return {'message': 'User not found'}, HTTPStatus.NOT_FOUND
        
        course = Course.query.get_or_404(course_id)
        return course, HTTPStatus.OK
    
    # Update a course by admin only
    @course_namespace.doc('update_course')
    @course_namespace.expect(course_model)
    @course_namespace.response(HTTPStatus.OK, 'Course updated')
    @jwt_required()
    def put(self, course_id):
        """
        Update a course
         by admin only
        """
        user_jwt = get_jwt_identity()
        
        if not user_jwt:
            return {'message': 'User not found'}, HTTPStatus.NOT_FOUND

        current_user = Admin.query.filter_by(id=user_jwt).first()

        if not current_user:
            return {'message': 'You are not authorized to perform this action'}, HTTPStatus.UNAUTHORIZED


        
        course = Course.query.get_or_404(course_id)
        data = course_namespace.payload
        course.name = data['name']
        course.description = data['description']
        course.lecturer = data['lecturer']
        course.credits = data['credits']
        course.save()

        return {'message': 'Course updated successfully'}, HTTPStatus.OK
    
    # Delete a course by admin only
    @course_namespace.doc('delete_course')
    @course_namespace.response(HTTPStatus.NO_CONTENT, 'Course deleted')
    @jwt_required()
    def delete(self, course_id):
        """
        Delete a course
        by admin only
        """
        user_jwt = get_jwt_identity()
        
        if not user_jwt:
            return {'message': 'User not found'}, HTTPStatus.NOT_FOUND

        current_user = Admin.query.filter_by(id=user_jwt).first()

        if not current_user:
            return {'message': 'You are not authorized to perform this action'}, HTTPStatus.UNAUTHORIZED

        
        Course.delete_by_id(course_id)
        return {'message': 'Course deleted successfully'}, HTTPStatus.NO_CONTENT

