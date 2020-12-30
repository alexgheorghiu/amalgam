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
from models import Link
from urllib.parse import urlparse
import logging
from threading import Thread, Condition, currentThread


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


def get_links(url):
	"""
	Get links from a link 
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


class Crawler:
	to_visit = []
	visited = []
	workers = []
	condition = Condition()
	external_links = []

	class Worker(Thread):		

		def __init__(self, crawler):
			Thread.__init__(self)
			self.running = True
			self.crawler = crawler
			self.jobInProgress = True
			logger.info("[%s] Constructor " %(self.getName()))

		def run(self):			
			while self.running and (self.crawler.max_links == 0 or (self.crawler.max_links >0 and self.crawler.max_links >= len(self.crawler.visited)) ) :
				self.jobInProgress = True

				link = None

				# Grab link
				self.crawler.condition.acquire()
				if len(self.crawler.to_visit) > 0:					
					link = self.crawler.to_visit.pop(0)
					logger.info("[%s] Picked %s" %(self.getName(), link.absolute_url))
				else:
					logger.info("[%s] No job to pick." %(self.getName()))
					self.jobInProgress = False
					if self.crawler.isJobInProgress(): 
						logger.info("[%s] Wait." %(self.getName()))
						self.crawler.condition.wait()
					else:
						logger.info("[%s] Going to shutdown." %(self.getName()))
						self.running = False
				self.crawler.condition.notify_all()
				self.crawler.condition.release()
				
				if 'link' in locals() and link != None:
					# Do the job
					logger.info("[%s] Current link : %s" %(self.getName(), link.absolute_url))

					internal_links, external_links = self._get_links(link.absolute_url)
					
					# logger.info("[%s] Found %d new internal links" % (self.getName(), len(new_internal_links)))

					# Bring back any new discovered link, if any
					self.crawler.condition.acquire()					
					self.crawler.visited.append(link)
					if len(internal_links) > 0 or len(external_links) > 0:						
						for link in internal_links:
							if not (link.absolute_url in [visited_link.absolute_url for visited_link in self.crawler.visited]):
								if not (link.absolute_url in [proposed_link.absolute_url for proposed_link in self.crawler.to_visit]):
									self.crawler.to_visit.append(link)

						for link in external_links:
							if not (link.absolute_url in [external_link.absolute_url for external_link in self.crawler.external_links]):
								self.crawler.external_links.append(link)
												
						self.jobInProgress = False
					self.crawler.condition.notify_all()
					self.crawler.condition.release()


				# Wait?
				logger.info("[%s] Visited: %d To visit: %d" % (self.getName(), len(self.crawler.visited), len(self.crawler.to_visit)))

		def setRunning(self, status):
			self.running = status

		def filter_links(self, links):
			#TODO: Add filter

			return links


		def _get_links(self, link):
			links = get_links(link)
			light_internal, light_external =  self._filter_links(links)
			heavy_internal = self._to_heavy_links(light_internal, Link.TYPE_INTERNAL)
			heavy_external = self._to_heavy_links(light_external, Link.TYPE_EXTERNAL)
			return (heavy_internal, heavy_external)

		
		def _filter_links(self, links):
			external = []
			internal = []

			for l in links:
				if re.search(self.crawler.domain_regex, l['absolute']): # internal link						
					internal.append(l)
				else: # external link
					external.append(l)
			return (internal, external)


		def _to_heavy_links(self, links, type):
			heavy_links = []
			for link in links:
				heavy_link = Link(link['absolute'], link['href'], type)
				heavy_links.append(heavy_link)
			return heavy_links


	def _start_all_workers(self):
		for w in self.workers:
			w.start()

		for w in self.workers:
			w.join()

	def _stop_all_workers(self):
		self.condition.acquire()
		for w in self.workers:			
			w.setRunning(False)
		self.condition.notify_all()
		self.condition.release()

	def isJobInProgress(self):
		for w in self.workers:
			if w.jobInProgress:
				return True
		return False

	def get_domain(self, url):		
		domain = urlparse(url).netloc
		return domain

	def __init__(self, initialLink, max_links = 0):
		self.to_visit.append( Link(initialLink,initialLink, Link.TYPE_EXTERNAL) )		
		self.max_links = max_links
		try:
			self.domain_regex = re.compile(self.get_domain(initialLink))
		except Exception as ex:
			logging.error("Boom")
		
		self.noOfWorkers = 10
		for i in range(self.noOfWorkers):
			self.workers.append(self.Worker(self))


	def crawl(self, notify=None):		
		# l = Link(self.initialLink, self.initialLink, Link.TYPE_INTERNAL )
		# self.to_visit = [l]

		self._start_all_workers()

		# 	logger.info("Visited: %d To visit: %d" % (len(self.visited), len(self.to_visit)))

		# if not notify == None:
		# 		notify(len(self.visited), len(self.to_visit), self.max_links)


def main():
	# domain = 'localhost:7000'
	domain = 'http://abctimetracking.com'
	max_links = 0

	# Parse arguments
	parser = argparse.ArgumentParser(description="A simple website crawler.")
	parser.add_argument('-d', '--domain', type=str, default=domain, help='Domain to crawl', required=True)
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

	crawler = Crawler(initialLink=theURL, max_links=max_links)

	t1 = time.time()
	crawler.crawl()
	t2 = time.time()
	total_time = t2 - t1

	logger.info("Total internal links visited: %d in: %ds" % (len(crawler.visited), total_time))
	for url in [link.absolute_url for link in crawler.visited]:
		logger.info("\t" + url)

	logger.info("Total external links: %d" % len(crawler.external_links))
	for url in [link.absolute_url for link in crawler.external_links]:
		logger.info("\t" + url)
	
	report('./crawl-requests-report.log', crawler.visited)

if __name__ == "__main__":
	main()