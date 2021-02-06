import unittest
import sys
from amalgam.models import inside
from amalgam.models.models import Link


class TestModels(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    

    def test_inside(self):
        links = []

        needle = Link(absolute_url = "https://amalgam.scriptoid.com", url = "/home", type=Link.TYPE_INTERNAL)
        assert not inside(needle, links)

        l = Link(absolute_url = "https://amalgam.scriptoid.com", url = "/home", type=Link.TYPE_INTERNAL)
        links.append(l)

        l = Link(absolute_url = "https://amalgam.scriptoid.com/contact", url = "/contact", type=Link.TYPE_INTERNAL)
        links.append(l)

        assert inside(needle, links)





if __name__ == '__main__':
    unittest.main()