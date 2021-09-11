from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from redis import Redis
from flask_wtf.csrf import CSRFProtect
import os
from flask_babel import Babel




ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.realpath('.') +'/my_app/static/uploads'
app.config['WTF_CSRF_SECRET_KEY']  = 'random key for form'
app.config['LOG_FILE'] = 'application.log'
csrf = CSRFProtect(app) 

db = SQLAlchemy(app)
migrate = Migrate(app, db)
redis = Redis()
ALLOWED_LANGUAGES = {
'en': 'English',
'fr': 'French',
}
babel = Babel(app)


#api = Api(app, decorators=[csrf.exempt])


app.secret_key = 'some_random_key'

from my_app.catalog.views import catalog


app.register_blueprint(catalog)

db.create_all()
