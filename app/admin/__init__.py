from app import models, db
from flask.ext.babelex import gettext, lazy_gettext
from .views import MyAdminIndexView, AnalyticsView, UserModelView, TaskModelView, ThingModelView, ProductModelView, \
	GroupModelView, ShipmentModelView, SupplierModelView
from flask.ext.admin import Admin
from flask_admin.contrib.sqla import ModelView

flaskadmin = Admin(name='Flasky', template_mode='bootstrap3', index_view=MyAdminIndexView(),
				   base_template='admin/mymaster.html')
flaskadmin.add_views(UserModelView(models.User, db.session, category=lazy_gettext('Database')),
					 TaskModelView(models.Task, db.session, category=lazy_gettext('Database')),
					 ThingModelView(models.Thing, db.session, category=lazy_gettext('Database')),
					 ProductModelView(models.Product, db.session, category=lazy_gettext('Database')),
					 GroupModelView(models.Group, db.session, category=lazy_gettext('Database')),
					 SupplierModelView(models.Supplier, db.session, category=lazy_gettext('Database')),
					 ShipmentModelView(models.Shipment, db.session, category=lazy_gettext('Database')))

flaskadmin.add_view(AnalyticsView(name=lazy_gettext('Analytics'), endpoint='analytics'))
#
#
# class AView(BaseView):
#     @expose('/')
#     def index(self):
#         return self.render('admin/notindex.html')
#
# flaskadmin.add_view(AView(name='A'))