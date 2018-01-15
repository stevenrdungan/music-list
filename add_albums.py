import pandas as pd
from datetime import datetime
from app import db
from app.models import User, Album

df = pd.read_csv('./app/input_files/favorites.txt', sep='\t')
u = User.query.get(1)
for i, r in df.iterrows():
    dstr = r['Last Listen'].split('/')
    yr, mo, da = int(dstr[2]), int(dstr[0]), int(dstr[1])
    if yr < 2000:
        yr += 2000
    dt = datetime(yr, mo, da)
    # add album
    a = Album(title=r.Album,
              artist=r.Artist,
              year=r.Year,
              last_played=dt,
              rank=r.Rank,
              user_id=u.id)
    db.session.add(a)

db.session.commit()
