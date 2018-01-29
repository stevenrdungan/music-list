from flask_wtf import FlaskForm
from wtforms import  (
    BooleanField,
    FieldList,
    FormField,
    PasswordField,
    StringField,
    SubmitField,
    validators
)
from datetime import datetime


class LoginForm(FlaskForm):
    username = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class AlbumForm(FlaskForm):
    rank = StringField('Rank', [validators.InputRequired()])
    title = StringField('Title', [validators.InputRequired()])
    artist = StringField('Artist', [validators.InputRequired()])
    year = StringField('Year', [validators.InputRequired()])
    last_played = StringField('Last Played (yyyy-MM-dd)',
                              [validators.InputRequired()])
    submit = SubmitField('Commit Changes')


class FavoritesForm(FlaskForm):
    favorites = FieldList(FormField(AlbumForm))
    submit = SubmitField('Update')


class ToListenAlbumForm(FlaskForm):
    title = StringField('Title', [validators.InputRequired()])
    artist = StringField('Artist', [validators.InputRequired()])
    year = StringField('Year', [validators.InputRequired()])
    submit = SubmitField('Commit Changes')


class ToListenForm(FlaskForm):
        tolisten = FieldList(FormField(ToListenAlbumForm))
        submit = SubmitField('Update')
