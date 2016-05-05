from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email

class LoginForm(Form):
	login = StringField('Login', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Remember me', default=False)
	submit = SubmitField('Log in')
