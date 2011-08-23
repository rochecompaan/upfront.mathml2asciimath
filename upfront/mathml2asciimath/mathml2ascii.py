import re
import sys
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
        if name == 'mrow':
            self.output += "("
        elif name == "msqrt":
            self.output += "sqrt"
        if self.previousNode:
            if name in ('mi', 'mn') and self.previousNode.name == 'mfrac':
                self.output += " "
            if name in ('mi', 'mo') and \
                    self.previousNode.name in ('mi', 'mo') and \
                    parent.name != 'mfrac':
                self.output += " "
            

    def endElementNS(self, name, qname): 
        if self.skip:
            return
        name = name[-1]
        currentNode = self.stack.pop()
        self.previousNode = currentNode
        parent = currentNode.parent
        parentname = parent and parent.name or ""
        if name in ('mrow',):
            self.output += ")"
        if parentname == "msup" and len(parent.children) == 1:
            self.output += "^"
        if parentname in ("msub", "munder") and len(parent.children) == 1:
            self.output += "_"
        if parentname == "mfrac" and len(parent.children) == 1:
            self.output += "/"


    def characters(self, content):
        if self.skip or content in "()":
            return
        if self.currentNode.name == 'mo' and symbolmap.has_key(content):
            self.output += symbolmap.get(content)
        else:
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
