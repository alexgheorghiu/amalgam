# import the Flask class from the flask module
from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify, copy_current_request_context
from functools import wraps
import os
from flask_sqlalchemy import SQLAlchemy
from amalgam.crawler.crawler import CrawlerDB
import jsonpickle
import threading

from amalgam import database
from amalgam.delegate import delegate
from amalgam.models.models import Url, Crawl, User, Site, User
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
CRAWLS = {}

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

			# Get first selected site
			if user.current_site_id == None:
				sites = delegate.site_get_all()
				if len(sites) > 0:
					current_site = sites[0]
					user.current_site_id = current_site.id
					delegate.user_update(user)

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
	user = delegate.user_get_by_id(session['user_id'])
	sites = delegate.site_get_all()	# TODO: In the future show only sites for current user
	return render_template('home.html', sites=sites, user=user)



@app.route('/sitemap')
@login_required
def sitemap():
	return render_template('sitemap.html')


@app.route('/crawl')
@login_required
def crawl():
	user = delegate.user_get_by_id(session['user_id'])	
	site = delegate.site_get_by_id(user.current_site_id)
	crawls = delegate.crawl_get_all_for_site(user.current_site_id)
	sites = delegate.site_get_all()	# TODO: In the future show only sites for current user
	return render_template('crawl.html', crawls = crawls, site=site, user=user, sites=sites)


@app.route('/switch_site')
@login_required
def switch_site():
	user_id = session['user_id']
	user = delegate.user_get_by_id(user_id)

	site_id = request.args.get('site_id')
	page = request.args.get('page')

	user.current_site_id = site_id
	delegate.user_update(user)

	if page == 'home':
		return redirect(url_for('home'))
	elif page == 'crawl':
		return redirect(url_for('crawl'))
	elif page == 'status':
		return redirect(url_for('status'))
	else:
		return redirect(url_for('home'))


@app.route('/crawl.exe', methods=['GET', 'POST'])
@login_required
def crawl_exe():
	global PROGRESS_TRACKER
	global CRAWLS

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

	user = delegate.user_get_by_id(session['user_id'])	
	sites = delegate.site_get_all()	# TODO: In the future show only sites for current user

	# Save to DB	
	crawl = Crawl(site_id=user.current_site_id)	
	delegate.crawl_create(crawl)
	

	initial_url = request.form['address']

	crawler = CrawlerDB(delegate, initial_url, id=crawl.id, no_workers=10)
	CRAWLS[crawl.id] = crawler
	crawler.addListener(notify)
	crawler.start()
	
	return render_template('crawl_progress.html', crawl=crawl, user=user, sites=sites)	


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
	global CRAWLS

	try:
		id = request.args.get('id', type=int)
		crawler = CRAWLS[id]
		crawler.setRunning(False)
		return "success"
	except ValueError as ve:
		return "failed"


@app.route('/viewCrawl', methods=['GET'])
@login_required
def viewCrawl():
	try:
		id = request.args.get('id', type=int)
		crawl = delegate.crawl_get_by_id(id)
		links = delegate.url_get_all_by_crawl_id(id)
		user = delegate.user_get_by_id(session['user_id'])	
		sites = delegate.site_get_all()	# TODO: In the future show only sites for current user
		return render_template('viewCrawl.html', crawl=crawl, links = links, user=user, sites=sites)
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
	
	user = delegate.user_get_by_id(session['user_id'])	
	sites = delegate.site_get_all()	# TODO: In the future show only sites for current user

	return render_template('status.html', status=status, user=user, sites=sites)


@app.route('/report_inner_links', methods=['GET', 'POST'])
@login_required
def report_inner_links():
	
	id = request.args.get('id', type=int)
	user = delegate.user_get_by_id(session['user_id'])	
	sites = delegate.site_get_all()	# TODO: In the future show only sites for current user
	
	return render_template('report_inner_links.html', crawlId = id, user=user, sites=sites)


@app.route('/report_inner_links_data', methods=['GET', 'POST'])
@login_required
def report_inner_links_data():
	id = request.args.get('id', type=int)

	from amalgam.tests.report_inner_links import inner_links_data
	data = inner_links_data(id)
	# data = {'name':'Alex'}
	# jdata =  jsonpickle.encode(data)
	
	return jsonify(data)


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
	return redirect(url_for('personal_settings'))


@app.route('/personal_settings', methods=['GET', 'POST'])
@login_required
def personal_settings():
	user = delegate.user_get_by_id(session['user_id'])	
	sites = delegate.site_get_all()	# TODO: In the future show only sites for current user
	return render_template('personal_settings.html', user=user, sites=sites, clazz=User)


@app.route('/personal_settings.edit', methods=['GET', 'POST'])
@login_required
def personal_settings_edit():
	user = delegate.user_get_by_id(session['user_id'])	
	sites = delegate.site_get_all()	# TODO: In the future show only sites for current user
	return render_template('personal_settings_edit.html', user=user, sites=sites, clazz=User)


