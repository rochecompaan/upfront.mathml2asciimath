import unittest
import os
import re
import glob
import unittest
from StringIO import StringIO

from upfront.mathml2asciimath import transform

dirname = os.path.dirname(__file__)

class TestTransform(unittest.TestCase):

    def setUp(self):
        self.cwd = os.getcwd()
        os.chdir(dirname)

    def tearDown(self):
        os.chdir(self.cwd)

    def test_transform(self):
        self.assertEqual(transform("""<math title="x^2+b/a x+(b/(2a))^2-(b/(2a))^2+c/a=0"><mstyle mathsize="1em" mathcolor="blue" fontfamily="serif" displaystyle="true"><msup><mi _moz-math-font-style="italic">x</mi><mn>2</mn></msup><mo>+</mo><mfrac><mi _moz-math-font-style="italic">b</mi><mi _moz-math-font-style="italic">a</mi></mfrac><mi _moz-math-font-style="italic">x</mi><mo>+</mo><msup><mrow><mo>(</mo><mfrac><mi _moz-math-font-style="italic">b</mi><mrow><mn>2</mn><mi _moz-math-font-style="italic">a</mi></mrow></mfrac><mo>)</mo></mrow><mn>2</mn></msup><mo>-</mo><msup><mrow><mo>(</mo><mfrac><mi _moz-math-font-style="italic">b</mi><mrow><mn>2</mn><mi _moz-math-font-style="italic">a</mi></mrow></mfrac><mo>)</mo></mrow><mn>2</mn></msup><mo>+</mo><mfrac><mi _moz-math-font-style="italic">c</mi><mi _moz-math-font-style="italic">a</mi></mfrac><mo>=</mo><mn>0</mn></mstyle></math>"""), "x^2+b/a x+(b/(2a))^2-(b/(2a))^2+c/a =0")


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTransform))
    return suite

