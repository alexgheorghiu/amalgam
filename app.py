# import the Flask class from the flask module
from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from functools import wraps
import os
from flask_sqlalchemy import SQLAlchemy


# create the application object
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///amalgam.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.database = "sample.db"

# Setup secret key
app.secret_key = 'my precious'

db = SQLAlchemy(app)

from models import *

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
			"max_links" : 0
		}

	return PROGRESS_TRACKER[crawlId]



def notify(crawlId, visited, to_visit, max_links):
	progress = getProgress(crawlId)
	progress['visited'] = visited
	progress['to_visit'] = to_visit
	progress['max_links'] = max_links



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


# @app.route('/crawl.exe', methods=['GET', 'POST'])
# @login_required
# def crawl_exe():
# 	if not request.form['address']:
# 		flash('No address.')
# 		return redirect(url_for('crawl'))

# 	from crawler import Crawler
# 	crawler = Crawler(request.form['address'], 10)
# 	crawler.crawl(notify=notify)
# 	links = crawler.visited

# 	# Save to DB
# 	crawl = Crawl()	
# 	for link in links:
# 		crawl.links.append(link)
# 		# db.session.add(link)

# 	db.session.add(crawl)
# 	db.session.commit()	
	
# 	return render_template('viewCrawl.html', crawl=crawl, links = crawl.links)	


@app.route('/crawl.exe', methods=['GET', 'POST'])
@login_required
def crawl_exe():
	# if not request.form['address']:
	# 	flash('No address.')
	# 	return redirect(url_for('crawl'))

	# from crawler import Crawler
	# crawler = Crawler(request.form['address'], 10)
	# crawler.crawl(notify=notify)
	# links = crawler.visited

	# Save to DB
	crawl = Crawl()	
	db.session.add(crawl)
	db.session.commit()	

	#Start crawling thread
	import threading
	class CrawlThread(threading.Thread):
		def __init__(self, address, db, crawlId, max):
			threading.Thread.__init__(self)
			self.address = address
			self.db = db
			self.crawlId = crawlId
			self.max = max

		def run(self):
			# Perform crawl
			from crawler import Crawler
			crawler = Crawler(self.address, self.max)

			def special_notify(visited, to_visit, max_link):
				notify(self.crawlId, visited, to_visit, max_link)

			crawler.crawl(notify=special_notify)

			# Store in DB
			crawl = Crawl.query.get(self.crawlId)
			crawl.links.extend(crawler.visited)
			db.session.commit()	
	
	max_links = request.form.get('max', type=int) or 0
	ct = CrawlThread(request.form['address'], db, crawl.id, max_links)
	ct.start()

	
	
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


@app.route('/sitemap_analyze', methods=['GET', 'POST'])
@login_required
def sitemap_analyze():
	import subprocess
	
	#sys.path.append('./foo/bar/mock-0.3.1')
	
	#check parameter
	if not request.form['address']:
		flash('No address.')
		return redirect(url_for('sitemap'))
		
	
	#Extraction
	current_folder = os.path.dirname(os.path.abspath(__file__))
	#print("Current folder %s" % current_folder)

	script_path = os.path.abspath(current_folder + '/pieces/sitemap-visualization-tool/extract_urls.py')
	#print("Script path %s" % script_path)


	address = request.form['address']
	result = subprocess.run(["python3", script_path, '--url', address, '--not_index'], stdout=subprocess.PIPE, text=True, input="")
	#print(result.stdout)


	#Categorization
	script_path = os.path.abspath(current_folder + '/pieces/sitemap-visualization-tool/categorize_urls.py')
	result = subprocess.run(["python3", script_path], stdout=subprocess.PIPE, text=True, input="")
	#print(result.stdout)


	#Visualize
	script_path = os.path.abspath(current_folder + '/pieces/sitemap-visualization-tool/visualize_urls.py')
	result = subprocess.run(["python3", script_path, '--output-format', 'png', '--size', '"40"'], stdout=subprocess.PIPE, text=True, input="")
	#print(result.stdout)
	
	#TODO: This is lame
	#copy image to /static
	from shutil import copyfile
	filename = 'sitemap_graph_3_layer.png'
	srcfile = current_folder + '/' + filename
	destinationfile = current_folder + '/static/' + filename
	copyfile(srcfile, destinationfile)

	
	#render image
	return redirect(url_for('sitemap_result'))
	

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
	app.debug = True
	app.run()
