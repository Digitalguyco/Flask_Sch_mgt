from flask import Flask
from flask_restx import Api
from .config.config import config_dict
from flask_migrate import Migrate
from .utils import db
from .models import Admin, Course, Enrollment, Student
from .auth.views import auth_namespace
from .courses.views import course_namespace  
from .enrollments.views import enrollment_namespace
from .students.views import student_namespace
from flask_jwt_extended import JWTManager
from werkzeug.exceptions import NotFound, MethodNotAllowed
import click
from werkzeug.security import generate_password_hash

# App

# Cli Function to create an admin
def create_admin(username, password):
    user = Admin(username=username, password=generate_password_hash(password), is_active=False)
    user.save()

# Cli Function to delete an admin
def delete_admin(username):
    user = Admin.query.filter_by(username=username).first()
    if user:
        user.delete()

# Cli Function to activate an admin
def activate_admin(username):
    user = Admin.query.filter_by(username=username).first()
    if user:
        user.is_active = True
        user.save()

# Cli Function to deactivate an admin
def deactivate_admin(username):
    user = Admin.query.filter_by(username=username).first()
    if user:
        user.is_active = False
        user.save()

# App Factory
def create_app(config=config_dict['dev']):
    app = Flask(__name__)

    app.config.from_object(config)
    
    # Init db
    db.init_app(app)

    #  JWT
    jwt = JWTManager(app)

    #  Flask Migrate
    migrate = Migrate(app, db)

    # Flask Restx authorization Bearer Auth
    authorizations = {
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Add a JWT token to the header with ** Bearer &lt;JWT&gt; token to authorize** "
        }
    }

    # Flask Restx Api Swagger
    api = Api(app,
        title='School REST API',
        description='A simple REST API for school',
        authorizations=authorizations,
        security='Bearer Auth'
    )
        
    # Flask Restx Namespaces
    api.add_namespace(auth_namespace, path='/auth')
    api.add_namespace(course_namespace, path='/courses')
    api.add_namespace(enrollment_namespace, path='/enrollments')
    api.add_namespace(student_namespace, path='/students')

    # Flask Restx Error Handlers
    @api.errorhandler(NotFound)
    def not_found(error):
        return {"error": "Not Found"},404

    @api.errorhandler(MethodNotAllowed)
    def method_not_allowed(error):
        return {"error": "Method Not Allowed"},404

    # Flask shell context
    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'Admin': Admin,
            'Course': Course,
            'Enrollment': Enrollment,
            'Student': Student
        }
    
    # Cli Commands

    # Create Admin
    @click.command()
    @click.option('--username', prompt=True, help='The admin username')
    @click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The admin password')
    def create_admin_command(username, password):
        create_admin(username, password)
        click.echo('Admin created!')

    # Delete Admin
    @click.command()
    @click.option('--username', prompt=True, help='The admin username')
    def delete_admin_command(username):
        delete_admin(username)
        click.echo('Admin deleted!')

    # Activate Admin
    @click.command()
    @click.option('--username', prompt=True, help='The admin username')
    def activate_admin_command(username):
        activate_admin(username)
        click.echo('Admin activated!')
    
    # Deactivate Admin
    @click.command()
    @click.option('--username', prompt=True, help='The admin username')
    def deactivate_admin_command(username):
        deactivate_admin(username)
        click.echo('Admin deactivated!')

    # Add Cli Commands
    app.cli.add_command(activate_admin_command)
    app.cli.add_command(deactivate_admin_command)
    app.cli.add_command(delete_admin_command)
    app.cli.add_command(create_admin_command)

    return app