from flask.ext.admin.form import DateTimeField, DateTimePickerWidget, DatePickerWidget
from flask.ext.babelex import lazy_gettext
from flask.ext.pagedown.fields import PageDownField
from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, PasswordField, SubmitField, SelectField, DecimalField, FieldList, \
	FormField
from wtforms.ext.dateutil.fields import DateField
from wtforms.validators import DataRequired, Email, Length, Regexp


class AssebledChartForm(Form):
	date_from = DateField('From', widget=DatePickerWidget())
	date_to = DateField('To', widget=DatePickerWidget())
	submit = SubmitField('Submit')

class PriceAmountForm(Form):
	price = StringField(lazy_gettext('price'), validators=[DataRequired(),
														  Length(1, 64),
														  Regexp('^[0-9]+$', 0,
																 'only numbers please')])

	amount = StringField(lazy_gettext('amount'), validators=[DataRequired(),
														   Length(1, 64),
														   Regexp('^[0-9]+$', 0,
																  'only numbers please')])
class PAF(Form):
	paf = FieldList(FormField(PriceAmountForm))