from flask import request
from flask_restx import Namespace, Resource, fields
from ..utils import db
from ..models import Student, Admin
from werkzeug.security import generate_password_hash, check_password_hash
from http import HTTPStatus
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

#  Auth Endpoints

# Auth Namespace
auth_namespace = Namespace('auth', description='Authentication related operations')

# Auth User/Student Model or Schema
user_model = auth_namespace.model('Student', {
    'full_name': fields.String(required=True, description='User full name'),
    'email': fields.String(required=True, description='User email'),
'password': fields.String(required=True, description='User password'),})

# Auth Login Model
login_model = auth_namespace.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password'),
})

# Auth Login Admin Model for Admin Login
login_admin_model = auth_namespace.model('Login Admin', {
    'username': fields.String(required=True, description='Admin email'),
    'password': fields.String(required=True, description='Admin password'),
})

# Register User/Student
@auth_namespace.route('/register')
class Register(Resource):
    @auth_namespace.expect(user_model)
    def post(self):
        data = request.get_json()
        user = Student.query.filter_by(email=data['email']).first()
        if user:
            return {'message': 'User already exists'}, HTTPStatus.CONFLICT
        new_user = Student(
            full_name=data['full_name'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
        )
        db.session.add(new_user)
        db.session.commit()
        return {'message': 'User created successfully'}, HTTPStatus.CREATED
    

# Login User/Student
@auth_namespace.route('/login')
class Login(Resource):
    @auth_namespace.expect(login_model)
    def post(self):
        data = request.get_json()
        user = Student.query.filter_by(email=data['email']).first()
        if not user or not check_password_hash(user.password_hash, data['password']):
            return {'message': 'Invalid credentials'}, HTTPStatus.UNAUTHORIZED
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        return {
            'message': 'Logged in as {}'.format(user.full_name),
            'access_token': access_token,
            'refresh_token': refresh_token
        }, HTTPStatus.OK
    

# Login Admin for Admin Login only
@auth_namespace.route('/login/admin')
class LoginAdmin(Resource):
    @auth_namespace.expect(login_admin_model)
    def post(self):
        data = request.get_json()
        user = Admin.query.filter_by(username=data['username']).first()
        if not user or not check_password_hash(user.password, data['password']):
            return {'message': 'Invalid credentials'}, HTTPStatus.UNAUTHORIZED
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        return {
            'message': 'Logged in as {}'.format(user.username),
            'access_token': access_token,
            'refresh_token': refresh_token
        }, HTTPStatus.OK
    
# Token Refresh
@auth_namespace.route('/refresh')
class Refresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user)
        return {'access_token': new_token}, HTTPStatus.OK
    

# Logout User/Student or Admin
@auth_namespace.route('/logout')
class Logout(Resource):
    @jwt_required()
    def post(self):
        return {'message': 'Successfully logged out'}, HTTPStatus.OK
