from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from redis import Redis
from flask_wtf.csrf import CSRFProtect
import os
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from elasticsearch import Elasticsearch



ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
RECEPIENTS = ['test@gmail.com']


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://doadmin:4q3Gvl_DU-UGIH5v@db-postgresql-nyc3-08885-do-user-9807415-0.b.db.ondigitalocean.com:25060/defaultdb?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.realpath('.') +'/my_app/static/uploads'
app.config['WTF_CSRF_SECRET_KEY']  = 'random key for form'
app.config['LOG_FILE'] = 'application.log'
app.config['AWS_ACCESS_KEY'] = 'AKIAQ33NPU6TC2AHSMK2'
app.config['AWS_SECRET_KEY'] = '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'
app.config['AWS_BUCKET'] = 'testbucket-smbj'
app.config['WHOOSH_BASE'] = '/tmp/whoosh'
csrf = CSRFProtect(app) 

db = SQLAlchemy(app)
migrate = Migrate(app, db)
redis = Redis()

app.config['LOG_FILE'] = '/tmp/application.log'

if not app.debug:
    import logging
    logging.basicConfig(level=logging.INFO)
    from logging import FileHandler, Formatter
    from logging.handlers import SMTPHandler
    file_handler = FileHandler(app.config['LOG_FILE'])
    app.logger.addHandler(file_handler)
    mail_handler = SMTPHandler(
        ("smtp.gmail.com", 587), 'test@gmail.com', RECEPIENTS,
        'Error occurred in your application',
        ('test@gmail.com', 'Test'), secure=None)
    mail_handler.setLevel(logging.ERROR)
    #app.logger.addHandler(mail_handler)
    for handler in [file_handler, mail_handler]:
        handler.setFormatter(Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))

#api = Api(app, decorators=[csrf.exempt])


app.secret_key = 'some_random_key'
es = Elasticsearch('http://localhost:9200/')
es.indices.create('catalog', ignore=400)


from my_app.catalog.views import catalog


app.register_blueprint(catalog)

db.create_all()

def get():
    return


