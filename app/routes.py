from flask import (
    flash,
    redirect,
    render_template,
    request,
    url_for
)
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user
)
from app import app, db
from app.forms import AlbumForm, FavoritesForm, LoginForm
from app.models import Album, User
import pandas as pd
import numpy as np
from datetime import datetime
from sqlalchemy import func

def prep_table(df):
    '''cleans dataframe and returns as html'''
    df.replace(np.nan, '', inplace=True)
    df.index += 1
    return df.to_html()

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html',
                            title='Music-List',
                            user=current_user.username)


@app.route('/favorites/')
@login_required
def favorites():
    favorites = (Album.query
                .filter_by(user_id=current_user.id)
                .order_by(Album.rank))
    title = 'Favorite Albums of All Time'
    return render_template('dbtable.html', rows=favorites)


@app.route('/favorites/add/', methods=['GET', 'POST'])
@login_required
def add_favorite():
    """
    Add an album to favorites
    """
    form = AlbumForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        album = Album()
        album.rank = form.rank.data
        album.title = form.title.data
        album.artist = form.artist.data
        album.year = form.year.data
        album.last_played = datetime.strptime(form.last_played.data, '%Y-%m-%d')
        album.user_id = current_user.id
        db.session.add(album)
        db.session.commit()
        flash('Successfully added album')
        return redirect(url_for('favorites'))
    # addt'l variables
    curr_dt = datetime.now().strftime('%Y-%m-%d')
    rankrow = (Album.query
           .filter_by(user_id=current_user.id)
           .order_by(Album.rank.desc())
           .limit(1)
           .all())
    rank = rankrow[0].rank + 1
    return render_template('addalbum.html',
                           form=form,
                           last_played=curr_dt,
                           rank=rank)


@app.route('/favorites/edit/<int:album_id>', methods=['GET', 'POST'])
@login_required
def edit(album_id):
    """
    Edit existing album attributes
    """
    form = AlbumForm(request.form)
    rankrow = (Album.query
           .filter_by(user_id=current_user.id)
           .filter_by(id=int(album_id))
           .order_by(Album.rank.desc())
           .limit(1)
           .all()) # do this before POST because we need previous al sbum id
    if request.method == 'POST' and form.validate_on_submit():
        '''logic to verify commit'''
        db.session.commit()
        flash('Successfully edited album')
        return redirect(url_for('favorites'))
    rank = rankrow[0].rank
    title = rankrow[0].title
    artist = rankrow[0].artist
    year = rankrow[0].year
    last_played = rankrow[0].last_played
    return render_template('editalbum.html',
                           form=form,
                           rank=rank,
                           title=title,
                           artist=artist,
                           year=year,
                           last_played=last_played)


# @app.route('/favorites/edit/<id>', methods=['GET', 'POST'])
# @login_required
# def edit():
#     """
#     Edit existing album attributes
#     """
#     favForm = FavoritesForm()
#     favorites = (Album.query
#                 .filter_by(user_id=current_user.id)
#                 .order_by(Album.rank))
#     for album in favorites:
#         a = AlbumForm()
#         a.rank = album.rank
#         a.title = album.title
#         a.artist = album.artist
#         a.year = album.year
#         a.last_played = album.last_played.strftime('%Y-%m-%d')
#         a.user_id = album.user_id
#         favForm.favorites.append_entry(a)
#     if request.method == 'POST':
#         if favForm.validate_on_submit():
#             # update database objects with changes to form
#             db.session.commit()
#             flash('Successfully edited albums')
#             return redirect(url_for('favorites'))
#         else:
#             # look at validate_on_submit() and validate() code
#             flash('Could not make updates')
#             return redirect(url_for('favorites'))
#     return render_template('edit.html', favForm=favForm)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('index')
        flash('You were successfully logged in')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('index'))

# @app.route('/tolisten')
# def tolisten():
#     df = pd.read_csv('./app/input_files/tolisten.txt', sep='\t')
#     table = prep_table(df)
#     title = 'To Listen'
#     return render_template('table.html', table=table, title=title)
