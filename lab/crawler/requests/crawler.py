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


# domain = 'localhost:7000'
domain = 'http://scriptod.com'
max_links = 0

class Link:
	def __init__(self, absolute_url, url):
		self.absolute_url = absolute_url
		self.url = url
		

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
domain_regex = re.compile(domain)

class Crawler:
	def __init__(self, initialLink, max_links = 0):
		self.initialLink = initialLink
		self.visited = []
		self.external_links = []
		self.max_links = max_links

	def crawl(self):
		l = Link(theURL,theURL)
		self.to_visit = [l]
		while len(self.to_visit) > 0 and (self.max_links == 0 or (self.max_links > 0 and self.max_links > len(self.visited)) ):
			# Get first link
			current_link = self.to_visit.pop(0)
			print("Visiting: %s" % current_link.absolute_url)

			try:
				r = requests.get(current_link.absolute_url)
			except requests.ConnectionError as con_err:
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
						print("[%s] -> %s" % (link.contents, href))
						if re.search(domain_regex, href): # internal link
							if (href in [l.absolute_url for l in self.visited] or href in [l.absolute_url for l in self.to_visit]) :
								pass
							else:
								print("\t[%s]Plan to visit" % link.absolute_url)
								self.to_visit.append(Link(href, to_absolute_url(current_link.absolute_url, href)))
						else: #external link
							if not (href in [l.absolute_url for l in self.external_links] ):
								self.external_links.append(Link(href,to_absolute_url(current_link.absolute_url, href)))
					elif 'name' in link.attrs:
						# Just anchor
						pass
			else:
				#TODO: mark it as broken
				print("%s-->%d", current_link.absolute_url, r.status_code)

			self.visited.append(current_link)

			print("Visited: %d To visit: %d" % (len(self.visited), len(self.to_visit)))

def main():
	crawler = Crawler(initialLink=theURL, max_links=max_links)

	t1 = time.time()
	crawler.crawl()
	t2 = time.time()
	total_time = t2 - t1

	print("Total internal links visited: %d in: %ds" % (len(crawler.visited), total_time))
	print("Total external links: %d" % len(crawler.external_links))
	report('./crawl-requests-report.log', crawler.visited)

if __name__ == "__main__":
	main()