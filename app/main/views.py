from flask import render_template, flash, redirect, abort, session, url_for, request, g, current_app
from flask.ext.login import login_user, logout_user, current_user, login_required
from sqlalchemy import or_
from .. import db, lm
from ..models import User, Permission, Group, Task, Thing, TypeOfThing
from . import main
from ..decorators import permission_required
from .forms import EditProfileForm, EditProfileAdminForm, TaskForm, ThingsForm, SelectProductsForm
from app import babel
from flask.ext.babelex import gettext, lazy_gettext


@main.route('/')
@main.route('/index')
def index():
	if current_user.is_authenticated:
		num_of_tasks = current_user.tasks_to_do.filter_by(state=0).count()
		return render_template("index.html",
							   title='Home',
							   user=current_user,
							   num_of_tasks=num_of_tasks)
	else:
		return render_template("index.html",
								title='Home',
								user=current_user)



@main.route('/user/<nickname>')
@login_required
def user(nickname):
	user = User.query.filter_by(nickname=nickname).first()
# TODO: 404 instead if redirect
	if user is None:
		flash('User {} not found.'.format(nickname))
		abort(404)
		return redirect(url_for('.index'))
	page = request.args.get('page', 1, type=int)
	pagination = user.tasks_to_do.order_by(Task.timelimit.desc()).paginate(
		page, per_page=current_app.config['FLASKY_ELEMENTS_PER_PAGE'] or None,
		error_out=False
	)
	tasks = pagination.items
	return render_template('user.html',
						   user=user,
						   tasks=tasks,
						   pagination=pagination)



@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm()
	if form.validate_on_submit():
		pass
	return render_template('edit_profile.html', form=form)



