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
	
	def get_domain(self, url):		
		domain = urlparse(url).netloc
		return domain

	def __init__(self, initialLink, max_links = 0):
		self.initialLink = initialLink
		self.visited = []
		self.external_links = []
		self.max_links = max_links
		self.domain_regex = re.compile(self.get_domain(self.initialLink)) 

	def crawl(self, notify=None):
		l = Link(self.initialLink, self.initialLink, Link.TYPE_INTERNAL)
		self.to_visit = [l]
		while len(self.to_visit) > 0 and (self.max_links == 0 or (self.max_links > 0 and self.max_links > len(self.visited)) ):
			if not notify == None:
				notify(len(self.visited), len(self.to_visit), self.max_links)

			# Get first link
			current_link = self.to_visit.pop(0)
			# print("Visiting: %s" % current_link.absolute_url)
			logger.info("Visiting: %s" % current_link.absolute_url)

			try:
				pre = requests.head(current_link.absolute_url)
				current_link.mime_type = pre.headers['content-type']

				if 'text/html' in pre.headers['content-type']:
					r = requests.get(current_link.absolute_url)
				# elif 'application/xhtml+xml' in pre.headers['content-type']:
				# 	r = requests.get(current_link.absolute_url)
					current_link.content = r.content
				else:
					self.visited.append(current_link)
					continue

			except requests.ConnectionError:
				#TODO: mark it as visit (but broken)
				self.visited.append(current_link)
				continue
			except requests.exceptions.InvalidSchema:
				#TODO: mark it as visit (but broken)
				self.visited.append(current_link)
				continue
			except requests.exceptions.InvalidURL:
				self.visited.append(current_link)
				continue
			except:
				self.visited.append(current_link)
				continue

			if r.status_code == 200:
				soup = BeautifulSoup(r.content, "html.parser")

				for link in soup.find_all("a"):
					#TODO: descent into link.contents (it can be an image) and gather all text
					if 'href' in link.attrs:
						href = link.attrs['href']
						logger.info("\tFound link: %s -> %s" % (href, link.contents))
						if re.search(self.domain_regex, href): # internal link
							if (href in [l.absolute_url for l in self.visited] or href in [l.absolute_url for l in self.to_visit]) :
								pass
							else:
								logger.info("\t\tPlan to visit: [%s]" % href)
								self.to_visit.append(Link(href, to_absolute_url(current_link.absolute_url, href), Link.TYPE_INTERNAL))
						else: #external link
							if not (href in [l.absolute_url for l in self.external_links] ):
								self.external_links.append(Link(href,to_absolute_url(current_link.absolute_url, href), Link.TYPE_INTERNAL))
					elif 'name' in link.attrs:
						# Just anchor
						pass
			else:
				#TODO: mark it as broken
				print("%s-->%d", current_link.absolute_url, r.status_code)

			self.visited.append(current_link)

			logger.info("Visited: %d To visit: %d" % (len(self.visited), len(self.to_visit)))

		if not notify == None:
				notify(len(self.visited), len(self.to_visit), self.max_links)


def main():
	# domain = 'localhost:7000'
	domain = 'http://scriptoid.com'
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

	print("Total internal links visited: %d in: %ds" % (len(crawler.visited), total_time))
	print("Total external links: %d" % len(crawler.external_links))
	report('./crawl-requests-report.log', crawler.visited)

	logger.info("Total internal links visited: %d in: %ds" % (len(crawler.visited), total_time))
	for url in [link.absolute_url for link in crawler.visited]:
		logger.info("\t" + url)

	logger.info("Total external links: %d" % len(crawler.external_links))
	for url in [link.absolute_url for link in crawler.external_links]:
		logger.info("\t" + url)

if __name__ == "__main__":
	main()