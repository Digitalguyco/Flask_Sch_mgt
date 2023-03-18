from flask_restx import Namespace, Resource, fields
from ..models import Student,  Admin
from ..utils import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from http import HTTPStatus

# Student Endpoint


# Student Namespace
student_namespace = Namespace('students', description='Students related operations')

# Calculate GPA for a student
def calculate_gpa(student):
    enrollments = student.enrollments
    if not enrollments:
        return None

    total_credits = 0.0
    total_points = 0.0

    for enrollment in enrollments:
        course = enrollment.course
        credits = course.credits
        grade = enrollment.grade or 0.0

        total_credits += credits
        total_points += grade * credits

    gpa = total_points / total_credits
    return gpa


# Student Model or Schema
student_model = student_namespace.model('Student', {
    'id': fields.String(required=True, description='Student id'),
    'full_name': fields.String(required=True, description='Student name'),
    'email': fields.String(required=True, description='Student email'),
})


# Student Get and Create to get all students and create a new student
@student_namespace.route('/')
class StudentGetCreate(Resource):
    @student_namespace.doc('get_students')
    @student_namespace.marshal_list_with(student_model)
    @jwt_required()
    def get(self):
        '''
        Get all students
        
        '''
        return Student.get_students(), HTTPStatus.OK
    
    @student_namespace.doc('create_student')
    @student_namespace.expect(student_model)
    @student_namespace.response(HTTPStatus.CREATED, 'Student created')
    @jwt_required()
    def post(self):
        '''
        
        Create a new student
            by admin only
        
        '''

        
        user_jwt = get_jwt_identity()

        if not user_jwt:
            return {'message': 'Admin not found'}, HTTPStatus.NOT_FOUND

        current_user = Admin.query.filter_by(id=user_jwt).first()

        if not current_user.is_active:
            response = {'message': 'You are not an active Admin so you are not authorized to perform this action'}
            return response, HTTPStatus.UNAUTHORIZED

        data = student_namespace.payload
        new_student = Student(
            full_name=data['name'],
            email=data['email'],
            is_student=data['is_student'],
            is_admin=False
        )
        new_student.set_password(data['password'])
        new_student.save()
        return {'message': 'Student created'}, HTTPStatus.CREATED
    

@student_namespace.route('/student/<int:id>')
class StudentGetUpdateDelete(Resource):
    @student_namespace.doc('get_student_by_id')
    @jwt_required()
    def get(self, id):
        '''
        Get a student by id
            by admin or student(only if it is the current student)
        '''

        user_jwt = get_jwt_identity()
        student = Student.get_by_id(id)
        
        enrollments = []
        for enrollment in student.enrollments:
            course = enrollment.course
            enrollments.append({
                'course_name': course.name,
                'course_description': course.description,
                'grade': enrollment.grade
            })

        gpa = calculate_gpa(student)

        if not student:
            return {'message': 'Student not found'}, HTTPStatus.NOT_FOUND
        
        if not user_jwt:
            return {'message': 'User not found'}, HTTPStatus.NOT_FOUND
        
        current_student = Student.query.filter_by(id=user_jwt).first()
        admin = Admin.query.filter_by(id=user_jwt,is_active=True).first()

        if not current_student and not admin:
            return {'message': 'User or Active Admin not found'}, HTTPStatus.NOT_FOUND
        

        if current_student.id != student.id and not admin:
            return {'message': 'You can\'t View this student'}, HTTPStatus.UNAUTHORIZED
        

        response = {
            'full_name': student.full_name,
            'email': student.email,
            'enrollments': enrollments,
            'gpa': gpa
            }

        return response, HTTPStatus.OK
    
    @student_namespace.doc('update_student')
    @student_namespace.expect(student_model)
    @student_namespace.response(HTTPStatus.OK, 'Student updated')
    @jwt_required()
    def put(self, id):
        '''
        Update a student  
        by admin and student(only if it is the current student)     
        '''

        user_jwt = get_jwt_identity()

        if not user_jwt:
            return {'message': 'User not found'}, HTTPStatus.NOT_FOUND
        
        # Check if user is and admin or Student
        current_student = Student.query.filter_by(id=user_jwt).first()
        admin = Admin.query.filter_by(id=user_jwt,is_active=True).first()
        #  Check if there is a user
        if not current_student and not admin:
            return {'message': 'User or Active Admin not found'}, HTTPStatus.NOT_FOUND
        
        #  check current user id and id in url are the same
        if current_student != id and not admin:
            return {'message': 'You can\'t update this student'}, HTTPStatus.UNAUTHORIZED
            
        
        student = Student.query.get_or_404(id)
        data = student_namespace.payload
        student.full_name=data['name']
        student.email=data['email']
        student.save()

        return {'message': 'Student updated'}, HTTPStatus.OK
    
    @student_namespace.doc('delete_student_by_id')
    @student_namespace.response(HTTPStatus.OK, 'Student deleted')
    @jwt_required()
    def delete(self, id):
        '''
        Delete a student
            by admin only
        '''
        user_jwt = get_jwt_identity()
        

        if not user_jwt:
            return {'message': 'Admin not found'}, HTTPStatus.NOT_FOUND

        current_user = Admin.query.filter_by(id=user_jwt,is_active=True).first()

        if not current_user:
            response = {'message': 'You are not authorized to perform this action'}
            return response, HTTPStatus.UNAUTHORIZED
        

            
        

        student = Student.query.get_or_404(id)
        db.session.delete(student)
        db.session.commit()
        return {'message': 'Student deleted'}, HTTPStatus.OK



