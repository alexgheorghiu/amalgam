import unittest
import sys

from flask_sqlalchemy import SQLAlchemy

from amalgam.models import inside
from amalgam.models.models import Link, Site
from amalgam.app import app


class TestModels(unittest.TestCase):

    def setUp(self):
        self.db = SQLAlchemy(app)

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


    def test_db(self):        
        site = Site()	
        site.name = "Hotmug"
        self.db.session.add(site)
        self.db.session.commit()

        siteId = site.id
        assert siteId > 0 
        
        # s = Site.query.get(siteId)
        self.db.session.delete(site)
        self.db.session.commit()




if __name__ == '__main__':
    unittest.main()