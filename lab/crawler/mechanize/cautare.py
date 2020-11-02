import re

domain=  'localhost:7000'
theURL = 'http://localhost:7000/'
domain_regex = re.compile('localhost:7000')

if re.search(domain_regex, theURL):
    print("Found")
else:
    print("Not found")