import pandas as pd
from datetime import datetime
from app import db
from app.models import User, ToListen

df = pd.read_csv('./app/input_files/tolisten.txt', sep='\t')
u = User.query.get(1)
for i, r in df.iterrows():
    tl = ToListen(title=r.Album,
              artist=r.Artist,
              year=r.Year,
              user_id=u.id)
    db.session.add(tl)

db.session.commit()
