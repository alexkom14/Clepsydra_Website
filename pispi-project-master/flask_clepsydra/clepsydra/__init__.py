from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache
from flask_msearch import Search

app = Flask(__name__)
# Used for sessions
app.secret_key = 'b\x90\x9a\xbd\xbbL.YA\xd3\x9e\xd7E\x96\x16J"\x06\xe9\x12\xaeC\xa2\xc8id\x90\xa1\xf0l<O\x1d'

# Cache config
app.config['CACHE_TYPE'] = 'simple'
cache = Cache()
cache.init_app(app)

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # file of database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
SQLAlchemy_ECHO = True

# Database migration
migrate = Migrate(app, db)

# M_search
search = Search()
search.init_app(app)

# DO NOT REMOVE, this is supposed to be last
from . import routes
