from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify, copy_current_request_context
from functools import wraps
import os
from amalgam.crawler.crawler import CrawlerDB
import jsonpickle
import threading
import logging
import sqlalchemy

from amalgam import database
from amalgam.progress_tracker import ProgressTracker
from amalgam.config import setup_logging, SQLALCHEMY_DATABASE

from amalgam.delegatex import XDelegate as Delegate
from amalgam.models.modelsx import User,Crawl, User, Site, User, metadata
from amalgam.manage_db import mock


log = logging.getLogger(__name__)


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

def check_db():
	if SQLALCHEMY_DATABASE == 'sqlite':
		if not os.path.isfile('./amalgam.db'):
			log.info("SQLite file NOT present. Creating it!")
			mock()
		else:
			log.info("SQLite file present. Skip creation.")


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
	log.info("Logging in")
	delegate = Delegate()
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
	delegate = Delegate()
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
	delegate = Delegate()
	user = delegate.user_get_by_id(session['user_id'])	
	site = delegate.site_get_by_id(user.current_site_id)
	crawls = delegate.crawl_get_all_for_site(user.current_site_id)
	sites = delegate.site_get_all()	# TODO: In the future show only sites for current user
	return render_template('crawl.html', crawls = crawls, site=site, user=user, sites=sites)


@app.route('/crawl.exe', methods=['GET', 'POST'])
@login_required
def crawl_exe():
	global PROGRESS_TRACKER
	global CRAWLS
	delegate = Delegate()

	@copy_current_request_context
	def notify(msg):
		crawlId = str(msg['crawlId'])		

		# FIXME: Naive way to avoid leaks (byt keeping references)
		if msg['status'] == 'done':
			del CRAWLS[int(crawlId)]

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
	max_links = 0
	if len(request.form['max']) > 0 and int(request.form['max']) > 0:
		max_links = int(request.form['max'])

	crawler = CrawlerDB(delegate, initial_url, id=crawl.id, no_workers=10, max_links=max_links)
	CRAWLS[crawl.id] = crawler
	crawler.addListener(notify)
	crawler.start()
	
	return render_template('crawl_progress.html', crawl=crawl, user=user, sites=sites)	


@app.route('/crawl.report', methods=['GET', 'POST'])
@login_required
def crawl_report():
	global PROGRESS_TRACKER
	delegate = Delegate()
	
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
	delegate = Delegate()
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


@app.route('/crawl.view_links', methods=['GET'])
@login_required
def crawl_view_links():
	delegate = Delegate()
	try:
		id = request.args.get('id', type=int)
		crawl = delegate.crawl_get_by_id(id)
		links = delegate.url_get_all_by_crawl_id(id)
		user = delegate.user_get_by_id(session['user_id'])	
		sites = delegate.site_get_all()	# TODO: In the future show only sites for current user
		return render_template('crawl_view_links.html', crawl=crawl, links = links, user=user, sites=sites)
	except ValueError as ve:
		flash('No crawl id.')
		return redirect(url_for('crawl'))	


@app.route('/crawl.view_pages', methods=['GET'])
@login_required
def crawl_view_pages():
	delegate = Delegate()
	try:
		id = request.args.get('id', type=int)
		crawl = delegate.crawl_get_by_id(id)
		# links = delegate.url_get_all_by_crawl_id(id)
		resources = delegate.resource_get_all_by_crawl(id)
		user = delegate.user_get_by_id(session['user_id'])	
		sites = delegate.site_get_all()	# TODO: In the future show only sites for current user
		return render_template('crawl_view_pages.html', crawl=crawl, resources = resources, user=user, sites=sites)
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
	delegate = Delegate()

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

	# SQLAlchemy version
	status.append({'key':'SQLAlchemy version', 'value':sqlalchemy.__version__ })	
	
	user = delegate.user_get_by_id(session['user_id'])	
	sites = delegate.site_get_all()	# TODO: In the future show only sites for current user
	
	db_status = {}
	db_status['size'] = 'N/A' if isinstance(database.engine.pool, sqlalchemy.pool.impl.NullPool) else database.engine.pool.size()
	db_status['checkedin'] = 'N/A' if isinstance(database.engine.pool, sqlalchemy.pool.impl.NullPool) else database.engine.pool.checkedin()
	db_status['overflow'] = 'N/A' if isinstance(database.engine.pool, sqlalchemy.pool.impl.NullPool) else database.engine.pool.overflow()
	db_status['checkedout'] = 'N/A' if isinstance(database.engine.pool, sqlalchemy.pool.impl.NullPool) else database.engine.pool.checkedout()

	return render_template('status.html', status=status, user=user, sites=sites, db_status = db_status)


