from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from ..utils import db
from werkzeug.security import generate_password_hash

# Main Database Model


# Many to Many Relationship Table
enrollment_table = Table('enrollment', db.Model.metadata,
    Column('student_id', Integer, ForeignKey('students.id')),
    Column('course_id', Integer, ForeignKey('courses.id'))
) 

# Admin Model
class Admin(db.Model):
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<Admin {self.username}>"
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

# Student Model
class Student(db.Model):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(db.Boolean, default=False, nullable=False)
    enrollments = relationship('Enrollment', back_populates='student')

    #Relationship with Course model
    courses = db.relationship('Course', secondary=enrollment_table, back_populates='students')

    

    def __repr__(self):
        return f"<User {self.full_name}>"
    

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_by_id(model, id):
        return model.query.get_or_404(id)
    
    @classmethod
    def get_students(model):
        return model.query.all()
    
    @classmethod
    def set_password(model, password):
        model.password_hash = generate_password_hash(password)
    

# Course Model
class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(80), nullable=False)
    lecturer= db.Column(db.String(80), nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    enrollments = db.relationship('Enrollment', back_populates='course')

    # Relationship with Student model
    students = db.relationship('Student',secondary=enrollment_table, back_populates='courses')

    def __repr__(self):
        return f"<Course {self.name}>"
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_by_id(model, id):
        return model.query.get_or_404(id)
    
    @classmethod
    def get_all(model):
        return model.query.all()
    
    @classmethod
    def delete_by_id(model, id):
        model = model.get_by_id(id)
        db.session.delete(model)
        db.session.commit()
        return model
    

# Enrollment Model
class Enrollment(db.Model):
    __tablename__ = 'enrollments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    grade = db.Column(db.Float)
    student = db.relationship('Student', back_populates='enrollments')
    course = db.relationship('Course', back_populates='enrollments')