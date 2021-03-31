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
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

def to_absolute_url(parent_page_link, link):
	"""Converts a link to absolute"""
	abs_regex = re.compile("^(http)|(https)://.*")
	if re.search(abs_regex, link): # already absolute
		return link
	else: #relative
		return requests.compat.urljoin(parent_page_link, link)

def is_internal(domain, url):
	"""Tests if the specific url is an internal link
	domain: the domain without schema
	url: the link should be a valid URL (schema + domain)
	"""
	parsed = urlparse(url)
	if domain.lower() == parsed.hostname:
		return True
	return False


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
	Get links from an URL as a list of {'href', 'content', 'absolute', 'time'}
	"""
	logger.info("[%s] Extracting links from : %s" % (currentThread().getName(), url))
	links = []
	page = {'url': url}

	try:
		t0 = time.time()
		pre = requests.head(url)

		page['status-code'] = pre.status_code
		logger.info("[%s] Status code : %d" % (currentThread().getName(), pre.status_code))
		
		if 'content-type' in pre.headers:
			page['content-type'] = pre.headers['content-type']

		if 'text/html' in pre.headers['content-type']:
			r = requests.get(url)			
			t1 = time.time()
			if r.status_code == 200:								
				soup = BeautifulSoup(r.content, "html.parser")
				for link in soup.find_all("a"):
					if 'href' in link.attrs:
						href = link.attrs['href']
						content = link.contents[0]
						absolute = to_absolute_url(url, href)
						links.append({'href': href, 'content': content, 'absolute': absolute})
					elif 'name' in link.attrs:
						# Just anchor
						pass

				page['content'] = r.content				
			page['elapsed'] = t1-t0			

	except Exception as ex:
		logger.info("[%s] Error %s" %(currentThread().getName(), ex))

	return page, links


def get_domain(url):
	parsed = urlparse(url)
	if parsed.scheme == '':
		raise Exception("The argument provided: [{}] does not contain scheme" . format(url))
	domain = parsed.netloc
	return domain

class CrawlerDB(Thread):
	def __init__(self, delegate, initialLink=None,  max_links = 0, no_workers = 10, id = str(uuid.uuid4())):
		Thread.__init__(self)
		self.noOfWorkers = no_workers
		self.workers = []
		self.running = True
		self.paused = False
		self.condition = RLock()
		self.delegate = delegate
		self.listeners = []  # A list of listeners that want to listen to messages (ex: progress) from Crawler
		self.id = id
		self.initialLink = initialLink
		if initialLink is not None:
			self.add_initial_url(initialLink)
		self.max_links = max_links
		try:
			self.domain_regex = re.compile(get_domain(initialLink))
		except Exception as ex:
			logging.error("Exception {}".format(ex))


	def add_initial_url(self, address):
		logger.info("Add initial URL")
		with self.condition:
			url = Url(url=address, absolute_url=address, type=Url.TYPE_INTERNAL, crawl_id=self.id, job_status=Url.JOB_STATUS_NOT_VISITED)
			self.delegate.url_create(url)

	def no_unvisited_urls(self):
		with self.condition:
			return self.delegate.url_count_unvisited(self.id)

	def no_pending_urls(self):
		with self.condition:
			return self.delegate.url_count_pending(self.id)

	def all_unvisited_urls(self):
		with self.condition:
			return self.delegate.url_get_all_unvisited(self.id)

	def no_visited_urls(self):
		with self.condition:
			return self.delegate.url_count_visited(self.id)

	def no_visited_resources(self):
		with self.condition:
			return self.delegate.resource_count_visited(self.id)

	def no_external_urls(self):
		with self.condition:
			return self.delegate.url_count_external(self.id)

	def next_unvisited_link_id(self):
		link_id = -1
		with self.condition:
			url = self.delegate.url_get_first_unvisited(self.id)
			if url is not None:
				url.job_status = Url.JOB_STATUS_IN_PROGRESS  # Set Url as in progress
				self.delegate.url_update(url)
				# self.increaseNoOfJobs()
				link_id = url.id
		return link_id


	def mark_url_as_visited(self, url_id):
		with self.condition:
			url = self.delegate.url_get_by_id(url_id)
			url.job_status = Url.JOB_STATUS_VISITED
			self.delegate.url_update(url)


	def _type_links(self, links):
		for link in links:
			if is_internal(get_domain(self.initialLink), link['absolute']):  # internal link
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
		url = Url(crawl_id=self.id)
		# url=link['href'], absolute_url=link['absolute'], type=link['type'],
		if 'href' in link:
			url.url = link['href']
		if 'absolute' in link:
			url.absolute_url=link['absolute']
		if 	'type' in link:
			url.type=link['type']
		if 'content' in link:
			url.raw_content = str(link['content'])
			url.text = str(link['content'])  # TODO: Parse the raw_content and used only the text without HTML tags or other stuff
		return url

	def page2resource(self, page):
		resource = Resource(crawl_id=self.id)
		if 'url' in page:
			resource.absolute_url = page['url']
		if 'content' in page:
			resource.content = page['content']
		if 'elapsed' in page:
			resource.elapsed = page['elapsed']
		return resource

	def add_links(self, links, src_resource_id=None, status_code = 200):
		"""Add a bunch of URLs using the resource id as source (page where found it)"""
		with self.condition:
			for link in links:
				url = self.link2url(link)
				if src_resource_id is not None:
					url.src_resource_id = src_resource_id
				
					# Check if destination resource exists, and if does mark it as visited
					try:
						src_resource = delegate.resource_get_by_id(src_resource_id)
						dest_resource = delegate.resource_get_by_absolute_url_and_crawl_id(url.absolute_url, src_resource.crawl_id)
						if dest_resource is not None:
							url.job_status = Url.JOB_STATUS_VISITED
							url.dst_resource_id = dest_resource.id
							url.status_code = status_code
					except Exception as e:
						logger.warning("Exception {}".format(e))

				self.delegate.url_create(url)


	def add_resource(self, page):
		with self.condition:
			if not self.delegate.resource_is_present(crawlId=self.id):
				resource = self.page2resource(page)
				self.delegate.resource_create(resource)

	def connect_url_to_destination(self, url_id, resource_id):
		with self.condition:
			url = self.delegate.url_get_by_id(url_id)
			url.dst_resource_id = resource_id
			self.delegate.url_update(url)

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
			if self._are_jobs_done():
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
			"max_links": self.max_links,
			"crawlId": self.id
		}

		self.notify(msg)


	def workerJob(self, crawlId):
		while self.running:
			logger.debug("[%s] Worker thread cycle started." % (currentThread().getName()))

			if self.paused:
				continue

			# If max pages specified see if we already reached it			
			if self.max_links > 0:
				no_pages_visited = self.no_visited_resources()
				if no_pages_visited >= self.max_links:
					continue
			
			# Grab next job
			link_id = self.next_unvisited_link_id()
			logger.debug("[%s] Next link [%d]." % (currentThread().getName(), link_id))

			if 'link_id' in locals() and link_id != -1:
				logger.debug("[%s] Current link : %d" % (currentThread().getName(), link_id))
				page, links = self._get_links(link_id)
				logger.debug("[%s] Discovered [%d] links." % (currentThread().getName(), len(links)))

				try:
					with self.condition:
						# Update links status code
						url = delegate.url_get_by_id(link_id)
						url.status_code = page['status-code']
						delegate.url_update(url)

						if page['status-code'] == 200:
							# 1.Add Resource 2.Link URLs to (new | existing) Resources
							resource = self.resource_get_by_absolute_url_and_crawl_id(page['url'], self.id)
							if resource is None:
								#Add it only if max links not reached
								maximum_reached = False
								if self.max_links > 0: # We have a max_link specified
									no_pages_visited = self.no_visited_resources()
									if no_pages_visited >= self.max_links:
										maximum_reached = True
								
								if not maximum_reached:
									resource = self.resource_create(page)
									self.connect_url_to_destination(link_id, resource.id)
									logger.debug("[%s] Adding links to DB linked to resource [%d]" % (currentThread().getName(), resource.id))
									self.add_links(links, resource.id, page['status-code'])							
							else:
								# Resource already added only make the end connection
								self.connect_url_to_destination(link_id, resource.id)							
						else:
							pass						

						self.mark_url_as_visited(link_id)

						msg = {
							"status": "in_progress",
							"visited": self.no_visited_urls(),
							"to_visit": self.no_unvisited_urls(),
							"max_links": self.max_links,
							"crawlId": crawlId,
							"currentWorker": currentThread().getName()
						}

						self.notify(msg)
				except Exception as e:
					print("Error {}".format(e))

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


	def _are_jobs_done(self):
		# Test if noOfJobs == 0 and to_visit == 0
		# no_of_jobs = self.getNoOfJobs()

		# FIXME: If a thread grabs the initial link, while here, no_unvisited_urls() will
		# return zero (on next line) , also the no_of_jobs are zero so the Crawler 
		# will initiate shutdown

		no_pending_urls = self.no_pending_urls()
		logger.debug("Crawler: _are_jobs_done(...) : no_pendind_urls = %d " % (no_pending_urls,))

		if no_pending_urls == 0:
			return True

		# Test if we have reached the max no of pages
		if self.max_links > 0:
			no_pages_visited = self.no_visited_resources()
			if no_pages_visited >= self.max_links:
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

	# Empty DB
	from manage_db import empty, mock
	mock()

	# Parse arguments
	parser = argparse.ArgumentParser(description="A simple website crawler.")
	parser.add_argument('-d', '--domain', type=str, default=domain, help='Domain to crawl', required=True)
	parser.add_argument('-w', '--workers', type=int, default=2, help='Number of workers')
	parser.add_argument('-m', '--max-links', type=int, default=0, help='Maximum no. of links to index')
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
	# crawler = CrawlerDB(max_links=max_links, no_workers=noOfWorkers, delegate=delegate, id=1)

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