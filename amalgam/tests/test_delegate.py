import unittest
import sys

from flask_sqlalchemy import SQLAlchemy

from amalgam.models import inside
from amalgam.models.models import Link, Site, Crawl
from amalgam.delegate import delegate

from amalgam.database import Base

class TestDelegate(unittest.TestCase):

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


    def test_db(self):        
        site = Site()	
        site.name = "Hotmugus"
        session = delegate.get_session()

        session.add(site)
        session.commit()

        siteId = site.id
        assert siteId > 0 
        
        # s = Site.query.get(siteId)
        # session.delete(site)
        # session.commit()

        # User.query.all()
        f = session.query(Site).first()
        assert f.id > 0 

        sites = session.query(Site).all()
        print("No of site: {}".format(len(sites)))
        assert len(sites) > 0

        crawl = Crawl(site_id = f.id)
        delegate.crawl_create(crawl)
        assert crawl.id > 0

        cc = delegate.crawl_get_by_id(crawl.id)
        assert cc.id == crawl.id


        # Links
        l = Link()
        l.type = Link.TYPE_INTERNAL
        l.url = './index.html'
        l.absolute_url = 'http://hotmug.net/index.html'        
        l.crawl_id = crawl.id
        delegate.link_create(l)
        assert l.id > 0 


        l.type = Link.TYPE_EXTERNAL
        delegate.link_update(l)

        l2 = Link()
        l2.type = Link.TYPE_INTERNAL
        l2.url = './contact.html'
        l2.absolute_url = 'http://hotmug.net/contact.html'
        l2.crawl_id = crawl.id
        delegate.link_create(l2)
        assert l2.id > 0


        delegate.crawl_delete(cc)
        



if __name__ == '__main__':
    unittest.main()