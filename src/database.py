from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import string
import random

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())
    bookmarks = db.relationship('Bookmark', backref='user')

    def __repr__(self) -> str:
        return 'User>>> {self.username}'


class Bookmark(db.Model):    
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=True)
    url = db.Column(db.Text, nullable=True)
    short_url = db.Column(db.String(3), nullable=True)
    visits = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

    def generate_short_characters(self, length):
        characters = string.digits + string.ascii_letters
        picked_chars = ''.join(random.choice(characters) for i in range(length))

        # checks the db if there is a link with the picked_chars
        link = self.query.filter_by(short_url=picked_chars).first()

        if link:
            # regenerate another character if picked_chars already exists
            self.generate_short_characters(3)
        else:
            return picked_chars


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.short_url = self.generate_short_characters(3)


    def __repr__(self) -> str:
        return 'Bookmark>>> {self.url}'




