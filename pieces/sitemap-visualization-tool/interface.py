''' 
Defines some methods that can be call from 
'''

import os
import subprocess
import uuid
from detect_sitemap import guess_sitemap
from categorize_urls import peel_layers
from visualize_urls import sitemap_graph, dump

def get_links(address):
	(type, compression, sitemap_url) = guess_sitemap(address)	
	return links(sitemap_url, type, compression)


def links(address, type, compressed):
	''' Retrieves all the links from a sitemap address. '''
	
	# Find current folder
	current_folder = os.path.dirname(os.path.abspath(__file__))
	print("Current folder: %s" % current_folder)
	
	# Create temporary dump file
	output_file_name = '{}.dat'.format(uuid.uuid4())
	output_path = os.path.abspath(current_folder + '/' + output_file_name);
	print("Output file: %s" % output_path)
	
	script_path = os.path.abspath(current_folder + '/extract_urls.py');
	
	command = ["python", script_path, '--url', address, '--output', output_path]
	
	if type == 'normal':
		command.append('--not_index')
		
	if compressed == 'compressed':
		command.append('--gzip')
	
	print('Command: ', command)
	result = subprocess.run(command, stdout=subprocess.PIPE, text=True, input="")
	
	# Load results
	f = open(output_path, "r")
	lines = f.readlines()
	f.close()	
	
	# Remove temp file
	os.remove(output_path)
	
	# Remove \n
	lines = [line[:-1] for line in lines]
	
	return lines



def get_categories(sitemap_urls, categorization_depth):
	# Find current folder
	current_folder = os.path.dirname(os.path.abspath(__file__))
	print("Current folder: %s" % current_folder)
	
	# Create temporary csv file
	output_file_name = '{}-category.csv'.format(uuid.uuid4())
	output_path = os.path.abspath(current_folder + '/' + output_file_name);
	print("Output file: %s" % output_path)
	
	sitemap_layers = peel_layers(urls=sitemap_urls, layers=categorization_depth, output_csv_file=output_path)
	print("Printed %d rows of data to %s" % (len(sitemap_layers), output_file_name))
	
	return sitemap_layers
	

def make_graph(sitemap_layers, graph_depth=3, limit=50, size='40', output_format='pdf', skip='', style='light', title=''):
	print(sitemap_layers)
	dump(sitemap_layers, 'dump_inteface.dat')
	sitemap_graph(sitemap_layers, layers=graph_depth, limit=limit, size=size, output_format=output_format, skip=skip, style=style, title=title)


if __name__ == '__main__':
	lines = links('https://abctimetracking.com/sitemap.xml')
	print(lines)

