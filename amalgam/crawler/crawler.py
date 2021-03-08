"""
Inspired by:
https://www.statworx.com/at/blog/web-scraping-101-in-python-with-requests-beautifulsoup/
http://unhackathon.org/springboard-projects/web-crawler.html 

"""

import requests
import argparse
import re
import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import logging
from threading import Thread, Condition, currentThread, Lock
import csv
import uuid

from amalgam.models.models import Crawl, Url, Resource
from amalgam.models import inside
from amalgam.delegate import Delegate


logging.basicConfig(filename='crawler.log', level=logging.INFO)
logger = logging.getLogger("crawler")
logger.setLevel(logging.INFO)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

def to_absolute_url(parent_page_link, link):
	'''Converts a link to absolute'''
	abs_regex = re.compile("^(http)|(https)://.*")
	if re.search(abs_regex, link): # already absolute
		return link
	else: #relative
		return requests.compat.urljoin(parent_page_link, link)


def report(filename, visited):
	"""Dump all visited into a file"""
	with open(filename, 'w') as f:
		for link in visited:
			f.write("%s\n" % link.absolute_url)


def dump(tag, links):
	logger.info("\t{} {}".format(currentThread().getName(), tag))
	for link in links:		
		logger.info("\t\t {} {}".format(currentThread().getName(), link.absolute_url))


def get_links(url):
	"""
	Get links from a link as a list of {'href', 'content', 'absolute'}
	"""
	logger.info("[%s] Extracting links from : %s" % (currentThread().getName(), url))
	new_links = []			

	try:
		pre = requests.head(url)

		if 'text/html' in pre.headers['content-type']:
			r = requests.get(url)			
			if r.status_code == 200:								
				soup = BeautifulSoup(r.content, "html.parser")
				for link in soup.find_all("a"):
					if 'href' in link.attrs:
						href = link.attrs['href']
						content = link.contents
						absolute = to_absolute_url(url, href)
						new_links.append({'href':href, 'content':content, 'absolute':absolute})
					elif 'name' in link.attrs:
						# Just anchor
						pass
	except Exception as ex:
		logger.info("[%s] Error %s" %(currentThread().getName(), ex))

	
	return new_links