@app.route('/internal_linking', methods=['GET', 'POST'])
@login_required
def internal_linking():
	delegate = Delegate()
	user = delegate.user_get_by_id(session['user_id'])	
	# site = delegate.site_delete_by_id(user.current_site_id)
	last_crawl = delegate.crawl_get_last_for_site(user.current_site_id)
	last_crawl_id = 'null' # Values for JavaScript
	if last_crawl is not None:
		last_crawl_id = last_crawl.id
	
	sites = delegate.site_get_all()	# TODO: In the future show only sites for current user
	
	return render_template('internal_linking.html', last_crawl_id = last_crawl_id, user=user, sites=sites)


@app.route('/report_inner_links_data', methods=['GET', 'POST'])
@login_required
def report_inner_links_data():
	id = request.args.get('id', type=int)

	from amalgam.reports.report_inner_links import inner_links_data
	data = inner_links_data(id)
	# data = {'name':'Alex'}
	# jdata =  jsonpickle.encode(data)
	
	return jsonify(data)


@app.route('/report_inner_links_bar_data', methods=['GET'])
@login_required
def report_inner_links_bar_data():
	crawl_id = request.args.get('crawl_id', type=int)
	bar_no = request.args.get('bar_no', type=int)

	from amalgam.reports.report_inner_links import bar_data
	data = bar_data(crawl_id, bar_no)
	# data = {'name':'Alex'}
	jdata =  jsonpickle.encode(data)
	
	return jdata


@app.route('/report_inner_incomming_urls', methods=['GET'])
@login_required
def report_inner_incomming_urls():
	resource_id = request.args.get('resource_id', type=int)
	delegate = Delegate()
	pages = delegate.resource_get_all_incoming_for_resource(resource_id)	
	jdata =  jsonpickle.encode(pages)	
	return jdata


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
	return redirect(url_for('personal_settings'))


@app.route('/personal_settings', methods=['GET', 'POST'])
@login_required
def personal_settings():
	delegate = Delegate()
	user = delegate.user_get_by_id(session['user_id'])	
	sites = delegate.site_get_all()	# TODO: In the future show only sites for current user
	return render_template('personal_settings.html', user=user, sites=sites, clazz=User)


@app.route('/personal_settings.edit', methods=['GET', 'POST'])
@login_required
def personal_settings_edit():
	delegate = Delegate()
	user = delegate.user_get_by_id(session['user_id'])	
	sites = delegate.site_get_all()	# TODO: In the future show only sites for current user
	return render_template('personal_settings_edit.html', user=user, sites=sites, clazz=User)


@app.route('/personal_settings.update', methods=['GET', 'POST'])
@login_required
def personal_settings_update():	
	delegate = Delegate()
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
	delegate = Delegate()
	user = delegate.user_get_by_id(session['user_id'])	
	sites = delegate.site_get_all()	# TODO: In the future show only sites for current user
	return render_template('sites.html', user=user, sites=sites)


@app.route('/site.delete', methods=['GET', 'POST'])
@login_required
def site_delete():
	delegate = Delegate()
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
	delegate = Delegate()
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


@app.route('/switch_site')
@login_required
def switch_site():
	delegate = Delegate()
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
	elif page == 'internal_linking':
		return redirect(url_for('internal_linking'))		
	else:
		return redirect(url_for('home'))
		

@app.route('/users', methods=['GET', 'POST'])
@login_required
def users():
	delegate = Delegate()
	user = delegate.user_get_by_id(session['user_id'])	
	sites = delegate.site_get_all()	# TODO: In the future show only sites for current user
	users = delegate.user_get_all()
	return render_template('users.html', user=user, sites=sites, users=users, clazz=User)


@app.route('/user.add', methods=['GET', 'POST'])
def user_add():
	delegate = Delegate()	
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
	delegate = Delegate()
	user_id = request.args.get('user_id', type=int)
	# page = request.args.get('page', type=str)

	delegate.user_delete_by_id(user_id)

	flash('User deleted !')

	return redirect(url_for('users'))


@app.route('/user.edit', methods=['GET', 'POST'])
@login_required
def user_edit():	
	delegate = Delegate()
	user_id = request.args.get('user_id', type=int)
	edited_user = delegate.user_get_by_id(user_id)	

	user = delegate.user_get_by_id(session['user_id'])	
	sites = delegate.site_get_all()	# TODO: In the future show only sites for current user
	users = delegate.user_get_all()
	
	return render_template('user_edit.html', user=user, sites=sites, users=users, clazz=User, edited_user=edited_user)


@app.route('/user.update', methods=['GET', 'POST'])
@login_required
def user_update():	
	delegate = Delegate()
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
	setup_logging()
	check_db()
	# app = create_app()
	# if not os.path.isfile('./amalgam.db'):
	# 	setup_database(app)
	
	app.run(host='0.0.0.0') # To run it a on certain port use: app.run(host='0.0.0.0', port=80)
