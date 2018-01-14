from flask import render_template, flash, redirect
from app import app
from app.forms import LoginForm
import pandas as pd
import numpy as np


def prep_table(df):
    '''cleans dataframe and returns as html'''
    df.replace(np.nan, '', inplace=True)
    df.index += 1
    return df.to_html()

@app.route('/')
@app.route('/index')
@app.route('/favorites')
def index():
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
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect('/index')
    return render_template('login.html', title='Sign In', form=form)
