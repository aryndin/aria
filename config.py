import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:

	DEBUG = True
	WTF_CSRF_ENABLED = True
	SECRET_KEY = 'qwerty'

	SQLALCHEMY_DATABASE_URI = 'mysql://root:951793@localhost/mainflask'
	SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
	SQLALCHEMY_TRACK_MODIFICATIONS = True

	OPENID_PROVIDERS = [
		{'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id'},
		{'name': 'Yahoo', 'url': 'https://me.yahoo.com'},
		{'name': 'AOL', 'url': 'http://openid.aol.com/<username>'},
		{'name': 'Flickr', 'url': 'http://www.flickr.com/<username>'},
		{'name': 'MyOpenID', 'url': 'https://www.myopenid.com'}]

	BOOTSTRAP_SERVE_LOCAL = True

	@staticmethod
	def init_app(app):
		pass


class TestingConfig(Config):
	TESTING = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
							  'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')

config = {
	'default': Config,
	'testing': TestingConfig
}