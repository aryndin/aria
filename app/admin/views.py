from app.models import User, Product, Order, OrderList
from flask.ext.admin import expose, AdminIndexView, BaseView
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.contrib.sqla.validators import Unique
from flask.ext.admin.form import Select2Widget, Select2TagsWidget, Select2Field
from flask.ext.babelex import lazy_gettext
from wtforms import fields, SelectMultipleField, StringField
from flask.ext.admin._compat import text_type, as_unicode
from wtforms import widgets
from flask.ext.admin.model import BaseModelView
from flask.ext.login import login_user, logout_user, current_user, login_required
import simplejson
from flask import request
from decimal import Decimal
from sqlalchemy import and_
from .forms import AssebledChartForm
from datetime import datetime, timedelta
from wtforms.validators import Length, DataRequired, Regexp, ValidationError, Email
from app import models, db
import sqlalchemy as sa
from dateutil import rrule
from itertools import groupby




class MyAdminIndexView(AdminIndexView):
	@expose('/')
	@login_required
	def index(self):
		test = 'test'
		date_to = datetime.now()
		date_from = date_to-timedelta(weeks=1)
		print(date_from)

		result = db.session.query(sa.func.day(Order.date_of_payment), sa.func.sum(OrderList.amount))\
			.join(OrderList)\
			.filter(Order.date_of_payment.between(date_from, date_to)) \
			.group_by(sa.func.day(Order.date_of_payment)).all()
		data = []
		labels = []
		print(result)
		if result == []:
			data = labels = []
		else:
			i = 0
			total = 0
			for dt in rrule.rrule(rrule.DAILY, dtstart=date_from, until=date_to):
				labels.append(dt.strftime('%a'))  # labels are appended anyway
				if i < len(result) and result[i][0] == dt.day:
					data.append(result[i][1])
					total += result[i][1]
					i += 1
				else:
					data.append(0)
			print(labels)
			data = simplejson.dumps({
				"labels": labels,
				"datasets": [
					{
						"label": "Продано",
						"data": data,
						"backgroundColor": "rgba(0,0,180,0.5)"
					}
				]
			})
			self._template_args['data'] = data
			self._template_args['total'] = total
		return super(MyAdminIndexView, self).index()


class UserModelView(ModelView):
	column_labels = dict(nickname='Логин', email='Адрес электронной почты',
						 tasks_to_do='Задачи на выполнение', assigned_tasks='Созданные задания',
						 fullname='ФИО', credit='Остаток средств',
						 group='Группа', products='Собранная продукция')




	form_extra_fields = {
		'f_email': StringField('Email', validators=[Email(), Unique(db.session,
																	models.User,
																	models.User.email)])
	}

	def on_model_change(self, form, model, is_created):
		if form.f_email.data != model.email and \
				User.query.filter_by(email=form.f_email.data).first():
			raise ValidationError(lazy_gettext('Email is already registered.'))
		model.email = form.f_email.data

	def on_form_prefill(self, form, id):
		form.f_email.data = models.User.query.filter_by(nickname=form.nickname.data).first().email
		print(form.data, id)



class TaskModelView(ModelView):
	form_columns = ('title', 'description',
					'timestamp', 'timelimit', 'price',
					'state', 'worker', 'manager')

	column_labels = dict(title='Заголовок', description='Описание',
						 description_html='HTML-описание', timestamp='Дата создания',
						 timelimit='Срок выполнения', price='Стоимость',
						 state='Состояние', worker='Исполнитель',
						 manager='Назначивший')


class ThingModelView(ModelView):
	column_labels = dict(shipments='Поставки', consist_of='Состоит из',
						 part_of='Является частью', products='Список продукции данного типа',
						 name='Название', stock='Остаток на складе',
						 price='Цена', type='Тип', measure='Единица измерения')


class ProductModelView(ModelView):
	column_labels = dict(id='Серийный номер', thing='Название продукта',
						 assembler='Сборщик', assembly_date='Дата сборки')
	column_list = ('id', 'thing', 'assembly_date')


class GroupModelView(ModelView):
	column_labels = dict(name='Имя группы', access_level='Уровень доступа', users='Пользователи')


class SupplierModelView(ModelView):
	column_labels = dict(name='Имя', shipments='Список поставок')


class ShipmentModelView(ModelView):
	column_labels = dict(date='Дата поставки', supplier='Поставщик', things='Перечень товаров')


class BuyerModelView(ModelView):
	column_labels = dict(orders='Список заказов', fullname='Имя/Компания', phone_number='Номер телефона')


class OrderModelView(ModelView):
	column_labels = dict()


