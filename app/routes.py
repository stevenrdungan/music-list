from flask import render_template
from app import app
import pandas as pd
import numpy as np


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
    filepath = './app/tolisten.txt'
    table = pd.read_csv(filepath, sep='\t')
    table.replace(np.nan, '', inplace=True)
    table.index += 1
    title = 'To Listen'
    return render_template('tolisten.html', table=table.to_html(), title=title)
