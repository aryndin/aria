from app import models, db
from .views import MyAdminIndexView, AnalyticsView
from flask.ext.admin import Admin
from flask_admin.contrib.sqla import ModelView

flaskadmin = Admin(name='Flasky', template_mode='bootstrap3', index_view=MyAdminIndexView(),
				   base_template='admin/mymaster.html')
flaskadmin.add_views(ModelView(models.User, db.session, category='Database'),
					 ModelView(models.Task, db.session, category='Database'),
					 ModelView(models.Thing, db.session, category='Database'),
					 ModelView(models.Product, db.session, category='Database'))

flaskadmin.add_view(AnalyticsView(name='Analytics', endpoint='analytics'))
#
#
# class AView(BaseView):
#     @expose('/')
#     def index(self):
#         return self.render('admin/notindex.html')
#
# flaskadmin.add_view(AView(name='A'))