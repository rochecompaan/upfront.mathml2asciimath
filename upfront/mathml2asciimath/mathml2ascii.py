import re
import sys
import string
import urllib
import argparse
from xml import sax
from xml.sax.saxutils import XMLGenerator
from cStringIO import StringIO

from symbols import symbolmap

class Element:

    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        self.children = []

tags_handled = ("math", "mrow", "mo", "mi", "mn", "mfrac", "msub",
    "msup", "munder", "msqrt")

atoms = symbolmap.values()
atoms.extend(d for d in string.digits)
atoms.extend(['+', '-', '='])

class MathMLHandler(sax.ContentHandler):
    """ SAX ContentHandler for converting MathML to ASCIIMath.
    """
    
    def __init__(self):
        self.output = ""
        self.currentNode = None
        self.previousNode = None
        self.stack = []

    def startElementNS(self, name, qname, attributes):
        name = name[-1]
        self.skip = name not in tags_handled
        parent = self.stack and self.stack[-1] or None
        e = Element(name, parent)
        self.currentNode = e
        if parent:
            parent.children.append(e)
        self.stack.append(e)
        if name == "msqrt":
            self.output += "sqrt("
        if name == "mrow" and parent.name in ("mfrac", "msub", "munder"):
            self.output += "("

    def endElementNS(self, name, qname): 
        if self.skip:
            return
        name = name[-1]
        currentNode = self.stack.pop()
        self.previousNode = currentNode
        parent = currentNode.parent
        parentname = parent and parent.name or ""
        if parentname == "msup" and len(parent.children) == 1:
            self.output += "^"
        if parentname in ("msub", "munder") and len(parent.children) == 1:
            self.output += "_"
        if name == "mrow" and parent.name in ("mfrac", "msub", "munder"):
            self.output += ")"
        if parentname == "mfrac" and len(parent.children) == 1:
            self.output += "/"
        if name == "msqrt":
            self.output += ")"

    def characters(self, content):
        if self.skip:
            return
        key = (self.currentNode.name, content)
        content = symbolmap.get(key, content)
        prevchar = self.output and self.output[-1] or ""
        symbol = prevchar + content 
        if prevchar and symbol not in atoms and \
                        content not in atoms and \
                        prevchar not in atoms:
            self.output += ' '
        # pad in with spaces
        if content in ('in', '!in'):
            content = ' %s ' % content
        self.output += content

def convert(mathml):
    handler = MathMLHandler()

    # Parse input file with a namespace-aware SAX parser
    parser = sax.make_parser()
    parser.setFeature(sax.handler.feature_namespaces, 1)
    parser.setContentHandler(handler)       
    # remove whitespace
    mathml = mathml.replace('\n', '')
    mathml = re.sub(r'>\s*<', '><', mathml)
    parser.parse(StringIO(mathml))

    return handler.output

def main():
    parser = argparse.ArgumentParser(description='Convert MathML to ASCIIMath')
    parser.add_argument('file', help='/path/to/file') 
    args = parser.parse_args()

    mathml = urllib.urlopen(args.file).read()

    print convert(mathml)

if __name__ == '__main__':
    main()

