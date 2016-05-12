from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, PasswordField, SubmitField, SelectField, DecimalField, FieldList, \
	FormField
from wtforms.ext.dateutil.fields import DateTimeField
from flask.ext.pagedown.fields import PageDownField
from wtforms.validators import Length, DataRequired, Regexp, ValidationError, Email
from wtforms.widgets import TableWidget
from ..models import Group, User


class EditProfileForm(Form):
	pass


class EditProfileAdminForm(Form):
	nickname = StringField('Nickname (login)', validators=[
		DataRequired(), Length(1, 64), Regexp('^^[a-zA-Z0-9_-]+$', 0,
										  'Usernames must have only letters,'
										  'numbers, dots or underscores')
	])
	email = StringField('Email', validators=[DataRequired(), Length(1, 64),
											 Email()])
	fullname = StringField('Fullname', validators=[Length(6, 64)])
	group = SelectField('Group', coerce=int)
	submit = SubmitField('Submit')

	def __init__(self, user, *args, **kwargs):
		super(EditProfileAdminForm, self).__init__(*args, **kwargs)
		self.group.choices = [(group.id, group.name)
							  for group in Group.query.order_by(Group.name).all()]
		self.user = user

	def validate_email(self, field):
		if field.data != self.user.email and \
				User.query.filter_by(email=field.data).first():
			raise ValidationError('Email is already registered.')

	def validate_nickname(self, field):
		if field.data != self.user.nickname and \
				User.query.filter_by(nickname=field.data).first():
			raise ValidationError('Nickname is already registered.')


class TaskForm(Form):
	title = StringField('Title', validators=[DataRequired()])
	description = PageDownField('Description')
	worker = SelectField('Worker', coerce=int)
	price = DecimalField('Price')
	timelimit = DateTimeField('Timelimit', display_format='%d.%m.%Y %H:%M')
	submit = SubmitField('Submit')

	def __init__(self, *args, **kwargs):
		super(TaskForm, self).__init__(*args, **kwargs)
		self.worker.choices = [(user.id, user.fullname)
								for user in User.query.order_by(User.fullname).all()]


class ThingForm(Form):
	name = StringField('Title', validators=[DataRequired()])


class ThingsForm(Form):
	things = FieldList(FormField(ThingForm), min_entries=5, widget=TableWidget())