@app.route('/personal_settings.update', methods=['GET', 'POST'])
@login_required
def personal_settings_update():	
	user = delegate.user_get_by_id(session['user_id'])	
	
	if not request.form['name']:
		flash('No name.')
		return redirect(url_for('users'))
	name = request.form['name']
	user.name = name

	if not request.form['email']:
		flash('No email.')
		return redirect(url_for('users'))
	email = request.form['email']
	user.email = email

	if request.form['password']:				
		password = request.form['password']
		user.password = password

	if not request.form['level']:
		flash('No level.')
		return redirect(url_for('users'))
	level = request.form['level']
	user.level = level

	delegate.user_update(user)
	
	flash('User updated !')

	return redirect(url_for('personal_settings'))


@app.route('/sites', methods=['GET', 'POST'])
@login_required
def sites():
	user = delegate.user_get_by_id(session['user_id'])	
	sites = delegate.site_get_all()	# TODO: In the future show only sites for current user
	return render_template('sites.html', user=user, sites=sites)


@app.route('/site.delete', methods=['GET', 'POST'])
@login_required
def site_delete():
	site_id = request.args.get('site_id', type=int)
	# page = request.args.get('page', type=str)

	delegate.site_delete_by_id(site_id)

	user = delegate.user_get_by_id(session['user_id'])	
	sites = delegate.site_get_all()	# TODO: In the future show only sites for current user
	
	flash('Site deleted !')
	return render_template('sites.html', user=user, sites=sites)
		

@app.route('/site.add', methods=['GET', 'POST'])
@login_required
def site_add():
	page = request.args.get('page', type=str)
	user = delegate.user_get_by_id(session['user_id'])
	page = request.form['page']
	site_name = request.form['site']
	site_url = request.form['url']
	site = Site(name=site_name, url=site_url)
	delegate.site_create(site)

	user.current_site_id = site.id
	delegate.site_update(site)

	if page == 'home':
		return redirect(url_for('home'))
	else:
		return redirect(url_for('sites'))


@app.route('/users', methods=['GET', 'POST'])
@login_required
def users():
	user = delegate.user_get_by_id(session['user_id'])	
	sites = delegate.site_get_all()	# TODO: In the future show only sites for current user
	users = delegate.user_get_all()
	return render_template('users.html', user=user, sites=sites, users=users, clazz=User)


@app.route('/user.add', methods=['GET', 'POST'])
def user_add():
	if not request.form['name']:
		flash('No name.')
		return redirect(url_for('users'))
	name = request.form['name']

	if not request.form['email']:
		flash('No email.')
		return redirect(url_for('users'))
	email = request.form['email']

	if not request.form['password']:
		flash('No password.')
		return redirect(url_for('users'))
	password = request.form['password']

	if not request.form['level']:
		flash('No level.')
		return redirect(url_for('users'))
	level = request.form['level']


	user = User(name=name, email=email, password=password, level=level)
	delegate.user_create(user)

	return redirect(url_for('users'))


@app.route('/user.delete', methods=['GET', 'POST'])
@login_required
def user_delete():
	user_id = request.args.get('user_id', type=int)
	# page = request.args.get('page', type=str)

	delegate.user_delete_by_id(user_id)

	flash('User deleted !')

	return redirect(url_for('users'))


@app.route('/user.edit', methods=['GET', 'POST'])
@login_required
def user_edit():	
	user_id = request.args.get('user_id', type=int)
	edited_user = delegate.user_get_by_id(user_id)	

	user = delegate.user_get_by_id(session['user_id'])	
	sites = delegate.site_get_all()	# TODO: In the future show only sites for current user
	users = delegate.user_get_all()
	
	return render_template('user_edit.html', user=user, sites=sites, users=users, clazz=User, edited_user=edited_user)


@app.route('/user.update', methods=['GET', 'POST'])
@login_required
def user_update():	
	edited_user_id = request.form['edited_user_id']
	edited_user = delegate.user_get_by_id(edited_user_id)	

	if not request.form['name']:
		flash('No name.')
		return redirect(url_for('users'))
	name = request.form['name']
	edited_user.name = name

	if not request.form['email']:
		flash('No email.')
		return redirect(url_for('users'))
	email = request.form['email']
	edited_user.email = email

	if request.form['password']:				
		password = request.form['password']
		edited_user.password = password

	if not request.form['level']:
		flash('No level.')
		return redirect(url_for('users'))
	level = request.form['level']
	edited_user.level = level

	delegate.user_update(edited_user)
	
	flash('User updated !')

	return redirect(url_for('users'))



# start the server with the 'run()' method
if __name__ == '__main__':
	# app = create_app()
	if not os.path.isfile('./amalgam.db'):
		setup_database(app)
	app.run()
