import unittest
import os
import re
import glob
import unittest
from StringIO import StringIO
from xml.dom.minidom import parseString

from upfront.mathml2asciimath.mathml2ascii import convert

dirname = os.path.dirname(__file__)

class TestConvert(unittest.TestCase):

    def setUp(self):
        self.cwd = os.getcwd()
        os.chdir(dirname)

    def tearDown(self):
        os.chdir(self.cwd)

    def test_convert(self):
        for filename in glob.glob('*.mml'):
            mathml = open(filename).read()
            dom = parseString(mathml)
            mathnode = dom.getElementsByTagName('math')[0]
            asciimath = mathnode.getAttribute('title')
            self.assertEqual(asciimath, convert(mathml))



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestConvert))
    return suite

