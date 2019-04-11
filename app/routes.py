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
    DeleteForm,
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
from elasticsearch import Elasticsearch


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
    rankrow = (Album.query
           .filter_by(user_id=current_user.id)
           .order_by(Album.rank.desc())
           .limit(1)
           .all())
    rank = rankrow[0].rank + 1
    if request.method == 'POST' and form.validate_on_submit():
        album = Album()
        album.rank = form.rank.data
        album.title = form.title.data
        album.artist = form.artist.data
        album.year = form.year.data
        album.last_played = datetime.strptime(form.last_played.data, '%Y-%m-%d')
        album.user_id = current_user.id
        # make sure the added album's ranking is no lower than what makes sense
        # e.g. if there are currently 200 albums in favorites,
        # the lowest that makes sense is 201
        if int(album.rank) > rank:
            album.rank = rank
        elif int(album.rank) < rank:
            # get every album lower *numerically higher) in current ranking
            # than the ranking we are trying to add to
            # and increment ranking by 1
            # e.g. there are 200 albums and we assign a ranking of 195 to new album
            # album currently ranked 195 will become 196,
            # album currently ranked 196 will becomes 197...
            # ...album current ranked 200 will become 201
            to_move = (Album.query
                .filter_by(user_id=current_user.id)
                .filter(Album.rank >= int(form.rank.data))
                .filter(Album.rank < rank)
                .order_by(Album.rank.desc())
                .all())
            for a in to_move:
                a.rank += 1
                db.session.commit()
        db.session.add(album)
        db.session.commit()
        flash(f'Successfully added album {album.title} by {album.artist}')
        return redirect(url_for('favorites'))
    # addt'l variables
    curr_dt = datetime.now().strftime('%Y-%m-%d')
    return render_template('addalbum.html',
                           form=form,
                           last_played=curr_dt,
                           rank=rank,
                           toadd=None)


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
    return render_template('editalbum.html',
                           form=form,
                           row=rankrow[0])


@app.route('/tolisten/', methods=['GET', 'POST'])
@login_required
def tolisten():
    form = RandomForm()
    tolisten = (ToListen.query
                .filter_by(user_id=current_user.id)
                .order_by(ToListen.artist)
                .order_by(ToListen.year)
                .all())
    if request.method == 'POST':
        selection = None
        while selection == None:
            #TO-DO: query for all id's and then select random id.
            #currently as albums get deleted the id's do not get backfilled
            #so over time we will not be including more and more albums...
            rint = randint(0, len(tolisten) - 1)
            selection = ToListen.query.get(rint)
        flash(f'Listen to {selection}')
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


@app.route('/tolisten/delete/<id>/', methods=['GET', 'POST'])
@login_required
def delete_tolisten(id):
    form = DeleteForm()
    todelete = ToListen.query.get(id)
    title, artist = todelete.title, todelete.artist
    if request.method == 'POST':
        flash(f'Deleted {title} by {artist} from albums to listen')
        ToListen.query.filter(ToListen.id==id).delete()
        db.session.commit()
        return redirect(url_for('tolisten'))
    return render_template('delete.html', form=form, todelete=todelete)


@app.route('/tolisten/add_to_favorites/<id>/', methods=['GET', 'POST'])
@login_required
def add_tl_to_fav(id):
    """
    Add an album from tolisten to favorites
    """
    toadd = ToListen.query.get(id)
    form = AlbumForm(request.form)
    # the suggested rank should be the next available rank
    # e.g. if there are 200 albums currently in the favorites list,
    # the suggested rank should be 201
    rank = db.session.query(func.max(Album.rank).label("rank")).scalar() + 1
    if request.method == 'POST' and form.validate_on_submit():
        album = Album()
        album.rank = form.rank.data
        album.title = form.title.data
        album.artist = form.artist.data
        album.year = form.year.data
        album.last_played = datetime.strptime(form.last_played.data, '%Y-%m-%d')
        album.user_id = current_user.id
        # make sure the added album's ranking is no lower than what makes sense
        # e.g. if there are currently 200 albums in favorites,
        # the lowest that makes sense is 201
        if int(album.rank) > rank:
            album.rank = rank
        elif int(album.rank) < rank:
            # get every album lower *numerically higher) in current ranking
            # than the ranking we are trying to add to
            # and increment ranking by 1
            # e.g. there are 200 albums and we assign a ranking of 195 to new album
            # album currently ranked 195 will become 196,
            # album currently ranked 196 will becomes 197...
            # ...album current ranked 200 will become 201
            to_move = (Album.query
                .filter_by(user_id=current_user.id)
                .filter(Album.rank >= int(form.rank.data))
                .filter(Album.rank < rank)
                .order_by(Album.rank.desc())
                .all())
            for a in to_move:
                a.rank += 1
                db.session.commit()
        db.session.add(album)
        title, artist = toadd.title, toadd.artist
        ToListen.query.filter(ToListen.id==id).delete()
        db.session.commit()
        flash(f'Successfully added album {album.title} by {album.artist}')
        flash(f'Deleted {title} by {artist} from albums to listen')
        return redirect(url_for('favorites'))
    # addt'l variables
    curr_dt = datetime.now().strftime('%Y-%m-%d')
    curr_dt = datetime.now().strftime('%Y-%m-%d')
    return render_template('addalbum.html',
                           form=form,
                           last_played=curr_dt,
                           rank=rank,
                           toadd=toadd)


@app.route('/lastplayed/')
@app.route('/lastplayed/<count>/')
def lastplayed(count=20):
    lastplayed = (Album.query
                .filter_by(user_id=current_user.id)
                .order_by(Album.last_played.desc())
                .limit(count))
    title = 'Favorite Albums of All Time'
    return render_template('favorites.html', rows=lastplayed)


@app.route('/favorites/search/')
def search():
    term = request.args.get('term', '')
    filters = request.args.get('filter', '')

    if not term or term == 'null':
        term = '*'

    results = perform_query(term, filters)

    return render_template('favorites.html')

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
