""" 
https://github.com/python-mechanize/mechanize

https://mechanize.readthedocs.io/en/latest/
"""
import re
import mechanize


to_visit = []
visited_links = []

br = mechanize.Browser()

resp = br.open("http://www.abctimetracking.com/")

for link in br.links(url_regex="//abctimetracking.com"):
	if not link.url in visited_links:
		visited_links.append(link.url)
		
	print(link)
	resp = br.follow_link(link)  # takes EITHER Link instance OR keyword args
	for link2 in br.links(url_regex="//abctimetracking.com"):
		print("\t%s [%s]" % (link2.url, link2.text))
		if not link2.url in visited_links:
			visited_links.append(link.url)

    
    #br.back()
    
print("No of collected links: %d" % len(visited_links))


		
	