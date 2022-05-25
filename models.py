from enum import unique
from app import db, Base
from sqlalchemy.orm import relationship
from flask_jwt_extended import create_access_token
from datetime import timedelta
from passlib.hash import bcrypt


class Category(Base):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)  
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  


    def __repr__(self):
       return f'{self.name}'


class User(Base):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    categories = relationship('Category', backref='user', lazy=True)


    def __init__(self,**kwargs):
        self.name = kwargs.get('name')
        self.email = kwargs.get('email')
        self.password = bcrypt.hash(kwargs.get('password'))

    def get_token(self, expire_time=24):
        expire_delta = timedelta(expire_time)
        token = create_access_token(identity=self.id, expires_delta= expire_delta)
        return token

    @classmethod   
    def authonticate(cls,email, password):
        user = cls.query.filter(cls.email == email).one()
        if not bcrypt.verify(password, user.password):
            raise Exception('No user with this password')
        return user

    def __repr__(self):
       return f'{self.name}'

class Check(Base):
    __tablename__ = 'checks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    status = db.Column(db.Integer,  nullable=False)
    items = relationship('Checktem', backref='check', lazy=True, cascade='all,delete') 
    #category
    def __repr__(self):
       return f'{self.name}'


class Checktem(Base):
    __tablename__ = 'check_items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hint = db.Column(db.String(200), nullable=False)
    dispaly_order = db.Column(db.Integer,  nullable=False)
    check_id = db.Column(db.Integer, db.ForeignKey('checks.id') ,nullable=False)
    control_type = db.Column(db.Integer,  nullable=False, default=0)
    def __repr__(self):
       return f'{self.name}'    

class CheckList(Base):
    __tablename__ = 'check_lists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    status = db.Column(db.Integer,  nullable=False)
    #category
    def __repr__(self):
       return f'{self.name}'        

class QuickCheck(Base):
    __tablename__ = 'quick_checks'
    id = db.Column(db.Integer, primary_key=True)    
    date_begin = db.Column(db.DateTime, nullable=False)
    date_end = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Integer,  nullable=False, default=0)
    items = relationship('QuickCheckItem', backref='check', lazy=True, cascade='all,delete') 
    #owner    
    def __repr__(self):
       return f'{self.id}'        

class QuickCheckItem(Base):
    __tablename__ = 'quick_check_items'
    id = db.Column(db.Integer, primary_key=True)    
    result = db.Column(db.String(200), nullable=False)
    quick_check_id = db.Column(db.Integer, db.ForeignKey('quick_checks.id') ,nullable=False)
    #checkItem 
    def __repr__(self):
       return f'{self.id}'       