class Crawler(Thread):
	
	def __init__(self, initialLink, max_links = 0, no_workers = 10, id = str(uuid.uuid4())):
		Thread.__init__(self)
		self.noOfWorkers = no_workers
		self.workers = []
		self.running = True
		self.paused = False
		self.condition = Lock()
		self.to_visit = [] # Links to visit
		self.visited = []
		self.external_links = []	
		self.noOfJobsLock = Lock()
		self.noOfJobs = 0		
		self.listeners = []

		
		self.to_visit.append( Url(initialLink,initialLink, Url.TYPE_INTERNAL) )
		self.max_links = max_links
		self.id = id
		try:
			self.domain_regex = re.compile(self.get_domain(initialLink))
		except Exception as ex:
			logging.error("Exception {}".format(ex))


	def run(self):
		
		# Initialize workers
		for i in range(self.noOfWorkers):
			self.workers.append(Thread(target=self.workerJob, kwargs={"crawlId": self.id}, name="Thread-{}".format(i)))

		# Start workers
		self._start_all_workers()

		while self.running:
			if self.paused:
				continue

			if self._is_job_done():
				logger.info("Crawler is shutting down")
				self.setRunning(False)
				break

			time.sleep(0.1)

		# Join them
		self._join_all_workers()

		msg = {
			"status": "done", 
			"visited" : len(self.visited), 
			"to_visit" : len(self.to_visit),
			"max_links" : 0,
			"crawlId" : self.id
		}

		self.notify(msg)

	
	def workerJob(self, crawlId):
		while self.running:
			if self.paused:
				continue

			link = None
			with self.condition:
				if len(self.to_visit) > 0:
					link = self.to_visit.pop(0)
					self.visited.append(link)
					self.increaseNoOfJobs()

			if 'link' in locals() and link != None:
				logger.info("[%s] Current link : %s" %(currentThread().getName(), link.absolute_url))
				internal_links, external_links = self._get_links(link.absolute_url)				

				with self.condition:
					for il in internal_links:
						if not inside(il, self.visited):
							if not inside(il, self.to_visit):
								self.to_visit.append(il)

					for el in external_links:
						if not inside(el, self.external_links):
							self.external_links.append(el)
					
					msg = {
						"status": "in_progress", 
						"visited" : len(self.visited), 
						"to_visit" : len(self.to_visit),
						"max_links" : 0,
						"crawlId" : crawlId,
						"currentWorker" : currentThread().getName()
					}

					self.notify(msg)

				self.decreaseNoOfJobs()
		else:
			logger.info("[%s] is shutting down." %(currentThread().getName()))


	def stop(self):
		self.setRunning(False)


	def pause(self):
		self.paused = True

	def resume(self):
		if self.paused:
			self.paused = False


	def _start_all_workers(self):
		for w in self.workers:
			w.start()

	def increaseNoOfJobs(self):
		with self.noOfJobsLock:
			self.noOfJobs = self.noOfJobs + 1

	def decreaseNoOfJobs(self):
		with self.noOfJobsLock:
			self.noOfJobs = self.noOfJobs - 1	


	def _is_job_done(self):
		# Test if noOfJobs == 0 and to_visit == 0
		with self.condition:
			with self.noOfJobsLock:
				if self.noOfJobs == 0 and len(self.to_visit) == 0:
					return True
		return False


	def _join_all_workers(self):
		for w in self.workers:
			w.join()


	def setRunning(self, status):
		self.running = status

		
	def _filter_links(self, links):
		external = []
		internal = []

		for l in links:
			if re.search(self.domain_regex, l['absolute']): # internal link						
				internal.append(l)
			else: # external link
				external.append(l)
		return (internal, external)


	def _to_heavy_links(self, links, type):
		heavy_links = []
		for link in links:
			heavy_link = Url(link['absolute'], link['href'], type)
			heavy_links.append(heavy_link)
		return heavy_links


	def _get_links(self, link):
		links = get_links(link)
		light_internal, light_external =  self._filter_links(links)
		heavy_internal = self._to_heavy_links(light_internal, Url.TYPE_INTERNAL)
		heavy_external = self._to_heavy_links(light_external, Url.TYPE_EXTERNAL)
		return (heavy_internal, heavy_external)


	def get_domain(self, url):		
		domain = urlparse(url).netloc
		return domain


	def crawl(self, notify=None):		
		# l = Link(self.initialLink, self.initialLink, Link.TYPE_INTERNAL )
		# self.to_visit = [l]

		self._start_all_workers()

		# 	logger.info("Visited: %d To visit: %d" % (len(self.visited), len(self.to_visit)))

		# if not notify == None:
		# 		notify(len(self.visited), len(self.to_visit), self.max_links)

	def export(self, file='crawl.csv'):
		with open(file, 'w', newline='') as csvfile:
			fieldnames = ['type','absolute url', 'url', 'mime'] 
			writer = csv.DictWriter(csvfile, fieldnames=fieldnames, dialect='unix')

			writer.writeheader()
			for il in self.visited:
				writer.writerow(
					{
						'type': Url.TYPE_INTERNAL,
						'absolute url': il.absolute_url,
						'url': il.url,
						'mime': il.mime_type
					})

			for el in self.external_links:
				writer.writerow(
					{
						'type': Url.TYPE_EXTERNAL,
						'absolute url': el.absolute_url,
						'url': el.url,
						'mime': el.mime_type
					})


	def addListener(self, callback):
		self.listeners.append(callback)


	def removeListener(self, callback):
		self.listeners.remove(callback)


	def notify(self, msg):
		for callback in self.listeners:
			callback(msg)


def main():
	# domain = 'localhost:7000'
	domain = 'http://abctimetracking.com'
	max_links = 0

	# Parse arguments
	parser = argparse.ArgumentParser(description="A simple website crawler.")
	parser.add_argument('-d', '--domain', type=str, default=domain, help='Domain to crawl', required=True)
	parser.add_argument('-w', '--workers', type=int, default=5, help='Number of workers')
	parser.add_argument('-m','--max-links', type=int, default=0, help='Maximum no. of links to index')
	parser.add_argument('--delay', type=int, default=0, help='Delay between requests')
	args = parser.parse_args()

	if args.domain:
		domain = args.domain
	else:
		print('No domain passed, using %s.' % domain)
		print('Read usage details in file header for more information on passing arguments.')

	if args.max_links:
		max_links = args.max_links

	theURL = 'http://' + domain	
	noOfWorkers = args.workers

	crawler = Crawler(initialLink=theURL, max_links=max_links, no_workers=noOfWorkers)

	t1 = time.time()
	crawler.start()
	crawler.join()
	t2 = time.time()
	total_time = t2 - t1

	logger.info("Total internal links visited: %d in: %ds" % (len(crawler.visited), total_time))
	# for url in [link.absolute_url for link in crawler.visited]:
	# 	logger.info("\t" + url)

	logger.info("Total external links: %d" % len(crawler.external_links))
	# for url in [link.absolute_url for link in crawler.external_links]:
	# 	logger.info("\t" + url)
	
	report('./crawl-requests-report.log', crawler.visited)

	crawler.export()

if __name__ == "__main__":
	main()