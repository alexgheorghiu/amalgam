import os
import subprocess

"""See https://docs.python.org/3.0/library/os.path.html"""

#list_files = subprocess.run(["dir"])
#list_files = subprocess.call("dir", shell=True)
#print("The exit code was: %d" % list_files.returncode)


#Extraction
current_folder = os.path.dirname(os.path.abspath(__file__))
print("Current folder %s" % current_folder)

script_path = os.path.abspath(current_folder + '/../' +  '/pieces/sitemap-visualization-tool/extract_urls.py');
print("Script path %s" % script_path)


result = subprocess.run(["python", script_path, '--url', 'https://toggl.com/sitemap.xml', '--not_index'], stdout=subprocess.PIPE, text=True, input="")
print(result.stdout)


#Categorization
script_path = os.path.abspath(current_folder + '/../' +  '/pieces/sitemap-visualization-tool/categorize_urls.py');
result = subprocess.run(["python", script_path], stdout=subprocess.PIPE, text=True, input="")
print(result.stdout)


#Visualize
script_path = os.path.abspath(current_folder + '/../' +  '/pieces/sitemap-visualization-tool/visualize_urls.py');
result = subprocess.run(["python", script_path, '--output-format', 'png', '--size', '"40"'], stdout=subprocess.PIPE, text=True, input="")
print(result.stdout)
