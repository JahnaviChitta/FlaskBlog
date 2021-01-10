import os
from os import urandom #instead of 'secrets' module
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from Hello import app, db, bcrypt, mail
from Hello.forms import (RegistrationForm, LoginForm, UpdateAccountForm, 
						PostForm, CheckHemoForm, RequestResetForm, ResetPasswordForm)
from Hello.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from Hello.hCode import get_result
from flask_mail import Message
@app.route('/')

@app.route("/home")
def home():
	page = request.args.get('page', 1, type = int)
	posts = Post.query.order_by(Post.date_posted.desc()).paginate(page = page, per_page = 5)
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

def result_of_picture(form_picture):
	im = Image.open(form_picture)
	
	im.thumbnail((400, 400))
	pix = im.load()
	result = get_result(im, pix)
	a = (14.639534353807022 + (result*(1.1083761675274781e-08)))
	flash("Your Hemoglobin level is : {}".format(a))
	if a < 9 :
	    flash("Results show you might have ANEMIA!!!\nEat plenty of iron-rich foods, such as tofu, green and leafy vegetables, lean red meat, lentils, beans and iron-fortified cereals and breads.\nEat and drink vitamin C-rich foods and drinks.\n Avoid drinking tea or coffee with your meals, as they can affect iron absorption. ", 'danger')
	elif a > 9 and a < 12 :
	    flash("Low levels of hemoglobin.\nIncreasing the intake of iron-rich foods (eggs, spinach, artichokes, beans, lean meats, and seafood) and foods rich in cofactors (such as vitamin B6, folic acid, vitamin B12, and vitamin C) are important for maintaining normal hemoglobin levels.", 'danger')
	elif a > 12 :
		flash("You are perfectly alright :) ", 'success')


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

@app.route("/check_hemo", methods = ['GET', 'POST'])
@login_required
def checkHemo():
	form = CheckHemoForm()
	if form.validate_on_submit():
		if form.picture.data:
			#picture_file = save_picture(form.picture.data)
			#current_user.image_file = picture_file
			flash("Your Haemoglobin result has arrived! ", 'success')
			result_of_picture(form.picture.data)
	return render_template('checkHemo.html', title = 'Check Haemoglobin', form = form)


@app.route("/post/new", methods = ['GET', 'POST'])
@login_required
def new_post():
	form = PostForm()
	if form.validate_on_submit():
		post = Post(title = form.title.data, content = form.content.data, author = current_user)
		db.session.add(post)
		db.session.commit()
		flash("Your post has been created!", 'success')
		return redirect(url_for('home'))
	return render_template('create_post.html', title = 'New post', form = form, legend = 'New Post')



@app.route("/post/<int:post_id>")
def post(post_id):
	post = Post.query.get_or_404(post_id) # if post is not there, gives 404 page
	return render_template('post.html', title = post.title, post = post)

@app.route("/post/<int:post_id>/update", methods = ['GET', 'POST'])
@login_required
def update_post(post_id):
	post = Post.query.get_or_404(post_id) # if post is not there, gives 404 page
	if post.author != current_user:
		abort(403) # is http response for a forbidden route
	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		post.content = form.content.data
		db.session.commit()
		flash("Your post has been updated!", 'success')
		return redirect(url_for('post', post_id = post.id))
	elif request.method == 'GET':
		form.title.data = post.title
		form.content.data = post.content	
	return render_template('create_post.html', title = 'Update post', form = form, legend = 'Update Post')

@app.route("/post/<int:post_id>/delete", methods = ['POST'])
@login_required
def delete_post(post_id):
	post = Post.query.get_or_404(post_id) # if post is not there, gives 404 page
	if post.author != current_user:
		abort(403) # is http response for a forbidden route	
	db.session.delete(post)
	db.session.commit()
	flash("Your post has been deleted!", 'success')
	return redirect(url_for('home'))


@app.route("/user/<string:username>")
def user_posts(username):
	page = request.args.get('page', 1, type = int)
	user = User.query.filter_by(username=username).first_or_404() #get the first user with the username, if u get a None then return 404 error.
	posts = Post.query.filter_by(author = user)\
		.order_by(Post.date_posted.desc())\
		.paginate(page = page, per_page = 5)
	return render_template("user_posts.html", posts=posts, user = user)

def send_reset_email(user):
	token = user.get_reset_token()
	msg = Message('Password Reset Request', sender = 'noreply@demo.com', recipients = [user.email])
	msg.body = "To reset your password, visit the following link : {} If you did not make this request then simply ignore this email and no change".format(url_for('reset_token', token = token, _external = True))
	mail.send(msg) ## this one corey did not say(additional)

@app.route("/reset_password", methods = ['GET', 'POST'])
def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RequestResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email = form.email.data).first()
		send_reset_email(user)
		flash('An email has been sent with instructions to reset your password', 'info')
		return redirect(url_for('login'))
	return render_template('reset_request.html', title = 'Reset Password', form = form)

@app.route("/reset_password/<token>", methods = ['GET', 'POST'])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	user = User.verify_reset_token(token)
	if user is None:
		flash('That is an invalid or expired token', 'warning')
		return redirect(url_for('reset_request'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') #to store the password entered bu user in table by hashing it.
		user.password = hashed_password
		db.session.commit() #commiting those changes
		flash("Your Password has been changed ! You are now able to log in", 'success')
		return redirect(url_for('login'))
	return render_template('reset_token.html', title = 'Reset Password', form = form)
