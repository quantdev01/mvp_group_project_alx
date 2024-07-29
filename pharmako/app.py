# Store this code in 'app.py' file

from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'pharmaco_db'

mysql = MySQL(app)

# Home page / landing page
@app.route('/')
@app.route('/landing_page')
def landing_page():
	return render_template('landing-page.html')

@app.route('/blog_page')
def blog_page():
	return render_template('blog-page.html')

@app.route('/about_us')
def about_us():
	return render_template('about-us.html')

@app.route('/login', methods =['GET', 'POST'])
def login():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']

		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password, ))
		account = cursor.fetchone()
		if account and check_password_hash(account['password'], password):
			session['loggedin'] = True
			session['id'] = account['id']
			session['username'] = account['username']
			msg = 'Logged in successfully !'
			return render_template('reach-us.html')
		else:
			msg = 'Incorrect username / password !'
	return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('login'))

@app.route('/nav_footer')
def nav_footer():
	return render_template('nav-footer.html')

@app.route('/signup', methods =['GET', 'POST'])
def signup():
	msg = ''
	# ! and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'age' in request.form
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		confirm_password = request.form['confirm_password']
		email = request.form['email']
		age = request.form['age']

		if (password != confirm_password):
			msg = 'Passwords do not match!'
			return render_template('signup.html', msg=msg)
		
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
		account = cursor.fetchone()
		if account:
			msg = 'Account already exists !'
			return render_template('login.html')
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'Username must contain only characters and numbers !'
		elif not username or not password or not email:
			msg = 'Please fill out the form !'
		else:
			# test
			hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
			cursor.execute('INSERT INTO accounts (username, password, email, age) VALUES (%s, %s, %s, %s)', (username, hashed_password, email, age))

			mysql.connection.commit()
			msg = 'You have successfully registered !'
			return render_template('login.html')
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('signup.html', msg=msg)

if __name__ == "__main__":
	app.run()