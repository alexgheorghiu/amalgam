""" 
Crawls a site
https://github.com/python-mechanize/mechanize

https://mechanize.readthedocs.io/en/latest/
"""
import argparse
import re
import mechanize
import time
from mechanize import HTTPError, BrowserStateError
from urllib.error import URLError

class Link:
	def __init__(self, absolute_url):
		self.absolute_url = absolute_url


class Crawler:
	pass

def report(filename, visited):
	"""Dump all visited into a file"""
	with open(filename, 'w') as f:
		for link in visited:
			f.write("%s\n" % link.absolute_url)

domain=  'localhost:7000'

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('--domain', type=str, default=domain, help='Domain to crawl')
args = parser.parse_args()

if args.domain:
    domain = args.domain
else:
    print('No domain passed, using %s.' % domain)
    print('Read usage details in file header for more information on passing arguments.')

# print("Using domain [%s]" % domain)

theURL = 'http://' + domain
domain_regex = re.compile(domain)

browser = mechanize.Browser()
browser.set_handle_robots(False)
browser.set_handle_equiv(False) 
browser.set_debug_http(True)
browser.set_debug_responses(True) #Somehow this line makes the browser skip download large files
browser.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

visited = [] 
external_links = []
l = Link(theURL)
to_visit = [l]
total_time = 0
while len(to_visit) > 0:		
	# Get first link
	current_link = to_visit.pop(0)
	print("Visiting: %s" % current_link.absolute_url)
	
	# Try to follow it
	t1 = time.time()
	try:
		# Warning: Do not use follow_link() as if you might get a BrowserError.
		# The Browser might be in a incomplete or broken state 
		"""
			https://mechanize.readthedocs.io/en/latest/browser_api.html#the-browser
			"BrowserStateError is raised whenever the browser is in the wrong state 
			to complete the requested operation - e.g., when back() is called when 
			the browser history is empty, or when follow_link() is called when the 
			current response does not contain HTML data."
		"""
		resp = browser.open(current_link.absolute_url, timeout=5)
		#resp = browser.open(current_link.absolute_url)
	except HTTPError as err:
		print("\tHTTPError: ", err)
	except BrowserStateError as err:	
		print("\tBrowserStateError: ", err)
	except URLError as err:
		print("\tURLError: ", err)
		#This is a brocken link

	t2 = time.time()
	print("\t Took %ss" % (t2-t1))
	total_time = total_time + (t2-t1)

	visited.append(current_link)
	#links = browser.links(url_regex=("//" + domain))

	links = []
	try:
		links = browser.links()

		# Note: url_regex does not work as it search only through .url and not absolute_url
		# links = browser.links(url_regex=domain_regex) 

	except BrowserStateError as err:
		print("\t", 'Browser error!', err)
	except:
		print("\tOther type of exception")	
	
	for link in links:
		if re.search(domain_regex, link.absolute_url):
			if (link.absolute_url in [l.absolute_url for l in visited] or link.absolute_url in [l.absolute_url for l in to_visit]) :
				#print("\t[%s]On radar" % link.absolute_url)
				pass
			else:
				print("\t[%s]Plan to visit" % link.absolute_url)
				to_visit.append(Link(link.absolute_url))
		else:
			if not (link.absolute_url in [l.absolute_url for l in external_links] ):
				external_links.append(Link(link.absolute_url))

	print("Visited: %d To visit: %d" % (len(visited), len(to_visit)))


print("Total internal links visited: %d in: %ds" % (len(visited), total_time))
print("Total external links: %d" % len(external_links))
report('./crawl-report.log', visited)

