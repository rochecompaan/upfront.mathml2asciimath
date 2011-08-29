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

known_chars = string.digits + string.ascii_letters + string.punctuation
known_chars += "".join(atoms)

class MathMLHandler(sax.ContentHandler):
    """ SAX ContentHandler for converting MathML to ASCIIMath.
    """
    
    def __init__(self):
        self.output = ""
        self.currentNode = None
        self.previousNode = None
        self.prevchar = ""
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
            self.write("sqrt")
            # separate write for opening bracket to ensure only the
            # bracket is set as prevchar
            self.write("(")
        elif name == "mrow" and parent and \
                              parent.name in ("mfrac", "msub", "munder"):
            self.write("(")

        elif name == "mover":
            self.write("__mover_marker__")

        elif name == "mfenced":
            self.write("(")

    def endElementNS(self, name, qname): 
        if self.skip:
            return
        name = name[-1]
        currentNode = self.stack.pop()
        self.previousNode = currentNode
        parent = currentNode.parent
        parentname = parent and parent.name or ""
        if name in ("msqrt", "mfenced"):
            self.write(")")
        if parent:
            if parentname == "msup" and len(parent.children) == 1:
                self.write("^")
            if parentname in ("msub", "munder") and len(parent.children) == 1:
                self.write("_")
            if name == "mrow" and parentname in ("mfrac", "msub", "munder"):
                self.write(")")
            if parentname == "mfrac" and len(parent.children) == 1:
                self.write("/")
        if name == "mover" and "__mover_marker__" in self.output:
            raise RuntimeError("Unrecognised mover symbol in %s" % self.output)

    def characters(self, content):
        if self.skip:
            return
        parentname = self.currentNode.parent and \
            self.currentNode.parent.name or None
        for nodename in (self.currentNode.name, parentname):
            key = (nodename, content)
            if symbolmap.has_key(key):
                content = symbolmap.get(key)

        symbol = self.prevchar + content 
        if self.prevchar and symbol not in atoms and \
                             content not in atoms and \
                             self.prevchar not in atoms:
            self.write(' ')
        elif content not in atoms and len(content) > 1:
            # add spaces between characters that are not recognized
            # symbols
            s = ""
            for char in content:
                if s and s[-1] not in string.digits:
                    s += " "
                if char not in known_chars:
                    raise RuntimeError("unknown character: %s (%s)" % 
                                       (char, hex(ord(char))))
                s += char
            content = s

        if parentname == 'mover':
            if len(self.currentNode.parent.children) == 2:
                self.output = self.output.replace('__mover_marker__',
                                                  " %s" % content)
                return

        # pad in with spaces
        if content in ('in', '!in'):
            content = ' %s ' % content
        self.prevchar = content
        self.write(content)

    def write(self, content):
        self.output += content
        self.prevchar = content

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

