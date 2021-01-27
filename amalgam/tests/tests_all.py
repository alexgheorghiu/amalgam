import unittest
from amalgam.tests.test_models import TestModels
from amalgam.tests.test_crawler import TestCrawler


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestModels())
    suite.addTest(TestCrawler())    
    return suite

if __name__ == '__main__':
    unittest.main()
    # runner = unittest.TextTestRunner()
    # runner.run(suite())