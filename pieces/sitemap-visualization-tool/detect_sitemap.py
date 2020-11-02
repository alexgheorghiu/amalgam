import requests
from bs4 import BeautifulSoup
import gzip
import os


urls = ['http://abctimetracking.com','https://clockify.me', 'https://toggl.com', 'https://getharvest.com']
#urls = ['https://getharvest.com']



def guess_sitemap(url):
	""" Tries to guess the sitemap and its type by simply using the root address of the site 
		Param url: the domain without any path
		Returns and N-uple ( normal | master, compressed | uncompressed, sitemap_url)
	"""	
	
	print("\nGuess: %s" % url)
	
	#Try normal sitemaps
	filename = 'sitemap.xml'
	url1 = url + '/' + filename
	
	content = ''
	try:
		response = requests.get(url1)
		
		if response.status_code == 200:
			print('Request success!')
			content = str(response.content)
		else:
			print('Request failed code', response.status_code)
			#we will continue bellow with .gz try
		
	except Exception as err:
		print(err)
		return None

	#If is an index of sitemaps
	if 'sitemapindex' in content:
		print('Is a master index!')
		return ('master', 'uncompressed', url1)
	elif 'urlset' in content:
		print('Is a normal index!')
		return ('normal', 'uncompressed', url1)
	else:
		print('Not an index!')
		print('Content: %s ' % str(content) )
	
	
	#If we reached this point it means that we have to try .gz version
	filename = 'sitemap.xml.gz'
	url1 = url + '/' + filename
	content = ''
	try:
		response = requests.get(url1)
		
		if response.status_code == 200:
			print('Request success!')
			# Make a folder to hold gzip files
			if not os.path.exists('gzip-sitemaps'):
				os.makedirs('gzip-sitemaps')
				
			with open('gzip-sitemaps/' + filename, 'wb') as f:
				f.write(response.content)
				
			with gzip.open('gzip-sitemaps/' + filename,'rb') as f:
				content = f.read().decode("utf-8")
				
			#TODO: remove file
		else:
			print('Request failed code' + response.status_code)
			return None
		
	except Exception as err:
		print(err)
		return None
	
	if 'sitemapindex' in content:
		print('Is a master index!')
		return ('master', 'compressed', url1)
	elif 'urlset' in content:
		print('Is a normal index!')
		return ('normal', 'compressed', url1)
	else:
		print('Not an index!')
		return None
	
if __name__ == '__main__' :
	for url in urls:
		guess = guess_sitemap(url)
		print(guess)

		
