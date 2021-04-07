import unittest
# from amalgam.tests.test_delegate import TestDelegate
from amalgam.tests.test_xdelegate import TestDelegate
from amalgam.tests.test_crawler import TestCrawler


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestDelegate())
    suite.addTest(TestCrawler())    
    return suite

if __name__ == '__main__':
    unittest.main()
    # runner = unittest.TextTestRunner()
    # runner.run(suite())