from datetime import datetime
from decimal import Decimal
import bleach
from markdown import markdown
from flask import request
from app import db
from . import lm
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
from flask.ext.login import AnonymousUserMixin
from sqlalchemy.ext.hybrid import hybrid_property

@lm.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))


class Permission:
	BASIC = 0x01
	USER_M = 0x02
	DEPOT_M = 0x04
	SALE_M = 0x08
	ADMINISTRATING = 0x80


class AnonymousUser(AnonymousUserMixin):
	def is_allowed(self, Permission):
		return False

lm.anonymous_user = AnonymousUser


class User(db.Model):
	__tablename__ = "users"
	id = db.Column(db.Integer, primary_key=True)
	nickname = db.Column(db.String(64), index=True, unique=True, nullable=False)
	fullname = db.Column(db.String(128))
	_email = db.Column('email', db.String(120), index=True, unique=True, nullable=False)
	group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
	credit = db.Column(db.Numeric(precision=10.3))
	password_hash = db.Column(db.String(120))
	avatar_hash = db.Column(db.String(32))
	tasks_to_do = db.relationship("Task", backref="worker", lazy="dynamic", foreign_keys='[Task.assigned_to]')
	assigned_tasks = db.relationship("Task", backref="manager", lazy="dynamic", foreign_keys='[Task.assigned_by]')

	def __init__(self, **kwargs):  # TODO ?
		super(User, self).__init__(**kwargs)
		if self.group is None:
			self.group = Group.query.filter_by(access_level=Permission.BASIC).first()

		if self.email is not None and self.avatar_hash is None:
			self.avatar_hash = md5(
				self.email.lower().encode('utf-8')
			).hexdigest()

	def is_allowed(self, permissions):
		return self.group is not None and \
			   (self.group.access_level & permissions) == permissions

	@property
	def is_authenticated(self):
		return True

	@property
	def is_active(self):
		return True

	@property
	def is_anonymous(self):
		return False

	@property
	def password(self):
		raise AttributeError('password is not a readable attribute')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

	@hybrid_property
	def email(self):
		return self._email

	@email.setter
	def email(self, email):
		self._email = email
		self.calc_avatar_hash()

	# generate fake users
	@staticmethod
	def generate_fake(count=100):
		from sqlalchemy.exc import IntegrityError
		from random import seed
		import forgery_py

		seed()
		for i in range(count):
			u = User(email=forgery_py.internet.email_address(),
					 nickname=forgery_py.internet.user_name(True),
					 password=forgery_py.lorem_ipsum.word(),
					 fullname=forgery_py.name.full_name())
			db.session.add(u)
			try:
				db.session.commit()
			except IntegrityError:
				db.session.rollback()

	def calc_avatar_hash(self):
		if self.email is not None:
			self.avatar_hash = md5(
				self.email.lower().encode('utf-8')
			).hexdigest()

	def get_id(self):
		try:
			return unicode(self.id)  # python 2
		except NameError:
			return str(self.id)  # python 3

	def __repr__(self):
		return '<User {}>'.format(self.nickname)

	def gravatar(self, size=100, default='identicon', rating='g'):
		if request.is_secure:
			url = 'https://secure.gravatar.com/avatar'
		else:
			url = 'http://www.gravatar.com/avatar'
		hash = self.avatar_hash or md5(
			self.email.lower().encode('utf-8')
		).hexdigest()
		return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
			url=url, hash=hash, size=size, default=default, rating=rating)


class Task(db.Model):
	__tablename__ = 'tasks'
	id = db.Column(db.Integer, primary_key=True)
	assigned_by = db.Column(db.Integer, db.ForeignKey('users.id'))
	assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
	title = db.Column(db.String(140))
	description = db.Column(db.Text)
	description_html = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, default=datetime.now)
	timelimit = db.Column(db.DateTime)
	price = db.Column(db.Numeric(precision=10, scale=3))
	state = db.Column(db.Boolean)

	def delete(self):
		db.session.delete(self)

	@staticmethod
	def on_changed_description(target, value, oldvalue, initialot):
		allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
						'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
						'h1', 'h2', 'h3', 'h4', 'h5', 'p']
		target.description_html = bleach.linkify(bleach.clean(
			markdown(value, output_format='html'),
			tags=allowed_tags, strip=True
		))

	#generate fake tasks
	@staticmethod
	def generate_fake(count=100):
		from random import seed, randint
		import forgery_py

		seed()
		user_count = User.query.count()
		for i in range(count):
			um = User.query.get(1)
			uw = User.query.get(2)
			p = Task(title=forgery_py.lorem_ipsum.words(randint(5,15)),
					 description=forgery_py.lorem_ipsum.sentences(randint(1,4)),
					 timelimit=forgery_py.date.date(True),
					 manager=um,
					 worker=uw,
					 state=randint(0,1),
					 price=Decimal(randint(100,1000)))
			db.session.add(p)
			db.session.commit()

	def __repr__(self):
		return '<Task {}>'.format(self.title)

