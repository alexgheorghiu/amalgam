import unittest
import sys
import threading
import time
import time

now = lambda : time.time()
# ms = time.time()*1000.0

from flask_sqlalchemy import SQLAlchemy

from amalgam.models import inside
from amalgam.models.models import *
from amalgam.delegate import Delegate
from amalgam.database import get_session


class TestDelegate(unittest.TestCase):

    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test_inside(self):
        links = []

        needle = Url(absolute_url = "https://amalgam.scriptoid.com", url = "/home", type=Url.TYPE_INTERNAL)
        assert not inside(needle, links)

        l = Url(absolute_url = "https://amalgam.scriptoid.com", url = "/home", type=Url.TYPE_INTERNAL)
        links.append(l)

        l = Url(absolute_url = "https://amalgam.scriptoid.com/contact", url = "/contact", type=Url.TYPE_INTERNAL)
        links.append(l)

        assert inside(needle, links)


    def test_site(self):
        delegate = Delegate(get_session())

        # session = delegate.get_session()

        # Site 1
        site1 = Site()	
        site1.name = "Site1"       
        site1.url = 'http://foo.com' 
        delegate.site_create(site1)
        

        siteId = site1.id
        assert siteId > 0 

        # Site 2
        site2 = Site()	
        site2.name = "Site2"
        site2.url = 'http://foo.com'
        delegate.site_create(site2)

        # # User.query.all()
        # f = session.query(Site).first()
        # assert f.id > 0 

        sites = delegate.site_get_all()
        print("No of site: {}".format(len(sites)))
        assert len(sites) == 2


        delegate.site_delete_all()


    def test_crawl(self):
        delegate = Delegate(get_session())

        print("test_crawl started")
        # session = delegate.get_session()

        # Site 1
        site1 = Site()	
        site1.name = "Site1"      
        site1.url = 'http://foo.com'  
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
        delegate = Delegate(get_session())

        print("test_page started")
        # Site 1
        site1 = Site()	
        site1.name = "Site1"
        site1.url = 'http://foo.com'
        delegate.site_create(site1)

        # Crawl
        crawl = Crawl(site_id = site1.id)
        delegate.crawl_create(crawl)
        assert crawl.id > 0

        no_pages = delegate.resource_count_visited(crawl.id)
        assert no_pages == 0, "No of pages is {}".format(no_pages)

        # Page
        page = Resource()
        page.crawl_id = crawl.id
        page.content = "A long content " + "a" * 1024 * 1024
        page.absolute_url = "https://scriptoid.com/index.php"
        delegate.resource_create(page)
        assert page.id > 0

        pages = delegate.resource_get_all()
        assert len(pages) > 0 

        no_pages = delegate.resource_count_visited(crawl.id)
        assert no_pages == 1, "No of pages is {}".format(no_pages)

        # # Test cascade delete
        delegate.crawl_delete_all()        
        pages = delegate.resource_get_all()
        assert len(pages) == 0, "It should be {} but we found {}".format(0, len(pages))

        # # Clean up
        delegate.resource_delete_all()
        delegate.crawl_delete_all()
        delegate.site_delete_all()

        print("test_page done")



    def test_link(self):
        delegate = Delegate(get_session())

        print("test_page started")
        # Site 1
        site1 = Site()	
        site1.name = "Site1" 
        site1.url = 'http://foo.com'       
        delegate.site_create(site1)

        # Crawl
        crawl = Crawl(site_id = site1.id)
        delegate.crawl_create(crawl)
        assert crawl.id > 0
        
        # Page
        page = Resource()
        page.crawl_id = crawl.id
        page.content = "Ala bala portocala"
        page.absolute_url = "https://scriptoid.com/index.php"
        delegate.resource_create(page)        

        # Link
        url = Url()
        url.src_resource_id = page.id
        url.url = '/team'
        url.absolute_url = 'https://scriptoid.com/team'
        url.type = Url.TYPE_INTERNAL
        url.crawl_id = crawl.id
        url.job_status = Url.JOB_STATUS_IN_PROGRESS
        delegate.url_create(url)

        url = Url()
        url.src_resource_id = page.id
        url.url = '/contact'
        url.absolute_url = 'https://scriptoid.com/index.php'
        url.type = Url.TYPE_INTERNAL
        url.crawl_id = crawl.id
        delegate.url_create(url)
        assert url.id > 0

        # Test first unvisited link
        l1 = delegate.url_get_first_unvisited(crawl_id=crawl.id)
        assert l1.id == url.id, 'L1 is {}'.format(l1)

        n1 = delegate.url_count_unvisited(crawl_id=crawl.id)
        assert n1 == 1, 'n1 is {}'.format(n1)

        n2 = delegate.url_count_visited(crawl_id=crawl.id)
        assert n2 == 0, 'Actually n2 is {}'.format(n2)

        url.job_status = Url.JOB_STATUS_VISITED
        delegate.url_update(url)
        l1 = delegate.url_get_first_unvisited(crawl_id=crawl.id)
        assert l1 is None, 'L1 is {}'.format(l1)

        n1 = delegate.url_count_unvisited(crawl_id=crawl.id)
        assert n1 == 0, 'n1 is {}'.format(n1)

        n2 = delegate.url_count_visited(crawl_id=crawl.id)
        assert n2 == 1, 'n2 is {}'.format(n2)

        # Test a cascade delete from parent Page to Link
        delegate.resource_delete_all()
        links = delegate.url_get_all()
        assert len(links) == 0, "When actually there are {}".format(len(links))

        # Clean up
        # delegate.link_delete_all()
        delegate.resource_delete_all()
        delegate.crawl_delete_all()
        delegate.site_delete_all()

        print("test_page done")   


    def test_user(self):
        delegate = Delegate(get_session())

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


    def test_threading(self):
        delegate = Delegate(get_session())

        lock = threading.Lock()
        print("\n")

        def create(tid):
            print("[%s] [%f] Create started." % (threading.currentThread().getName(), now()))
            with lock:
                print("[%s] [%f] Lock acquired" % (threading.currentThread().getName(), now()))
                user = User(name="john", email='john@foo.com', password='1234')
                delegate.user_create(user)

        def update(tid):
            print("[%s] [%f] Update started." % (threading.currentThread().getName(), now()))
            with lock:
                print("[%s] [%f] Lock acquired" % (threading.currentThread().getName(), now()))
                user = delegate.user_get_by_email_and_password(email="john@foo.com", password='1234')
                user.name = 'mary'
                delegate.user_update(user)
                print("[%s] [%f] Update job done." % (threading.currentThread().getName(), now()))
            # time.sleep(5)
            print("[%s] [%f] Update finished." % (threading.currentThread().getName(), now()))

        def retrive(tid):
            time.sleep(1)
            print("[%s] [%f] Retrieve started." % (threading.currentThread().getName(), now()))
            with lock:
                print("[%s] [%f] Lock acquired" % (threading.currentThread().getName(), now()))
                user = delegate.user_get_by_email_and_password(email="john@foo.com", password='1234')
                assert user.name == 'mary', "Actually the name is: {}".format(user.name)
            # time.sleep(10)

        t1 = threading.Thread(target=create, args=(1,))
        t1.start()
        t1.join()

        t2 = threading.Thread(target=update, args=(2,))
        t2.start()

        t3 = threading.Thread(target=retrive, args=(3,))
        t3.start()


        t2.join()
        t3.join()

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
        
    #     l.destination_resource_id = p.id
    #     delegate.link_update(l)


    #     delegate.crawl_delete(cc)
        



if __name__ == '__main__':
    unittest.main()