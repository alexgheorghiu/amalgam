import unittest
import sys
from amalgam.crawler.crawler import to_absolute_url, get_links



class TestCrawler(unittest.TestCase):

    def test_to_absolute_url(self):
        parent = 'http://foo.com'
        child = "./hello"
        result = to_absolute_url(parent, child)
        assert result == 'http://foo.com/hello'

        parent = 'http://foo.com'
        child = "https://bar.com/tango"
        result = to_absolute_url(parent, child)
        assert result == 'https://bar.com/tango'

        parent = 'http://foo.com/main/activity'
        child = "/tango"
        result = to_absolute_url(parent, child)
        assert result == 'http://foo.com/tango'


        parent = 'http://foo.com/main/activity'
        child = "../tango"
        result = to_absolute_url(parent, child)
        assert result == 'http://foo.com/tango'

        parent = 'http://foo.com/main/activity/'
        child = "../tango"
        result = to_absolute_url(parent, child)
        assert result == 'http://foo.com/main/tango'


        parent = 'http://foo.com/main/activity/'
        child = "../../index.html"
        result = to_absolute_url(parent, child)
        assert result == 'http://foo.com/index.html'

    def test_get_links(self):
        url = 'http://scriptoid.com'
        page, links = get_links(url)

        assert len(links) == 12, "Found {} links at {}".format(len(links), url)

if __name__ == '__main__':
    unittest.main()