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
parser = argparse.ArgumentParser()
parser.add_argument('--domain', type=str, default=domain, help='Domain to crawl')
args = parser.parse_args()

if args.domain:
	domain = args.domain
else:
	print('No domain passed, using %s.' % domain)
	print('Read usage details in file header for more information on passing arguments.')

theURL = 'http://' + domain
domain_regex = re.compile(domain)

visited = [] 
external_links = []
l = Link(theURL,theURL)
to_visit = [l]
total_time = 0
while len(to_visit) > 0:
	# Get first link
	current_link = to_visit.pop(0)
	print("Visiting: %s" % current_link.absolute_url)

	# Try to follow it
	t1 = time.time()

	try:
		r = requests.get(current_link.absolute_url)
	except requests.ConnectionError as con_err:
		#TODO: mark it as visit (but broken)
		visited.append(current_link)
		continue
	except requests.exceptions.InvalidSchema:
		#TODO: mark it as visit (but broken)
		visited.append(current_link)
		continue

	if r.status_code == 200:
		soup = BeautifulSoup(r.content, "html.parser")

		for link in soup.find_all("a"):
			#TODO: descent into link.contents (it can be an image) and gather all text
			if 'href' in link.attrs:
				href = link.attrs['href']
				print("[%s] -> %s" % (link.contents, href))
				if re.search(domain_regex, href): # internal link
					if (href in [l.absolute_url for l in visited] or href in [l.absolute_url for l in to_visit]) :
						pass
					else:
						print("\t[%s]Plan to visit" % link.absolute_url)
						to_visit.append(Link(href, to_absolute_url(current_link.absolute_url, href)))
				else: #external link
					if not (href in [l.absolute_url for l in external_links] ):
						external_links.append(Link(href,to_absolute_url(current_link.absolute_url, href)))
			elif 'name' in link.attrs:
				# Just anchor
				pass
	else:
		#TODO: mark it as broken
		print("%s-->%d", current_link.absolute_url, r.status_code)

	visited.append(current_link)

	print("Visited: %d To visit: %d" % (len(visited), len(to_visit)))

print("Total internal links visited: %d in: %ds" % (len(visited), total_time))
print("Total external links: %d" % len(external_links))
report('./crawl-requests-report.log', visited)