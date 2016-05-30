from flask.ext.admin.form import DateTimeField, DateTimePickerWidget, DatePickerWidget
from flask.ext.pagedown.fields import PageDownField
from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, PasswordField, SubmitField, SelectField, DecimalField
from wtforms.ext.dateutil.fields import DateField
from wtforms.validators import DataRequired, Email

class AssebledChartForm(Form):
	date_from = DateField('From', widget=DatePickerWidget())
	date_to = DateField('To', widget=DatePickerWidget())
	submit = SubmitField('Submit')
