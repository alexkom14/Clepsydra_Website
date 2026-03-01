# PSPI-Project Phase II

### Required packages:
* flask-sqlalchemy
* flask-wtf
* flask-migrate
* flask-caching
* flask-msearch

### To run the web app:
Run `python run.py` in the flask_clepsydra folder.

### To migrate the database:
* Make sure you are in the `clepsydra/` folder (inside the package) in the terminal.
* Make sure you have set the FLASK_APP variable; <br/>
  In windows `set FLASK_APP=__init__.py`, <br/>
  In linux `export FLASK_APP=__init__.py`
* Add the new schema with, `flask db migrate -m "<commit-message>"`
* Upgrade to the new database with, `flask db upgrade`
