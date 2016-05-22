from flask.ext.admin import expose, AdminIndexView, BaseView
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.login import login_user, logout_user, current_user, login_required
import json
from flask import request
from sqlalchemy import and_
from .forms import AssebledChartForm
import datetime
from app import models




class MyAdminIndexView(AdminIndexView):
	@expose('/')
	@login_required
	def index(self):
		return super(MyAdminIndexView, self).index()


class UserModelView(ModelView):
	column_labels = dict(nickname='Логин', _email='Адрес электронной почты',
						 tasks_to_do='Задачи на выполнение', assigned_tasks='Созданные задания',
						 fullname='ФИО', credit='Остаток средств',
						 group='Группа', products='Собранная продукция')


class TaskModelView(ModelView):
	column_labels = dict(title='Заголовок', description='Описание',
						 description_html='HTML-описание', timestamp='Дата создания',
						 timelimit='Срок выполнения', price='Стоимость',
						 state='Состояние', worker='Исполнитель',
						 manager='Назначивший')


class ThingModelView(ModelView):
	column_labels = dict(shipments='Поставки', consist_of='Состоит из',
						 part_of='Является частью', products='Список продукции данного типа',
						 name='Название', stock='Остаток на складе',
						 зrice='Цена', type='Тип', measure='Единица измерения')


class ProductModelView(ModelView):
	column_labels = dict(id='Серийный номер', product='Название продукта',
						 assembler='Сборщик', assembly_date='Дата сборки')
	column_list = ('id', 'product', 'assembly_date')


class GroupModelView(ModelView):
	column_labels = dict(name='Имя группы', access_level='Уровень доступа', users='Пользователи')


class SupplierModelView(ModelView):
	column_labels = dict(name='Имя', shipments='Список поставок')


class ShipmentModelView(ModelView):
	column_labels = dict(date='Дата поставки', supplier='Поставщик', things='Перечень товаров')


class AnalyticsView(BaseView):
	@expose('/', methods=['GET', 'POST'])
	def index(self):
		data = json.dumps({
			"labels": ["January", "February", "March", "April", "May", "June", "July"],
			"datasets": [
				{
					"label": "2014 год",
					"data": [65, 59, 80, 81, 56, 35, 34],
					"backgroundColor" : "rgba(155,99,132,0.3)"
				},
				{
					"label": "2015 год",
					"data": [35, 79, 30, 51, 46, 35, 24],
					"backgroundColor": "rgba(99,170,132,0.3)"
				}
			]
		})
		# labels = []
		# print(request.args.get('form'))
		# if request.args.get('form') == 'acf':
		# 	form = AssebledChartForm()
		# 	if form.validate_on_submit():
		#
		# 		date_from = d1 = form.date_from.data
		# 		date_to = form.date_to.data
		# 		if date_from.month == 12:
		# 			d2 = date_from.replace(year=date_from.year+1,
		# 								  month=1,
		# 								  day=1)
		# 		else:
		# 			d2 = date_from.replace(month=date_from.month+1,
		# 								  day=1)
		# 		labels.append(date_from.strftime('%B'))
		# 		d3 = datetime.date(1990,1,1)
		# 		d4 = datetime.date(2020,1,1)
		# 		print (models.Product.query.filter(and_(models.Product.assembly_date>d3,models.Product.assembly_date<d4)).count())
		# 		while d2 < date_to:
		# 			labels.append(d2.strftime('%B'))
		#
		# 			if d.month == 12:
		# 				d = d.replace(year=date_from.year + 1,
		# 							  month=1,
		# 							  day=1)
		# 			else:
		# 				d = d.replace(month=d.month + 1,
		# 									  day=1)
		# 		else:
		# 			pass
		# 		print(labels)
		#
		#
		# 	return self.render('admin/analytic.html', form=form)

		return self.render('admin/assembled_bar_chart.html', data=data)

