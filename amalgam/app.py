# import the Flask class from the flask module
from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify, copy_current_request_context
from functools import wraps
import os
from flask_sqlalchemy import SQLAlchemy
from amalgam.crawler.crawler import Crawler
import jsonpickle
import threading

from amalgam import database
from amalgam.delegate import delegate
from amalgam.models.models import Url, Crawl, User
from amalgam.progress_tracker import ProgressTracker
# from amalgam.progress_tracker import ProgressTracker


# def create_app():
# create the application object
app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = 'my precious'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///amalgam.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.database = "sample.db"
	# return app	

PROGRESS_TRACKER = ProgressTracker()


def check_db(app):
	if not os.path.isfile('./amalgam.db'):
		setup_database(app)


def setup_database(app):
	with app.app_context():
		# db.init_app(app)
		# db.create_all()
		# db.session.commit()
		pass

	# Create all tables if needed
	database.Base.metadata.create_all(database.engine)

	user = User(email='one@foo.com', password='one', name='one')
	delegate.user_create(user)

check_db(app)

# login required decorator
def login_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash("You need to login first.")
			return redirect(url_for('login'))		
	return wrap



# use decorators to link the function to a url
@app.route('/')
def index():
	return render_template('index.html')  # render a template


@app.route('/welcome')
def welcome():
	return render_template('welcome.html')  # render a template


# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST': 
		email = request.form['email']
		password = request.form['password']
		user = delegate.user_get_by_email_and_password(email, password)

		if user == None or False:
			error = 'Invalid Credentials. Please try again.'
		else:
			session['logged_in'] = True			
			session['user_id'] = user.id
			# session['progress_tracker'] = jsonpickle.encode(ProgressTracker())
			# progress_tracker = jsonpickle.decode(session['progress_tracker'])

			flash('You were just logged in!')
			return redirect(url_for('home'))
	return render_template('login.html', error=error)


@app.route('/logout')
@login_required
def logout():	
	session.pop('logged_in', None)
	session.pop('user_id', None)
	flash('You were just logged out!')
	return redirect(url_for('index'))
	

@app.route('/home')
@login_required
def home():
	return render_template('home.html')
	

@app.route('/sitemap')
@login_required
def sitemap():
	return render_template('sitemap.html')


@app.route('/crawl')
@login_required
def crawl():
	session = delegate.get_session()
	crawls = session.query(Crawl).all()	
	return render_template('crawl.html', crawls = crawls)


@app.route('/crawl.exe', methods=['GET', 'POST'])
@login_required
def crawl_exe():
	global PROGRESS_TRACKER

	@copy_current_request_context
	def notify(msg):
		crawlId = str(msg['crawlId'])		
		# progress = ProgressTracker._msg_to_progress(msg)
		# pj = jsonpickle.encode(progress)
		PROGRESS_TRACKER.set_progress(crawlId, msg)
		try:
			crawl = delegate.crawl_get_by_id(crawlId)
		except ValueError as ve:
			flash('No crawl id.')
			return redirect(url_for('crawl'))	


	if not request.form['address']:
		flash('No address.')
		return redirect(url_for('crawl'))

	# Save to DB
	crawl = Crawl()	
	delegate.crawl_create(crawl)
	

	initial_url = request.form['address']
	crawler = Crawler(initial_url, id=crawl.id, no_workers=1)
	crawler.addListener(notify)
	crawler.start()
	
	return render_template('crawlProgress.html', crawl=crawl)	


@app.route('/crawl.report', methods=['GET', 'POST'])
@login_required
def crawl_report():
	global PROGRESS_TRACKER

	# print("\n{}: Current session tracker: {}".format(threading.current_thread().ident, session['progress_tracker']))
	crawlId = request.args.get('id')
	try:
		crawl = delegate.crawl_get_by_id(crawlId)
		# ptj = crawl.note
		# progress = jsonpickle.decode(ptj)
		progress = PROGRESS_TRACKER.get_progress(crawlId)
		return jsonify(progress)
	except ValueError as ve:
		flash('No crawl id.')
		return redirect(url_for('crawl'))	


@app.route('/crawl.delete', methods=['GET', 'POST'])
@login_required
def crawl_delete():
	try:
		id = request.args.get('id', type=int)
		crawl = delegate.crawl_get_by_id(id)

		delegate.crawl_delete(crawl)

		flash('Crawl deleted')
		return redirect(url_for('crawl'))
	except ValueError as ve:
		flash('No crawl id.')
		return redirect(url_for('crawl'))	



@app.route('/crawl.cancel', methods=['GET', 'POST'])
@login_required
def crawl_cancel():
	try:
		id = request.args.get('id', type=int)
		crawl = Crawl.query.get(id)

		db.session.delete(crawl)
		db.session.commit()

		flash('Crawl deleted')
		return redirect(url_for('crawl'))
	except ValueError as ve:
		flash('No crawl id.')
		return redirect(url_for('crawl'))	


@app.route('/viewCrawl', methods=['GET'])
@login_required
def viewCrawl():
	try:
		id = request.args.get('id', type=int)
		crawl = delegate.crawl_get_by_id(id)

		return render_template('viewCrawl.html', crawl=crawl, links = crawl.links)
	except ValueError as ve:
		flash('No crawl id.')
		return redirect(url_for('crawl'))	


@app.route('/sitemap_result', methods=['GET', 'POST'])
@login_required
def sitemap_result():
	return render_template('sitemap_result.html')


@app.route('/status', methods=['GET', 'POST'])
@login_required
def status():
	status = []
	
	#Home folder
	from os.path import expanduser	
	home = expanduser("~")	
	status.append({'key':'Home folder', 'value':home})	
	
	#Python version
	import sys
	status.append({'key':'Python version', 'value':sys.version})	
		
	#Current folder	
	status.append({'key':'Current folder', 'value':os.path.dirname(__file__)})	

	#Graphviz dependency
	from shutil import which
	status.append({'key':'Graphviz present', 'value': which('dot') is not None})	
	
	return render_template('status.html', status=status)


@app.route('/one')
def one():
	@copy_current_request_context
	def x():
		try:
			# id = request.args.get('id', type=int)
			id = 1
			crawl = Crawl.query.get(id)			

			crawl.note = "Hello from X"
			session = delegate.get_session()
			session.commit()	
		except ValueError as ve:
			flash('No crawl id.')
			return redirect(url_for('crawl'))		

	t = threading.Thread(target=x)
	t.start()
	return "One"



@app.route('/two')
def two():
	v = session['v'] 
	return "Two: {}".format(v)


# start the server with the 'run()' method
if __name__ == '__main__':
	# app = create_app()
	if not os.path.isfile('./amalgam.db'):
		setup_database(app)
	app.run()
