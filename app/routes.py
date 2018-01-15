from flask import render_template, flash, redirect, request, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import LoginForm, AlbumForm
from app.models import User, Album
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
