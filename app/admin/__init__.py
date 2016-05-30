from app import models, db
from flask.ext.babelex import gettext, lazy_gettext as _l
from flask import current_app
from .views import MyAdminIndexView, AnalyticsView, UserModelView, TaskModelView, ThingModelView, ProductModelView, \
	GroupModelView, ShipmentModelView, SupplierModelView, BuyerModelView, OrderModelView, SalesModelView
from flask.ext.admin import Admin
from flask_admin.contrib.sqla import ModelView

flaskadmin = Admin(name='Flasky', template_mode='bootstrap3', index_view=MyAdminIndexView(),
				   base_template='admin/mymaster.html')
flaskadmin.add_views(UserModelView(models.User, db.session, name=_l('User'), category=_l('Database')),
					 TaskModelView(models.Task, db.session, name=_l('Task'), category=_l('Database')),
					 ModelView(models.TaskType, db.session, name=_l('Type of task'), category=_l('Database')),
					 ModelView(models.TaskToAssemble, db.session, name=_l('Task to assemble'), category=_l('Database')),
					 ThingModelView(models.Thing, db.session, name=_l('Thing'), category=_l('Database')),
					 ProductModelView(models.Product, db.session, name=_l('Product'), category=_l('Database')),
					 GroupModelView(models.Group, db.session, name=_l('Group'), category=_l('Database')),
					 SupplierModelView(models.Supplier, db.session, name=_l('Supplier'), category=_l('Database')),
					 ShipmentModelView(models.Shipment, db.session, name=_l('Shipment'), category=_l('Database')),
					 BuyerModelView(models.Buyer, db.session, name=_l('Buier'), category=_l('Database')),
					 OrderModelView(models.Order, db.session, name=_l('Order'), category=_l('Database')),
					 ModelView(models.Invoice, db.session, name=_l('Invoice'), category=_l('Database')),
					 ModelView(models.OrderList, db.session, name=_l('Order list'), category=_l('Database')),
					 ModelView(models.TypeOfThing, db.session, name=_l('Type of thing'), category=_l('Database')),
					 ModelView(models.Measure, db.session, name=_l('Measure'), category=_l('Database')),
					 ModelView(models.ConsistOf, db.session, name=_l('Consist of'), category=_l('Database')))

flaskadmin.add_view(AnalyticsView(name=_l('Analytics'), endpoint='analytics'))


flaskadmin.add_view(SalesModelView(db.session, category=_l('Database'), endpoint='sasles'))
#
#
# class AView(BaseView):
#     @expose('/')
#     def index(self):
#         return self.render('admin/notindex.html')
#
# flaskadmin.add_view(AView(name='A'))