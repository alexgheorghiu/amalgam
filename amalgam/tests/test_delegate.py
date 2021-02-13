import unittest
import sys

from flask_sqlalchemy import SQLAlchemy

from amalgam.models import inside
from amalgam.models.models import *
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


    def test_site(self):
        # session = delegate.get_session()

        # Site 1
        site1 = Site()	
        site1.name = "Site1"        
        delegate.site_create(site1)
        

        siteId = site1.id
        assert siteId > 0 

        # Site 2
        site2 = Site()	
        site2.name = "Site2"
        delegate.site_create(site2)

        # # User.query.all()
        # f = session.query(Site).first()
        # assert f.id > 0 

        sites = delegate.site_get_all()
        print("No of site: {}".format(len(sites)))
        assert len(sites) == 2


        delegate.site_delete_all()


    def test_crawl(self):
        print("test_crawl started")
        # session = delegate.get_session()

        # Site 1
        site1 = Site()	
        site1.name = "Site1"        
        delegate.site_create(site1)


        # Crawl
        crawl = Crawl(site_id = site1.id)
        delegate.crawl_create(crawl)
        assert crawl.id > 0


        # Test cascade delete
        assert len(site1.crawls) == 1

        delegate.site_delete(site1)

        sites = delegate.site_get_all()
        print("No of site: {}".format(len(sites)))
        assert len(sites) == 0

        crawls = delegate.crawl_get_all()
        assert len(crawls) == 0

        
        delegate.crawl_delete_all()        
        delegate.site_delete_all()
        print("test_crawl done")


    def test_page(self):
        print("test_page started")
        # Site 1
        site1 = Site()	
        site1.name = "Site1"        
        delegate.site_create(site1)

        # Crawl
        crawl = Crawl(site_id = site1.id)
        delegate.crawl_create(crawl)
        assert crawl.id > 0
        
        # Page
        page = Page()
        page.crawl_id = crawl.id
        page.content = "Ala bala portocala"
        page.absolute_url = "https://scriptoid.com/index.php"
        delegate.page_create(page)
        assert page.id > 0

        pages = delegate.page_get_all()
        assert len(pages) > 0 

        # # Test cascade delete
        delegate.crawl_delete_all()        
        pages = delegate.page_get_all()
        assert len(pages) == 0, "It should be {} but we found {}".format(0, len(pages))

        # # Clean up
        delegate.page_delete_all()
        delegate.crawl_delete_all()
        delegate.site_delete_all()

        print("test_page done")



    def test_link(self):
        print("test_page started")
        # Site 1
        site1 = Site()	
        site1.name = "Site1"        
        delegate.site_create(site1)

        # Crawl
        crawl = Crawl(site_id = site1.id)
        delegate.crawl_create(crawl)
        assert crawl.id > 0
        
        # Page
        page = Page()
        page.crawl_id = crawl.id
        page.content = "Ala bala portocala"
        page.absolute_url = "https://scriptoid.com/index.php"
        delegate.page_create(page)
        

        # Link
        link = Link()
        link.parent_page_id = page.id
        link.url = '/contact'
        link.absolute_url = 'https://scriptoid.com/index.php'
        link.type = Link.TYPE_INTERNAL
        delegate.link_create(link)
        assert link.id > 0

        # Test a cascade delete from parent Page to Link
        delegate.page_delete_all()
        links = delegate.link_get_all()
        assert len(links) == 0

        # Clean up
        # delegate.link_delete_all()
        delegate.page_delete_all()
        delegate.crawl_delete_all()
        delegate.site_delete_all()

        print("test_page done")   


    def test_user(self):
        u1 = User()
        u1.email = "one@foo.com"
        u1.password = "one"
        u1.name = "One"
        delegate.user_create(u1)
        assert u1.id > 0 

        u2 = delegate.user_get_by_email_and_password(u1.email, u1.password)
        assert u1.email == u2.email 
        assert u1.password == u2.password 
        assert u1.id == u2.id, "U1's id:{}  U2's id:{} ".format(u1.id, u2.id)


        delegate.user_delete_all()



    # def test_db(self):        
    #     site = Site()	
    #     site.name = "Hotmugus"
    #     session = delegate.get_session()

    #     session.add(site)
    #     session.commit()

    #     siteId = site.id
    #     assert siteId > 0 
        
    #     # s = Site.query.get(siteId)
    #     # session.delete(site)
    #     # session.commit()

    #     # User.query.all()
    #     f = session.query(Site).first()
    #     assert f.id > 0 

    #     sites = session.query(Site).all()
    #     print("No of site: {}".format(len(sites)))
    #     assert len(sites) > 0

    #     crawl = Crawl(site_id = f.id)
    #     delegate.crawl_create(crawl)
    #     assert crawl.id > 0

    #     cc = delegate.crawl_get_by_id(crawl.id)
    #     assert cc.id == crawl.id


    #     # Links
    #     l = Link()
    #     l.type = Link.TYPE_INTERNAL
    #     l.url = './index.html'
    #     l.absolute_url = 'http://hotmug.net/index.html'        
    #     l.crawl_id = crawl.id
    #     delegate.link_create(l)
    #     assert l.id > 0 


    #     l.type = Link.TYPE_EXTERNAL
    #     delegate.link_update(l)

    #     l2 = Link()
    #     l2.type = Link.TYPE_INTERNAL
    #     l2.url = './contact.html'
    #     l2.absolute_url = 'http://hotmug.net/contact.html'
    #     l2.crawl_id = crawl.id
    #     delegate.link_create(l2)
    #     assert l2.id > 0

    #     # Pages
    #     p = Page()
    #     p.absolute_url = l.absolute_url
    #     p.crawl_id = crawl.id
    #     delegate.page_create(p)
        
    #     l.destination_page_id = p.id
    #     delegate.link_update(l)


    #     delegate.crawl_delete(cc)
        



if __name__ == '__main__':
    unittest.main()