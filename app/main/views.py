from flask import render_template, flash, redirect, abort, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from .. import db, lm
from ..models import User, Permission, Group
from . import main
from ..decorators import permission_required
from .forms import EditProfileForm, EditProfileAdminForm


@main.route('/')
@main.route('/index')
def index():
	user = g.user
	tasks = [  # fake array of posts
		{
			'state': 1,
			'author': {'nickname': 'John'},
			'body': 'Beautiful day in Portland!'
		},
		{
			'state': 0,
			'author': {'nickname': 'Susan'},
			'body': 'The Avengers movie was so cool!'
		}
	]
	return render_template("index.html",
						   title='Home',
						   user=user,
						   tasks=tasks)



@main.route('/user/<nickname>')
@login_required
def user(nickname):
	user = User.query.filter_by(nickname=nickname).first()
# TODO: 404 instead if redirect
	if user is None:
		flash('User {} not found.'.format(nickname))
		abort(404)
		return redirect(url_for('.index'))
	tasks = [
		{'author': user, 'body': 'Test post #1'},
		{'author': user, 'body': 'Test post #2'}
	]
	return render_template('user.html',
						   user=user,
						   tasks=tasks)



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
		user.group = Group.query.get(form.group.data)
		db.session.add(user)
		db.session.commit()
		flash('The profile had been updated successfully.', category='success')
		return redirect(url_for('.user', username=user.nickname))
	form.nickname.data = user.nickname
	form.fullname.data = user.fullname
	form.group.data = user.group_id
	return render_template('edit_profile.html', form=form, user=user)



@main.before_app_request
def before_request():
	g.user = current_user


@lm.user_loader
def load_user(id):
	return User.query.get(int(id))