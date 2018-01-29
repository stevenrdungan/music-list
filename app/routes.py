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
from app.forms import (
    AlbumForm,
    LoginForm,
    RandomForm,
    ToListenForm
)
from app.models import Album, User, ToListen
import pandas as pd
import numpy as np
from datetime import datetime
from sqlalchemy import func
from random import randint


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
    return render_template('favorites.html', rows=favorites)


@app.route('/favorites/add/', methods=['GET', 'POST'])
@login_required
def add_favorite():
    """
    Add an album to favorites
    """
    form = AlbumForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        # add logic to insert album in any position
        album = Album()
        album.rank = form.rank.data
        album.title = form.title.data
        album.artist = form.artist.data
        album.year = form.year.data
        album.last_played = datetime.strptime(form.last_played.data, '%Y-%m-%d')
        album.user_id = current_user.id
        db.session.add(album)
        db.session.commit()
        flash(f'Successfully added album {album.title} by {album.artist}')
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


@app.route('/favorites/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """
    Edit existing album attributes
    """
    form = AlbumForm(request.form)
    rankrow = (Album.query
           .filter_by(user_id=current_user.id)
           .filter_by(id=int(id))
           .order_by(Album.rank.desc())
           .limit(1)
           .all()) # do this before POST because we need previous album id
    if request.method == 'POST' and form.validate_on_submit():
        album = Album.query.get(id)
        if int(form.rank.data) != rankrow[0].rank:
            currank = int(rankrow[0].rank)
            album.rank = 20000 # commit dummy value
            db.session.commit()
            # logic for dropping album rank (e.g. 11 to 17)
            if int(form.rank.data) > currank:
                to_move = (Album.query
                    .filter_by(user_id=current_user.id)
                    .filter(Album.rank > currank)
                    .filter(Album.rank <= int(form.rank.data))
                    .order_by(Album.rank)
                    .all())
                for a in to_move:
                    a.rank -= 1
                    db.session.commit()
            # logic for raising album rank (e.g. 11 to 8)
            elif int(form.rank.data) < currank:
                to_move = (Album.query
                    .filter_by(user_id=current_user.id)
                    .filter(Album.rank >= int(form.rank.data))
                    .filter(Album.rank < currank)
                    .order_by(Album.rank.desc())
                    .all())
                for a in to_move:
                    a.rank += 1
                    db.session.commit()
        album.rank = form.rank.data
        album.title = form.title.data
        album.artist = form.artist.data
        album.year = form.year.data
        album.last_played = datetime.strptime(form.last_played.data, '%Y-%m-%d')
        album.user_id = current_user.id
        db.session.commit()
        flash(f'Successfully edited album {form.title.data} by {form.artist.data}')
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

#TODO:
# ability to add to tolisten
# ability to add tolisten album to favorites
@app.route('/tolisten/', methods=['GET', 'POST'])
@login_required
def tolisten():
    form = RandomForm()
    tolisten = (ToListen.query
                .filter_by(user_id=current_user.id)
                .order_by(ToListen.artist)
                .order_by(ToListen.title)
                .all())
    if request.method == 'POST':
        rint = randint(0, len(tolisten) - 1)
        flash(f'Listen to {ToListen.query.get(rint)}')
        #return redirect(url_for('tolisten'))
    title = 'Albums To Listen'
    return render_template('tolisten.html',
                           form=form,
                           rows=tolisten)


@app.route('/tolisten/add/', methods=['GET', 'POST'])
@login_required
def add_tolisten():
    """
    Add an album to favorites
    """
    form = ToListenForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        tla = ToListen()
        tla.title = form.title.data
        tla.artist = form.artist.data
        tla.year = form.year.data
        tla.user_id = current_user.id
        db.session.add(tla)
        db.session.commit()
        flash(f'Successfully added album {tla.title} to listen')
        return redirect(url_for('tolisten'))
    return render_template('addalbumtolisten.html',
                           form=form)


@app.route('/tolisten/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit_tolisten(id):
    """
    Edit existing tolisten attributes
    """
    form = ToListenForm(request.form)
    row = (ToListen.query
           .filter_by(user_id=current_user.id)
           .filter_by(id=int(id))
           .limit(1)
           .all())
    if request.method == 'POST' and form.validate_on_submit():
        tla = ToListen.query.get(id)
        tla.title = form.title.data
        tla.artist = form.artist.data
        tla.year = form.year.data
        tla.user_id = current_user.id
        db.session.commit()
        flash(f'Successfully edited to listen album {form.title.data} by {form.artist.data}')
        return redirect(url_for('tolisten'))
    title = row[0].title
    artist = row[0].artist
    year = row[0].year
    return render_template('edittolisten.html',
                           form=form,
                           title=title,
                           artist=artist,
                           year=year)


@app.route('/lastplayed/')
@app.route('/lastplayed/<count>/')
def lastplayed(count=20):
    lastplayed = (Album.query
                .filter_by(user_id=current_user.id)
                .order_by(Album.last_played.desc())
                .limit(count))
    title = 'Favorite Albums of All Time'
    return render_template('favorites.html', rows=lastplayed)


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