class AnalyticsView(BaseView):
	form_create_rules = ('date_to')

	@expose('/', methods=['GET', 'POST'])
	def index(self):
		form = AssebledChartForm()
		labels = []
		print(request.args.get('form'))
		if request.args.get('form') == 'acf':
			form = AssebledChartForm()
			if form.validate_on_submit():

				date_from = form.date_from.data
				date_to = form.date_to.data
				result = db.session.query(sa.func.month(Product.assembly_date), sa.func.year(Product.assembly_date), sa.func.count())\
						  .filter(Product.assembly_date.between(date_from,date_to))\
						  .group_by(sa.func.month(Product.assembly_date), sa.func.year(Product.assembly_date)).all()
				data = []
				labels = []
				if result == []:
					data = labels = []

				else:
					i = 0
					for dt in rrule.rrule(rrule.MONTHLY, dtstart=date_from, until=date_to):
						labels.append(dt.strftime('%B'))  # labels are appended anyway
						if result[i][0] == dt.month and result[i][1] == dt.year:
							data.append(result[i][2])

							i += 1
						else:
							data.append(0)
					print(labels)
					data = simplejson.dumps({
						"labels": labels,
						"datasets": [
							{
								"label": "2014 год",
								"data": data,
								"backgroundColor": "rgba(0,0,180,0.5)"
							}
						]
					})
					total = db.session.query(sa.func.year(Product.assembly_date), sa.func.count())\
						  .filter(Product.assembly_date.between(date_from,date_to))\
						  .group_by(sa.func.year(Product.assembly_date)).all()
					return self.render('admin/assembled_bar_chart.html', data=data, total=total)


				#print(Product.query.filter(Product.assembly_date.between(date_from, date_to)).group_by(sa.func.month(Product.assembly_date)).all())

				# labels.append(date_from.strftime('%B'))
				# d3 = datetime.date(1990,1,1)
				# d4 = datetime.date(2020,1,1)
				# print (models.Product.query.filter(and_(models.Product.assembly_date>d3,models.Product.assembly_date<d4)).count())
				# while d2 < date_to:
				# 	labels.append(d2.strftime('%B'))
				#
				# 	if d.month == 12:
				# 		d = d.replace(year=date_from.year + 1,
				# 					  month=1,
				# 					  day=1)
				# 	else:
				# 		d = d.replace(month=d.month + 1,
				# 							  day=1)
				# else:
				# 	pass
				# print(labels)
			return self.render('admin/analytic.html', form=form)

		if form.validate_on_submit():

			date_from = d1 = form.date_from.data
			date_to = form.date_to.data
			print(date_from, type(date_from))
		return self.render('admin/analytic.html', form=form)
		#return self.render('admin/assembled_bar_chart.html', data=data)


class Select2MultipleWidget():
	"""
	(...)

	By default, the `_value()` method will be called upon the associated field
	to provide the ``value=`` HTML attribute.
	"""

	input_type = 'select2multiple'

	def __call__(self, field, **kwargs):
		kwargs.setdefault('data-choices', self.json_choices(field))
		kwargs.setdefault('type', 'hidden')
		return super(Select2MultipleWidget, self).__call__(field, **kwargs)

	@staticmethod
	def json_choices (field):
		objects = ('{{"id": {}, "text": "{}"}}'.format(*c) for c in field.iter_choices())
		return '[' + ','.join(objects) + ']'

class Select2MultipleField(fields.SelectMultipleField):
    """
        `Select2 <https://github.com/ivaynberg/select2>`_ styled select widget.

        You must include select2.js, form.js and select2 stylesheet for it to
        work.

        This is a slightly altered derivation of the original Select2Field.
    """
    widget = Select2Widget(multiple=True)

    def __init__(self, label=None, validators=None, coerce=text_type,
                 choices=None, allow_blank=False, blank_text=None, **kwargs):
        super(Select2MultipleField, self).__init__(
            label, validators, coerce, choices, **kwargs
        )
        self.allow_blank = allow_blank
        self.blank_text = blank_text or ' '

    def iter_choices(self):
        if self.allow_blank:
            yield ('__None', self.blank_text, self.data is [])

        for value, label in self.choices:
            yield (value, label, self.coerce(value) in self.data)

    def process_data(self, value):
        if not value:
            self.data = []
        else:
            try:
                self.data = []
                for v in value:
                    self.data.append(self.coerce(v[0]))
            except (ValueError, TypeError):
                self.data = []

    def process_formdata(self, valuelist):
        if valuelist:
            if valuelist[0] == '__None':
                self.data = []
            else:
                try:
                    self.data = []
                    for value in valuelist[0].split(','):
                        self.data.append(self.coerce(value))
                except ValueError:
                    raise ValueError(self.gettext('Invalid Choice: could not coerce {}'.format(value)))

    def pre_validate(self, form):
        if self.allow_blank and self.data is []:
            return

        super(Select2MultipleField, self).pre_validate(form)

    def _value (self):
        return ','.join(map(str, self.data))


class SalesModelView(ModelView):
	form_columns = ('things_list',)
	form_extra_fields = {
		'things_list': Select2MultipleField(
			'Things',
			choices = [(group.id, group.name) for group in models.Thing.query.order_by(models.Thing.name).all()],
			coerce=int, widget=Select2Widget(multiple=True)
		),
	}

	def on_model_change(self, form, model, is_created=False):
		for index, id in enumerate(form.things_list.data):
			print(index, id)
		if not is_created:
			self.session.query(models.OrderList).filter_by(order=model).delete()
		#for index, id in enumerate(form.things_list.data):
		#	models.OrderList(order=model, thing_id=id)

	def __init__(self, session, **kwargs):
		print([(group.id, group.name) for group in models.Thing.query.order_by(models.Thing.name).all()])
		super(SalesModelView, self).__init__(models.Order, db.session, name='Sales', **kwargs)