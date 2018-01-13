from flask import render_template
from app import app
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
    filename = 'favorites'
    return render_template('favorites.html', filename=filename)

@app.route('/beachboys')
def beachboys():
    filename= 'beachboys'
    return render_template('beachboys.html', filename=filename)

@app.route('/tolisten')
def tolisten():
    filepath = './app/input_files/tolisten.txt'
    df= pd.read_csv(filepath, sep='\t')
    table = prep_table(df)
    title = 'To Listen'
    return render_template('tolisten.html', table=table, title=title)
