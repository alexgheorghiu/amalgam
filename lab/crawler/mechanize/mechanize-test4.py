import mechanize
import time

br = mechanize.Browser()
br.set_debug_http(True)
br.set_debug_responses(True)
site_address = "http://localhost:7000/android-studio-ide-201.6858069-linux.tar.gz"
# site_address = "https://app.abctimetracking.com/?lang=en"
t1 = time.time()
try:
    print("1")
    resp = br.open("http://localhost:7000")

    print("2")
    resp = br.open("http://localhost:7000/zoom_amd64.deb")

    print("3")
    resp = br.open("http://localhost:7000/android-studio-ide-201.6858069-linux.tar.gz")
    #br.follow_link("http://blog.scriptoid.com/2010/08")

    print("Response code: %d" % resp.getcode())
    #links = br.links()
except mechanize.HTTPError as err:
		print("\t", err)
except mechanize.BrowserStateError as err:	
		print("\t", err)
t2 = time.time();
print("Time took: %ss" % (t2-t1));