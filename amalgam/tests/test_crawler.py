import unittest
import sys
from amalgam.crawler.crawler import to_absolute_url, get_links, get_domain, is_internal



class TestCrawler(unittest.TestCase):

    def test_get_domain(self):
        domains = {
            'http://abctimetracking.com': 'abctimetracking.com',
            'https://foo.com': 'foo.com',
            'ftp://baz.com/goo': 'baz.com',
            'http://my.foo.com/today': 'my.foo.com'
        }

        for k, v in domains.items():
            assert v == get_domain(k), '[{}] not equal to [{}]'.format(v, get_domain(k))


    def test_is_internal(self):
        domain = 'foo.com'

        url = 'foo.com' # Invalid URL (no schema)
        assert is_internal(domain, url) == False, '{} is not internal to {}'.format(url, domain)

        url = 'http://foo.com/contact.html'
        assert is_internal(domain, url), '{} is not internal to {}'.format(url, domain)

        url = 'http://john@foo.com:400/retro/active_contact.html'
        assert is_internal(domain, url), '{} is not internal to {}'.format(url, domain)


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