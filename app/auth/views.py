from flask import render_template, flash, redirect, abort, session, url_for, request, g, current_app
from flask.ext.login import login_user, logout_user, current_user, login_required
from .. import db, lm
from app.models import User
from .forms import LoginForm
from . import auth


@auth.route('/login', methods=['GET', 'POST'])
def login():
#?    if g.user is not None and g.user.is_authenticated:
#?        return redirect(url_for('.index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(nickname=form.login.data).first()


		if user is not None and user.verify_password(form.password.data):
			print(user.nickname)
			print(type(user.nickname))
			login_user(user, form.remember_me.data)
			return redirect(request.args.get('next') or url_for('main.index'))
		flash('Invalid username or/and password', category='error')
	return render_template('auth/login.html',
						   title='Sign In',
						   form=form,
						   providers=current_app.config['OPENID_PROVIDERS'])


@auth.route('/logout')
def logout():
	if current_user.is_authenticated:
		logout_user()
		flash('You have been logged out', category='success')
	return redirect(url_for('main.index'))