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
from threading import Thread, Condition


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crawler")
logger.setLevel(logging.INFO)

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



class Crawler:
	to_visit = []
	visited = []
	workers = []
	condition = Condition()

	class Worker(Thread):		

		def __init__(self, crawler):
			Thread.__init__(self)
			self.running = True
			self.crawler = crawler
			self.jobInProgress = True

		def run(self):			
			while self.running and self.crawler.max_links > len(self.crawler.visited) :
				link = None

				# Grab link
				self.crawler.condition.acquire()
				if len(self.crawler.to_visit) > 0:
					self.jobInProgress = True
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

					newlinks = self.get_links(link)
					new_internal_links = [l for l in newlinks if l.type == Link.TYPE_INTERNAL]
					logger.info("[%s] Found %d new internal links" % (self.getName(), len(new_internal_links)))

					# Bring back any new discovered link, if any
					if len(new_internal_links) > 0 :						
						self.crawler.condition.acquire()
						self.crawler.to_visit.extend(new_internal_links)
						self.crawler.visited.append(link)
						self.jobInProgress = False
						self.crawler.condition.notify_all()
						self.crawler.condition.release()


				# Wait?
				logger.info("[%s] Visited: %d To visit: %d" % (self.getName(), len(self.crawler.visited), len(self.crawler.to_visit)))

		def setRunning(self, status):
			self.running = status

		def get_links(self, current_link):
			logger.info("[%s] Visiting: %s" % (self.getName(), current_link.absolute_url))
			new_links = []

			# TODO: Add code
			
			try:
				pre = requests.head(current_link.absolute_url)
				current_link.mime_type = pre.headers['content-type']

				if 'text/html' in pre.headers['content-type']:
					r = requests.get(current_link.absolute_url)
				# elif 'application/xhtml+xml' in pre.headers['content-type']:
				# 	r = requests.get(current_link.absolute_url)
					current_link.content = r.content

					if r.status_code == 200:
						new_links = self.get_content_links(r.content, current_link)
						logger.info("[%s] Found: %d links" % (self.getName(), len(new_links)))
				else:
					return new_links

			except Exception as ex:
				# self.visited.append(current_link)
				logger.warning("[%s] Exception: %s" % ( self.getName(), ex) )

			return new_links


		def get_content_links(self, content, current_link):
			content_links = []
			soup = BeautifulSoup(content, "html.parser")

			for link in soup.find_all("a"):
				#TODO: descent into link.contents (it can be an image) and gather all text
				if 'href' in link.attrs:
					href = link.attrs['href']
					# logger.info("\tFound link: %s -> %s" % (href, link.contents))
					logger.info("\t[%s]Found link: %s " % (self.getName(), href))
					if re.search(self.crawler.domain_regex, href): # internal link
						if (href in [l.absolute_url for l in self.crawler.visited] or href in [l.absolute_url for l in self.crawler.to_visit]) :
							pass
						else:
							logger.info("\t\t[%s]Plan to visit: [%s]" % ( self.getName(),href) )
							content_links.append(Link(href, to_absolute_url(current_link.absolute_url, href), Link.TYPE_INTERNAL))						
					else: #external link
						if not (href in [l.absolute_url for l in self.crawler.external_links] ):
							content_links.append(Link(href,to_absolute_url(current_link.absolute_url, href), Link.TYPE_EXTERNAL))
				elif 'name' in link.attrs:
					# Just anchor
					pass
			return content_links


	def _start_all_workers(self):
		for w in self.workers:
			w.start()
			# w.join()

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
		self.external_links = []
		self.max_links = max_links
		self.domain_regex = re.compile(self.get_domain(initialLink)) 
		self.noOfWorkers = 5
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
	logger.info("Total external links: %d" % len(crawler.external_links))
	report('./crawl-requests-report.log', crawler.visited)

if __name__ == "__main__":
	main()