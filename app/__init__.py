import locale
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bootstrap import Bootstrap
from flask.ext.login import LoginManager
from flask.ext.pagedown import PageDown
from flask_babelex import Babel
from config import config


locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

bootstrap = Bootstrap()
db = SQLAlchemy()
lm = LoginManager()
lm.session_protection = 'strong'
lm.login_view = 'auth.login'
pagedown = PageDown()
babel = Babel()


def create_app(config_name):
	app = Flask(__name__)
	app.config.from_object(config[config_name])
	config[config_name].init_app(app)

	bootstrap.init_app(app)
	babel.init_app(app)
	db.init_app(app)
	lm.init_app(app)
	pagedown.init_app(app)

	with app.app_context():
		from app.admin import flaskadmin
	flaskadmin.init_app(app)

	from .main import main as main_blueprint
	app.register_blueprint(main_blueprint)

	from .auth import auth as auth_blueprint
	app.register_blueprint(auth_blueprint, url_prefix='/auth')

	return app
# lm = LoginManager()
# lm.session_protection = 'strong'
#
# # create app
# app = Flask(__name__)
# app.config.from_object('config')
#
# # initialise db
# db = SQLAlchemy(app)
# from app import views, models
#
# # initialise Twitter Bootstrap
# bootstrap = Bootstrap(app)
#
# # initialise migration tool
# migrate = Migrate(app, db)
#
# # initialise cli-parser
# manager = Manager(app)
# manager.add_command('db', MigrateCommand)
#
# # initialise login manager
# lm.init_app(app)
# lm.login_view = 'login'




