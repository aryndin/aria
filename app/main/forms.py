from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, PasswordField, SubmitField, SelectField
from wtforms.validators import Length, DataRequired, Regexp, ValidationError
from ..models import Group, User


class EditProfileForm(Form):
	pass


class EditProfileAdminForm(Form):
	nickname = StringField('Nickname (login)', validators=[
		DataRequired(), Length(1, 64), Regexp('^^[a-zA-Z0-9_-]+$', 0,
										  'Usernames must have only letters,'
										  'numbers, dots or underscores'
	)])
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

	def validate_username(self, field):
		if field.data != self.user.nickname and \
				User.query.filter_by(nickname=field.data).first():
			raise ValidationError('Nickname is already registered.')