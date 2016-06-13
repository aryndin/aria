from flask.ext.babelex import lazy_gettext
from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, PasswordField, SubmitField, SelectField, DecimalField, FieldList, \
	FormField, SelectMultipleField
from wtforms.ext.dateutil.fields import DateTimeField
from flask.ext.pagedown.fields import PageDownField
from wtforms.validators import Length, DataRequired, Regexp, ValidationError, Email
from wtforms.widgets import TableWidget
from ..models import Group, User, TypeOfThing, Thing


class Select2MultipleField(SelectMultipleField):



	def pre_validate(self, form):
		# Prevent "not a valid choice" error
		pass


class SelectProductsForm(Form):
	products = SelectMultipleField(u'Tags',
				 coerce=int)

	number = StringField(lazy_gettext('Number of'), validators=[
		DataRequired(), Regexp('^[0-9 ]+$', 0,
							   'only numbers please')
	])
	submit = SubmitField()

	def __init__(self, *args, **kwargs):
		super(SelectProductsForm, self).__init__(*args, **kwargs)
		print (self.products.choices)
		self.products.choices = [(thing.id, thing.name)
								for thing in Thing.query.join(TypeOfThing).filter_by(assembled=1).all()]


class EditProfileForm(Form):
	pass


class EditProfileAdminForm(Form):
	nickname = StringField(lazy_gettext('Nickname (login)'), validators=[
		DataRequired(), Length(1, 64), Regexp('^^[a-zA-Z0-9_-]+$', 0,
										  'Usernames must have only letters,'
										  'numbers, dots or underscores')
	])
	email = StringField(lazy_gettext('Email'), validators=[DataRequired(), Length(1, 64),
											 Email()])
	fullname = StringField(lazy_gettext('Fullname'), validators=[Length(6, 64)])
	group = SelectField(lazy_gettext('Group'), coerce=int)
	submit = SubmitField(lazy_gettext('Submit'))

	def __init__(self, user, *args, **kwargs):
		super(EditProfileAdminForm, self).__init__(*args, **kwargs)
		self.group.choices = [(group.id, group.name)
							  for group in Group.query.order_by(Group.name).all()]
		self.user = user

	def validate_email(self, field):
		if field.data != self.user.email and \
				User.query.filter_by(email=field.data).first():
			raise ValidationError(lazy_gettext('Email is already registered.'))

	def validate_nickname(self, field):
		if field.data != self.user.nickname and \
				User.query.filter_by(nickname=field.data).first():
			raise ValidationError(lazy_gettext('Nickname is already registered.'))


class TaskForm(Form):
	title = StringField(lazy_gettext('Title'), validators=[DataRequired()])
	description = PageDownField(lazy_gettext('Description'))
	worker = SelectField(lazy_gettext('Worker'), coerce=int)
	price = DecimalField(lazy_gettext('Price'))
	timelimit = DateTimeField(lazy_gettext('Timelimit'), display_format='%d.%m.%Y %H:%M')
	submit = SubmitField(lazy_gettext('Submit'))

	def __init__(self, *args, **kwargs):
		super(TaskForm, self).__init__(*args, **kwargs)
		self.worker.choices = [(user.id, user.fullname)
								for user in User.query.order_by(User.fullname).all()]


class ThingForm(Form):
	name = StringField(lazy_gettext('Title'), validators=[DataRequired()])


class ThingsForm(Form):
	things = FieldList(FormField(ThingForm), min_entries=5, widget=TableWidget())