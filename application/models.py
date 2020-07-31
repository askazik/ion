from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Date, String, Boolean, func, \
    CheckConstraint, event, BLOB, Text, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class Users(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(80), index=True, unique=True)
    email = Column(String(120), index=True, unique=True)
    pw_hash = Column(String(256), index=True, unique=True)
    rand_number = Column(Integer)  # store the last registration token
    language = Column(String(80), default="en_US")

    def __repr__(self):
        return '<Users %r>' % self.id

    @property
    def password_string(self):
        raise AttributeError('password_string is not a readable attribute')

    @password_string.setter
    def password_string(self, password):
        self.pw_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.pw_hash, password)
