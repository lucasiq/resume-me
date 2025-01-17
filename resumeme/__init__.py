import os

from flask import Flask, render_template, request, redirect
from flask.ext.mongoengine import MongoEngine, MongoEngineSessionInterface
from flask.ext.login import LoginManager
from flask.ext.bcrypt import Bcrypt
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.mail import Mail

# Create and name Flask app
app = Flask("ResumeMeApp")

# database connection
app.config['MONGODB_SETTINGS'] = {
    'HOST': os.environ.get('MONGOLAB_URI'), 'DB': 'test'}
app.config['SECRET_KEY'] = 'This string will be replaced'

app.debug = os.environ.get('DEBUG', True)

db = MongoEngine(app)  # connect MongoEngine with Flask App
app.session_interface = MongoEngineSessionInterface(db)  # sessions w/ mongoengine

# Flask BCrypt will be used to salt the user password
flask_bcrypt = Bcrypt(app)

# Adding Bootstrap Support
bootstrap = Bootstrap(app)

# Adding momentjs support
moment = Moment(app)

# Associate Flask-Login manager with current app
login_manager = LoginManager()
login_manager.init_app(app)

# Adding Mail Support
# email server
app.config.update(
    MAIL_SUPPRESS_SEND=False,
    TESTING=False,
    MAIL_DEBUG=True,
    MAIL_USE_SSL=True,
    MAIL_SERVER="smtp.unil.ch",
    MAIL_PORT=465,
    MAIL_USERNAME=os.environ.get('RCV_MAIL_USER'),
    MAIL_PASSWORD=os.environ.get('RCV_MAIL_PWD')
)

mail = Mail(app)

app.config['MAX_CONTENT_LENGTH'] = 0.99 * 1024 * 1024


# Application wide Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.errorhandler(400)
def bad_request(e):
    return render_template('400.html'), 400
