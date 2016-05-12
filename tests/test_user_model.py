import unittest
from app.models import User, Group, Permission, AnonymousUser
from app import create_app, db


class UserModelTestCase(unittest.TestCase):
	def setUp(self):
		self.app = create_app('testing')
		self.app_context = self.app.app_context()
		self.app_context.push()
		db.create_all()
		Group.insert_roles()

	def tearDown(self):
		db.session.remove()
		db.drop_all()
		self.app_context.pop()

	def test_password_setter(self):
		u = User(password='cat')
		self.assertTrue(u.password_hash is not None)

	def test_no_password_getter(self):
		u = User(password='cat')
		with self.assertRaises(AttributeError):
			u.password

	def test_password_verification(self):
		u = User(password='cat')
		self.assertTrue(u.verify_password('cat'))
		self.assertFalse(u.verify_password('dog'))

	def test_password_salts_are_random(self):
		u = User(password='cat', nickname='john', email='email')
		u2 = User(password='cat', nickname='john2', email='email')
		self.assertTrue(u.password_hash != u2.password_hash)

	def test_groups_and_permissions(self):
		Group.insert_roles()
		u = User(nickname='mr. Smith', password='cat')
		self.assertTrue(u.is_allowed(Permission.BASIC))
		self.assertFalse(u.is_allowed(Permission.ADMINISTRATING))

	def test_anonymous_user(self):
		u = AnonymousUser()
		self.assertFalse(u.is_allowed(Permission.BASIC))

	def test_gravatar(self):
		u = User(email='john@example.com', nickname='john', password='cat')
		with self.app.test_request_context('/'):
			gravatar = u.gravatar()
			gravatar_256 = u.gravatar(size=256)
			gravatar_pg = u.gravatar(rating='pg')
			gravatar_retro = u.gravatar(default='retro')
		with self.app.test_request_context('/', base_url='https://localhost/'):
			gravatar_ssl = u.gravatar()
			self.assertTrue('http://www.gravatar.com/avatar/' +
								'd4c74594d841139328695756648b6bd6' in gravatar)
			self.assertTrue('s=256' in gravatar_256)
			self.assertTrue('d=retro' in gravatar_retro)
			self.assertTrue('https://secure.gravatar.com/avatar/' +
								'd4c74594d841139328695756648b6bd6' in gravatar_ssl)
