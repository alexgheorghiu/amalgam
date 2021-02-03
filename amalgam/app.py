# import the Flask class from the flask module
from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from functools import wraps
import os
from flask_sqlalchemy import SQLAlchemy
from amalgam.crawler.crawler import Crawler

from amalgam.database import db
from amalgam.models.link import Link
from amalgam.models.crawl import Crawl


# def create_app():
# create the application object
app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = 'my precious'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///amalgam.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.database = "sample.db"
db.init_app(app)
	# return app	


def setup_database(app):
	with app.app_context():
		db.create_all()
	db.session.commit()


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


PROGRESS_TRACKER = {	
}

def getProgress(crawlId):
	global PROGRESS_TRACKER

	if not crawlId in PROGRESS_TRACKER:		
		PROGRESS_TRACKER[crawlId] = {
			"visited" : 0,
			"to_visit" : 0,
			"max_links" : 0,
			"status": ""
		}

	return PROGRESS_TRACKER[crawlId]



def notify(msg):	
	progress = getProgress(msg["crawlId"])
	progress['visited'] = msg["visited"]
	progress['to_visit'] = msg["to_visit"]
	progress['max_links'] = msg["max_links"]
	progress['status'] = msg["status"]
	progress['crawlId'] = msg["crawlId"]


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
		if request.form['username'] != 'admin' or request.form['password'] != 'admin':
			error = 'Invalid Credentials. Please try again.'
		else:
			session['logged_in'] = True
			flash('You were just logged in!')
			return redirect(url_for('home'))
	return render_template('login.html', error=error)


@app.route('/logout')
@login_required
def logout():
	session.pop('logged_in', None)
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
	crawls = Crawl.query.all()
	return render_template('crawl.html', crawls = crawls)




@app.route('/crawl.exe', methods=['GET', 'POST'])
@login_required
def crawl_exe():
	if not request.form['address']:
		flash('No address.')
		return redirect(url_for('crawl'))

	# Save to DB
	crawl = Crawl()	
	db.session.add(crawl)
	db.session.commit()	

	initial_url = request.form['address']
	crawler = Crawler(initial_url, id=crawl.id)
	crawler.addListener(notify)
	crawler.start()
	
	return render_template('crawlProgress.html', crawl=crawl)	


@app.route('/crawl.report', methods=['GET', 'POST'])
@login_required
def crawl_report():
	id = request.args.get('id', type=int)
	return jsonify(getProgress(id))


@app.route('/crawl.delete', methods=['GET', 'POST'])
@login_required
def crawl_delete():
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
		crawl = Crawl.query.get(id)

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




# start the server with the 'run()' method
if __name__ == '__main__':
	# app = create_app()
	if not os.path.isfile('./amalgam.db'):
		setup_database(app)
	app.run()
