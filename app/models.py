from datetime import datetime
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    albums = db.relationship('Album', backref='listener', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Album(db.Model):
    __tablename__ = 'albums'
    id = db.Column(db.Integer, primary_key=True)
    rank = db.Column(db.Integer, unique=True)
    title = db.Column(db.String(140))
    artist = db.Column(db.String(140))
    year = db.Column(db.Integer)
    last_played = db.Column(db.DateTime, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<{}. {} by {}>'.format(self.rank, self.title, self.artist)


class ToListen(db.Model):
    __tablename__ = 'tolisten'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    artist = db.Column(db.String(140))
    year = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f'{self.title} by {self.artist}'