@main.route('/edit-profile/<nickname>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ADMINISTRATING)
def edit_profile_admin(nickname):
	user = User.query.filter_by(nickname=nickname).first()
	if user is None:
		abort(404)
	form = EditProfileAdminForm(user=user)
	if form.validate_on_submit():
		user.nickname = form.nickname.data
		user.fullname = form.fullname.data
		user.email = form.email.data
		user.group = Group.query.get(form.group.data)
		db.session.add(user)
		db.session.commit()
		flash('The profile had been updated successfully.', category='success')
		return redirect(url_for('.user', nickname=user.nickname))
	form.nickname.data = form.nickname.data or user.nickname
	form.fullname.data = form.fullname.data or user.fullname
	form.email.data = form.email.data or user.email
	form.group.data = form.group.data or user.group_id
	return render_template('edit_profile.html', form=form, user=user)


@main.route('/new-task', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.USER_M)
def add_new_task():
	form = TaskForm()
	if current_user.is_allowed(Permission.USER_M) and \
			form.validate_on_submit():
		task = Task(title=form.title.data,
					description=form.description.data,
					assigned_to=form.worker.data,
					manager=current_user._get_current_object(),
					timelimit=form.timelimit.data,
					price=form.price.data)
		db.session.add(task)
		worker_nickname = task.worker.nickname
		db.session.commit()
		flash('The task has been added', category='success')
		return redirect(url_for('.user', nickname=worker_nickname))
	return render_template('new_task.html', form=form)


@main.route('/edit-task/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_task(id):
	task = Task.query.get_or_404(id)
	if current_user != task.manager and \
			not current_user.is_allowed(Permission.ADMINISTRATING):
		abort(403)
	current_worker = task.worker
	form = TaskForm()
	if form.validate_on_submit():
		task.title = form.title.data
		task.description = form.description.data
		task.assigned_to = form.worker.data
		task.timelimit = form.timelimit.data
		task.price = form.price.data
		db.session.add(task)
		db.session.commit()
		flash('The task has been updated', category='success')
		return redirect(url_for('.user', nickname=current_worker.nickname))
	form.title.data = task.title
	form.description.data = task.description
	form.worker.data = task.assigned_to
	form.timelimit.data = task.timelimit
	form.price.data = task.price
	return render_template('edit_task.html', form=form)



@main.route('/task/<int:id>')
@login_required
def task(id):
	task = Task.query.get_or_404(id)
	return render_template('task.html', task=task)


@main.route('/delete-task/<int:id>')
@login_required
def delete_task(id):
	task = Task.query.get_or_404(id)
	worker_nickname = task.worker.nickname
	if current_user != task.manager and \
			not current_user.is_allowed(Permission.ADMINISTRATING):
		abort(403)
	task.delete()
	db.session.commit()
	flash('The task has deleted', category='success')
	return redirect(url_for('.user', nickname=worker_nickname))


@main.route('/depot')
@login_required
@permission_required(Permission.DEPOT_M)
def depot():
	page = request.args.get('page', 1, type=int)
	pagination = Thing.query.order_by(Thing.name).paginate(
		page, per_page=current_app.config['FLASKY_ELEMENTS_PER_PAGE'] or None,
		error_out=False
	)
	things = pagination.items
	return render_template('depot.html',
						   things=things,
						   pagination=pagination)

@main.route('/products')
@login_required
@permission_required(Permission.BASIC)
def products():
	page = request.args.get('page', 1, type=int)
	print(Thing.query.join(TypeOfThing).filter_by(assembled=1).first())
	pagination = Thing.query.join(TypeOfThing).filter_by(assembled=1).order_by(Thing.name).paginate(
		page, per_page=current_app.config['FLASKY_ELEMENTS_PER_PAGE'] or None,
		error_out=False
	)
	products = pagination.items
	return render_template('products.html',
						   products=products,
						   pagination=pagination)


@main.route('/product/<int:id>')
@login_required
def product(id):
	product = Thing.query.get_or_404(id)
	return render_template('product.html', product=product)

@main.route('/depot/new-item', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEPOT_M)
def new_thing():
	if request.method == 'POST':
		if 'add_entry' in request.form:
			form = ThingsForm()
			form.data = request.form
			form.append_entry()
			return render_template('new_thing.html', form=form)
	else:
		form = ThingsForm()
		return render_template('new_thing.html', form=form)
	return render_template('index.html')

	# TODO: Call to mind what is this?
	# if form.validate_on_submit():
	# 	task = Task(title=form.title.data,
	# 				description=form.description.data,
	# 				assigned_to=form.worker.data,
	# 				manager=current_user._get_current_object(),
	# 				timelimit=form.timelimit.data,
	# 				price=form.price.data)
	# 	db.session.add(task)
	# 	worker_nickname = task.worker.nickname
	# 	db.session.commit()
	# 	flash('The task has been added', category='success')
	# 	return redirect(url_for('.user', nickname=worker_nickname))


@main.route('/depot/analytics', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEPOT_M)
def depot_analytics():
	form = SelectProductsForm(request.form)

	if form.validate_on_submit():
		numbers = [int(n) for n in form.number.data.split(' ')]
		if len(numbers) != len(form.products.data):
			flash('Количество аппаратов и характеризующих их числел не совпадает', category='error')
		else:
			np = {}
			products = Thing.query.filter(Thing.id.in_(form.products.data)).all()
			for product, number in zip(products, numbers):
				for part in product.consist_of:
					if part.part.id in np:
						np[part.part.id] += part.amount*number
					else:
						np[part.part.id] = part.amount*number
			stock_p = Thing.query.filter(Thing.id.in_(np.keys())).all()
			success = True
			plenty = True
			for p in stock_p:
				if (p.stock-np[p.id]) < 0:
					success = False
				elif (p.stock-np[p.id]) < p.stock/10:
					plenty = False
				if not success and not plenty:
					break
			for part in stock_p:
				print (part.name, part.stock)
			return render_template("analytics_result.html", np=np, stock_p=stock_p, success=success, plenty=plenty)


	return render_template("analytics.html", form=form)


@main.route('/buyers')
@login_required
@permission_required(Permission.DEPOT_M)
def buyers():
	return render_template('buyers.html')


@babel.localeselector
def get_locale():
	print(request.accept_languages.best_match(current_app.config.get('LANGUAGES').keys()))
	return request.accept_languages.best_match(current_app.config.get('LANGUAGES').keys())



@main.before_app_request
def before_request():
	g.user = current_user


@lm.user_loader
def load_user(id):
	return User.query.get(int(id))

