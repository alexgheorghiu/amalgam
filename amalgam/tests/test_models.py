import unittest
import sys
from models import Link, inside


class TestModels(unittest.TestCase):

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