db.event.listen(Task.description, 'set', Task.on_changed_description)


class Group(db.Model):
	__tablename__ = 'groups'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64))
	access_level = db.Column(db.Integer)
	users = db.relationship('User', backref='group')

	def __repr__(self):
		return '<Group {}>'.format(self.name)


	@staticmethod
	def insert_roles():
		groups = {
			'User': Permission.BASIC,
			'Manager': (Permission.DEPOT_M |
						Permission.SALE_M |
						Permission.USER_M),
			'Administrator': 0xff
		}

		for g in groups:
			group = Group.query.filter_by(name=g).first()
			if group is None:
				group = Group(name=g)
			group.access_level = groups[g]
			db.session.add(group)
		db.session.commit()


class Supplier(db.Model):
	__tablename__ = 'suppliers'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(128))
	shipment = db.relationship('Shipment', backref='supplier', lazy='dynamic')


class Shipment(db.Model):
	__tablename__ = 'shipments'
	id = db.Column(db.Integer, primary_key=True)
	id_supplier = db.Column(db.Integer, db.ForeignKey(Supplier.id))
	date = db.Column(db.Date)
	things = db.relationship('Invoice', back_populates='shipment', lazy='dynamic',
							 cascade="save-update, merge, delete, delete-orphan")

	def __repr__(self):
		return '<Shipment by {}>'.format(self.supplier.name)

	def add_thing(self, thing, amount, price):
		if not self.has(thing):
			invoice = Invoice(amount=amount, price=price)
			invoice.thing = thing
			self.things.append(invoice)
			db.session.add(self)

	def remove_thing(self, thing):
		thing = self.things.filter_by(thing_id=thing.id).first()
		if thing:
			db.session.delete(thing)

	def has(self, thing):
		return self.things.filter_by(thing_id=thing.id).first() is not None


class Invoice(db.Model):
	__tablename__ = 'invoices'
	shipment_id = db.Column(db.Integer, db.ForeignKey('shipments.id'), primary_key=True)
	thing_id = db.Column(db.Integer, db.ForeignKey('things.id'), primary_key=True)
	amount = db.Column(db.Numeric(precision=10, scale=3))
	price = db.Column(db.Numeric(precision=10, scale=3))
	shipment = db.relationship('Shipment', back_populates='things', lazy='joined')
	thing = db.relationship('Thing', back_populates='shipments', lazy='joined')


class Thing(db.Model):
	__tablename__ = 'things'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(128))
	shipments = db.relationship('Invoice', back_populates='thing', lazy='dynamic',
								cascade="save-update, merge, delete, delete-orphan")
	measure_id = db.Column(db.Integer, db.ForeignKey('measures.id'))
	stock = db.Column(db.Numeric(precision=10, scale=3))
	price = db.Column(db.Numeric(precision=10, scale=3))
	type_id = db.Column(db.Integer, db.ForeignKey('types_of_things.id'))
	consist_of = db.relationship('ConsistOf', foreign_keys='[ConsistOf.thing_id]',
								 backref=db.backref('thing', lazy='joined'),
								 lazy='dynamic',
								 cascade='all, delete-orphan')

	part_of = db.relationship('ConsistOf', foreign_keys='[ConsistOf.part_id]',
								 backref=db.backref('part', lazy='joined'),
								 lazy='dynamic',
								 cascade='all, delete-orphan')
	products = db.relationship('Product', backref='product')


class TypeOfThing(db.Model):
	__tablename__ = 'types_of_things'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64))
	assembled = db.Column(db.Boolean, default=False)
	marketable = db.Column(db.Boolean, default=False)
	things = db.relationship('Thing', backref='type')


class Measure(db.Model):
	__tablename__ = 'measures'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64))
	things_measures = db.relationship('Thing', backref='measure')


class ConsistOf(db.Model):
	__tablename__ = 'consist_of'
	thing_id = db.Column(db.Integer, db.ForeignKey('things.id'), primary_key=True)
	part_id = db.Column(db.Integer, db.ForeignKey('things.id'), primary_key=True)
	amount = db.Column(db.Numeric(precision=10, scale=3))


class Product(db.Model):
	__tablename__ = 'products'
	id = db.Column(db.Integer, primary_key=True)
	product_id = db.Column(db.Integer, db.ForeignKey('things.id'))
	assembly_date = db.Column(db.DateTime)
	assembler = db.relationship('User',
								secondary='product_assembler',
								backref=db.backref('products', lazy='dynamic'),
								lazy='dynamic')


product_assembler = db.Table('product_assembler',
							 db.Column('assembler_id', db.Integer, db.ForeignKey('users.id')),
							 db.Column('product_id', db.Integer, db.ForeignKey('products.id')))




