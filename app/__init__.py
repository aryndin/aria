from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.bootstrap import Bootstrap
import os
from flask.ext.login import LoginManager
from flask.ext.openid import OpenID
from config import config

bootstrap = Bootstrap()
db = SQLAlchemy()
lm = LoginManager()
lm.session_protection = 'strong'
lm.login_view = 'auth.login'

def create_app(config_name):
	app = Flask(__name__)
	app.config.from_object(config[config_name])
	config[config_name].init_app(app)



	bootstrap.init_app(app)
	db.init_app(app)
	lm.init_app(app)

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




