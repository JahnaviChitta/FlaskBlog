import os
from os import urandom #instead of 'secrets' module
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from Hello import app, db, bcrypt
from Hello.forms import RegistrationForm, LoginForm, UpdateAccountForm
from Hello.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required


posts = [
	{
		'author' : 'Sriram',
		'title' : 'Blog post 1',
		'content' : 'First post content',
		'date_posted' : '22 September, 2020'
	},
	{
		'author' : 'Jahnavi',
		'title' : 'Blog post 2',
		'content' : 'Second post content',
		'date_posted' : '30 November, 2020'
	}
]

@app.route('/')
@app.route("/home")

def home():
	return render_template("home.html", posts=posts)

@app.route("/about")
def about():
	return render_template("about.html", title='About')

@app.route("/register", methods = ['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') #to store the password entered bu user in table by hashing it.
		user = User(username = form.username.data, email = form.email.data, password = hashed_password) # creating user with entered username, password
		db.session.add(user) #adding that info to db
		db.session.commit() #commiting those changes
		flash("Your Account has been created {} ! You are now able to log in".format(form.username.data), 'success')
		return redirect(url_for('login'))

	return render_template('register.html', title = 'Register', form = form)

@app.route("/login", methods = ['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email = form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember = form.remember.data)
			next_page = request.args.get('next') #args is a dictionary, so in the url arguments, if there is 'next' then it returns something, and if there is no next, it return none.
			if next_page:
				return redirect(next_page)
			return redirect(url_for('home'))
		else:
			flash('Login Unsuccessful. Please check email and password', 'danger')
	return render_template('login.html', title = 'Login', form = form)

@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('home'))


def save_picture(form_picture):
	random_hex = urandom(8).hex() #random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext #filename = secret code + file extention
	picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn) #to save the path for this pic uploaded as profile pic
	output_size = (125, 125)
	i = Image.open(form_picture)
	i.thumbnail(output_size) #resizing an image
	i.save(picture_path) # save pic to system
	return picture_fn


@app.route("/account", methods = ['GET', 'POST'])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			current_user.image_file = picture_file
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash("Your account has been updated! ", 'success')
		return redirect(url_for('account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
	return render_template('account.html', title = 'Account', image_file = image_file, form = form)
