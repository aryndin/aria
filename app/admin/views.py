from flask.ext.admin import expose, AdminIndexView, BaseView
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


class AnalyticsView(BaseView):
	@expose('/', methods=['GET', 'POST'])
	def index(self):
		data = json.dumps({
			"labels": ["January", "February", "March", "April", "May", "June", "July"],
			"datasets": [
				{
					"data": [65, 59, 80, 81]
				},
				{
					"data": [37, 96, 25, 45]
				}
			]
		})
		labels = []
		print(request.args.get('form'))
		if request.args.get('form') == 'acf':
			form = AssebledChartForm()
			if form.validate_on_submit():

				date_from = d1 = form.date_from.data
				date_to = form.date_to.data
				if date_from.month == 12:
					d2 = date_from.replace(year=date_from.year+1,
										  month=1,
										  day=1)
				else:
					d2 = date_from.replace(month=date_from.month+1,
										  day=1)
				labels.append(date_from.strftime('%B'))
				d3 = datetime.date(1990,1,1)
				d4 = datetime.date(2020,1,1)
				print (models.Product.query.filter(and_(models.Product.assembly_date>d3,models.Product.assembly_date<d4)).count())
				while d2 < date_to:
					labels.append(d2.strftime('%B'))

					if d.month == 12:
						d = d.replace(year=date_from.year + 1,
									  month=1,
									  day=1)
					else:
						d = d.replace(month=d.month + 1,
											  day=1)
				else:
					pass
				print(labels)


			return self.render('admin/analytic.html', form=form)

		return self.render('admin/analytic.html', data=data)

