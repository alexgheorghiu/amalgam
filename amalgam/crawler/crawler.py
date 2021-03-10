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
from threading import Thread, Condition, currentThread, Lock, RLock
import csv
import uuid

from amalgam.models.models import Crawl, Url, Resource, Site
from amalgam.models import inside
from amalgam.delegate import delegate





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
	links = []
	page = {'url': url}

	try:
		pre = requests.head(url)

		if 'content-type' in pre.headers:
			page['content-type'] = pre.headers['content-type']

		if 'text/html' in pre.headers['content-type']:
			r = requests.get(url)			
			if r.status_code == 200:								
				soup = BeautifulSoup(r.content, "html.parser")
				for link in soup.find_all("a"):
					if 'href' in link.attrs:
						href = link.attrs['href']
						content = link.contents
						absolute = to_absolute_url(url, href)
						links.append({'href': href, 'content': content, 'absolute': absolute})
					elif 'name' in link.attrs:
						# Just anchor
						pass

				page['content'] = r.content
			page['status'] = r.status_code

	except Exception as ex:
		logger.info("[%s] Error %s" %(currentThread().getName(), ex))

	return page, links


class CrawlerDB(Thread):
	def __init__(self, initialLink, delegate, max_links = 0, no_workers = 10, id = str(uuid.uuid4())):
		Thread.__init__(self)
		self.noOfWorkers = no_workers
		self.workers = []
		self.running = True
		self.paused = False
		self.condition = Lock()
		self.delegate = delegate
		self.noOfJobsLock = Lock()
		self.noOfJobs = 0
		self.listeners = []
		self.id = id
		self.add_initial_url(initialLink)
		self.max_links = max_links
		try:
			self.domain_regex = re.compile(self.get_domain(initialLink))
		except Exception as ex:
			logging.error("Exception {}".format(ex))

	def get_domain(self, url):
		domain = urlparse(url).netloc
		return domain

	def add_initial_url(self, address):
		logger.info("Add intial URL")
		with self.condition:
			url = Url(url=address, absolute_url=address, type=Url.TYPE_INTERNAL, crawl_id=self.id)
			self.delegate.url_create(url)

	def no_unvisited_urls(self):
		with self.condition:
			return self.delegate.url_count_unvisited()

	def no_visited_urls(self):
		with self.condition:
			return self.delegate.url_count_visited()

	def no_external_urls(self):
		with self.condition:
			return self.delegate.url_count_external()

	def next_unvisited_link_id(self):
		link_id = -1
		if self.no_unvisited_urls() > 0:
			link_id = self._get_next_unvisited_url_id()
			if link_id != -1:
				self.increaseNoOfJobs()
		return link_id

	def _get_next_unvisited_url_id(self):
		with self.condition:
			url = self.delegate.url_get_first_unvisited()
			if url is not None:
				return url.id
		return -1

	def mark_url_as_visited(self, url_id):
		with self.condition:
			url = self.delegate.url_get_by_id(url_id)
			url.visited = True
			self.delegate.url_update(url)

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
							new_links.append({'href': href, 'content': content, 'absolute': absolute})
						elif 'name' in link.attrs:
							# Just anchor
							pass
		except Exception as ex:
			logger.info("[%s] Error %s" % (currentThread().getName(), ex))

		return new_links

	def _type_links(self, links):
		for link in links:
			if re.search(self.domain_regex, link['absolute']): # internal link
				link['type'] = 'internal'
			else: # external link
				link['type'] = 'external'

	def _get_links(self, link_id):
		with self.condition:
			link = self.delegate.url_get_by_id(link_id)
			(page, links) = get_links(link.absolute_url)
			self._type_links(links)
			return page, links

	def link2url(self, link):
		url = Url(url=link['href'], absolute_url=link['absolute'], type=link['type'], crawl_id=self.id)
		return url

	def page2resource(self, page):
		resource = Resource(crawl_id=self.id)
		if 'url' in page:
			resource.absolute_url = page['url']
		if 'content' in page:
			resource.content = page['content']
		return resource

	def add_links(self, links, resource_id = None):
		"""Add a bunch of URLs using the resource id as source (page where found it)"""
		with self.condition:
			for link in links:
				if not self.delegate.url_is_present(link['absolute']):
					url = self.link2url(link)
					if resource_id is not None:
						url.src_resource_id = resource_id
					self.delegate.url_create(url)

	def add_resource(self, page):
		with self.condition:
			if not self.delegate.resource_is_present():
				resource = self.page2resource(page)
				self.delegate.resource_create(resource)

	def connect_url_to_destination(self, url_id, resource_id):
		with self.condition:
			url = self.delegate.url_get_by_id(url_id)
			url.dst_resource_id = resource_id
			self.delegate.url_update(url)

	def run(self):

		# Initialize workers
		for i in range(self.noOfWorkers):
			self.workers.append(Thread(target=self.workerJob, kwargs={"crawlId": self.id}, name="Thread-{}".format(i)))

		# Start workers
		self._start_all_workers()

		while self.running:
			logger.debug("[%s] Crawler thread cycle started." % (currentThread().getName()))
			if self.paused:
				logger.debug("[%s] Crawler paused." % (currentThread().getName()))
				continue

			logger.debug("[%s] Crawler check if jobs are done." % (currentThread().getName()))
			if self._is_job_done():
				logger.debug("Crawler is shutting down")
				self.setRunning(False)
				break
			else:
				logger.debug("[%s] Crawler's jos are NOT done." % (currentThread().getName()))

			logger.debug("[%s] Crawler sleep." % (currentThread().getName()))
			time.sleep(1)

		# Join them
		self._join_all_workers()

		msg = {
			"status": "done",
			"visited": self.no_visited_urls(),
			"to_visit": self.no_unvisited_urls(),
			"max_links": 0,
			"crawlId": self.id
		}

		self.notify(msg)

	def resource_get_by_absolute_url_and_crawl_id(self, address, crawler_id):
		with self.condition:
			resource = self.delegate.resource_get_by_absolute_url_and_crawl_id(address, crawler_id)
			return resource

	def resource_create(self, page):
		with self.condition:
			try:
				resource = self.page2resource(page)
				self.delegate.resource_create(resource)
			except Exception as e:
				logger.warn("{} Exception {}}.".format (currentThread().getName(), e))
			return resource

	def workerJob(self, crawlId):
		while self.running:
			logger.debug("[%s] Worker thread cycle started." % (currentThread().getName()))

			if self.paused:
				continue

			link_id = self.next_unvisited_link_id()
			logger.debug("[%s] Next link [%d]." % (currentThread().getName(), link_id))

			if 'link_id' in locals() and link_id != -1:
				logger.debug("[%s] Current link : %d" % (currentThread().getName(), link_id))
				page, links = self._get_links(link_id)
				logger.debug("[%s] Discovered [%d] links." % (currentThread().getName(), len(links)))

				try:
					# 1.Add Resource 2.Link URLs to (new | existing) Resources
					resource = self.resource_get_by_absolute_url_and_crawl_id(page['url'], self.id)
					if resource is None:
						resource = self.resource_create(page)

					self.connect_url_to_destination(link_id, resource.id)

					logger.debug("[%s] Adding links to DB linked to resource [%d]" % (currentThread().getName(), resource.id))
					self.add_links(links, resource.id)

					self.mark_url_as_visited(link_id)

					msg = {
						"status": "in_progress",
						"visited": self.no_visited_urls(),
						"to_visit": self.no_unvisited_urls(),
						"max_links": 0,
						"crawlId": crawlId,
						"currentWorker": currentThread().getName()
					}

					self.notify(msg)
				except Exception as e:
					print("Error {}".format(e))

				self.decreaseNoOfJobs()

			logger.debug("[%s] cycle ended." % (currentThread().getName()))
		else:
			logger.debug("[%s] is shutting down." % (currentThread().getName()))


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

	def getNoOfJobs(self):
		with self.noOfJobsLock:
			return self.noOfJobs

	def _is_job_done(self):
		# Test if noOfJobs == 0 and to_visit == 0
		if self.getNoOfJobs() == 0 and self.no_unvisited_urls() == 0:
			return True
		return False


	def _join_all_workers(self):
		for w in self.workers:
			w.join()


	def setRunning(self, status):
		self.running = status

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
	parser.add_argument('-w', '--workers', type=int, default=4, help='Number of workers')
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


	site = Site(name=domain)
	delegate.site_create(site)
	crawl = Crawl(site_id=site.id)
	delegate.crawl_create(crawl)

	crawler = CrawlerDB(initialLink=theURL, max_links=max_links, no_workers=noOfWorkers, delegate=delegate, id=crawl.id)

	t1 = time.time()
	crawler.start()
	crawler.join()
	t2 = time.time()
	total_time = t2 - t1

	logger.info("Total internal links visited: %d in: %ds" % (crawler.no_visited_urls(), total_time))
	# for url in [link.absolute_url for link in crawler.visited]:
	# 	logger.info("\t" + url)

	logger.info("Total external links: %d" % crawler.no_external_urls())
	# for url in [link.absolute_url for link in crawler.external_links]:
	# 	logger.info("\t" + url)

	# report('./crawl-requests-report.log', crawler.visited)

	# crawler.export()


if __name__ == "__main__":
	main()