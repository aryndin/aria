from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand
from app import create_app, db

app = create_app('default')
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)
db.Model()

@manager.command
def test():
	'''Запускает модульное тестирование'''
	import unittest
	tests = unittest.TestLoader().discover('tests')
	unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
	manager.run()

