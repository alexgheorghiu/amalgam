.\env\Scripts\activate.bat

python extract_urls.py --url https://abctimetracking.com/sitemap.xml
python categorize_urls.py 
python visualize_urls.py --output-format png --size "40"