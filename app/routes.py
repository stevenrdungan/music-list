from flask import render_template, flash, redirect, request, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app import app
from app.forms import LoginForm
from app.models import User
import pandas as pd
import numpy as np


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

@app.route('/favorites')
@login_required
def favorites():
    df = pd.read_csv('./app/input_files/favorites.txt', sep='\t')
    df.drop(['Rank'], axis=1, inplace=True)
    table = prep_table(df)
    title = 'Favorite Albums of All Time'
    return render_template('table.html', table=table, title=title)

@app.route('/beachboys')
def beachboys():
    df = pd.read_csv('./app/input_files/beachboys.txt', sep='\t')
    df.drop(['Rank'], axis=1, inplace=True)
    table = prep_table(df)
    title = 'Favorite Beach Boys Songs of All Time'
    return render_template('table.html', table=table, title=title)

@app.route('/tolisten')
def tolisten():
    df = pd.read_csv('./app/input_files/tolisten.txt', sep='\t')
    table = prep_table(df)
    title = 'To Listen'
    return render_template('table.html', table=table, title=title)

@app.route('/login', methods=['GET', 'POST'])
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

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
