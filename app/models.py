from datetime import datetime
from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    albums = db.relationship('Album', backref='listener', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    artist = db.Column(db.String(140))
    year = db.Column(db.Integer)
    last_played = db.Column(db.DateTime, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Album {}>'.format(self.title)
