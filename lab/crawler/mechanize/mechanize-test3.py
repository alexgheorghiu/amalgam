""" 
https://github.com/python-mechanize/mechanize

https://mechanize.readthedocs.io/en/latest/
"""
import re
import mechanize

br = mechanize.Browser()
site_address = "http://www.abctimetracking.com"

l = mechanize.Link(base_url='https://abctimetracking.com/', url='', text='', tag='', attrs=[])
resp = br.open(site_address)
print(br.follow_link(l))
