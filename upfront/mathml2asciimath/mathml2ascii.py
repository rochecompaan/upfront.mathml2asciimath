import re
import sys
import string
import urllib
import argparse
from xml import sax
from xml.sax.saxutils import XMLGenerator
from cStringIO import StringIO

from symbols import symboltagmap, symbolmap

class Element:

    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        self.children = []

tags_handled = ("math", "mrow", "mo", "mi", "mn", "mfrac", "msub",
    "msup", "munder", "munderover", "msqrt", "mtext")

atoms = symboltagmap.values()
atoms.extend(d for d in string.digits)
atoms.extend(['+', '-', '='])

known_chars = string.digits + string.ascii_letters + string.punctuation
known_chars += "".join(atoms)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

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
        parentnames = [n.name for n in self.stack]
        self.skip = name not in tags_handled or "mphantom" in parentnames
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
                                parent.name in ("mfrac", "msub", "munder",
                                                "munderover"):
            self.write("(")

        elif name == "mover":
            self.write("__mover_marker__")

        elif name == "mfenced":
            self.write("(")

        elif name == "mtext":
            self.write('"')

    def endElementNS(self, name, qname): 
        currentNode = self.stack.pop()
        if self.skip:
            return
        name = name[-1]
        parent = currentNode.parent
        parentname = parent and parent.name or ""
        if name in ("msqrt", "mfenced"):
            self.write(")")
        if name == "mtext":
            self.write('"')
        if parent:
            if name == "mrow" and parentname in ("mfrac", "msub", "munder",
                                                 "munderover"):
                # don't duplicate brackets
                if not (self.output[-1] == ')' and \
                        self.previousNode.name == 'mo'):
                    self.write(")")
            if parentname == "msup" and len(parent.children) == 1:
                self.write("^")
            if parentname in ("msub", "munder") and len(parent.children) == 1:
                self.write("_")
            if parentname == "mfrac" and len(parent.children) == 1:
                self.write("/")
            if parentname == "munderover":
                if len(parent.children) == 1:
                    self.write("_")
                elif len(parent.children) == 2:
                    self.write("^")
        if name == "mover" and "__mover_marker__" in self.output:
            raise RuntimeError("Unrecognised mover symbol in %s" % self.output)

        self.previousNode = currentNode

    def characters(self, content):
        if self.skip:
            return
        name = self.currentNode.name
        # write out mtext as we receive it
        if name == 'mtext':
            self.write(content)
            return
        parentname = self.currentNode.parent and \
            self.currentNode.parent.name or None
        for nodename in (name, parentname):
            key = (nodename, content)
            if symboltagmap.has_key(key):
                content = symboltagmap.get(key)
            # let's try and map it anyway since some symbols are used in
            # both mo and mi tags
            elif symbolmap.has_key(content):
                content = symbolmap.get(content)

        symbol = self.prevchar + content 

        if self.prevchar and symbol not in atoms and \
                             content not in atoms and \
                             self.prevchar not in atoms:
            self.write(' ')
        # don't concatenate adjacent numbers
        elif self.prevchar and is_number(self.prevchar) and is_number(content):
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

        # don't duplicate brackets. closing bracket handled in
        # endElementNS
        if len(self.output) > 0 and content == "(" and name == "mo" and \
                parentname == "mrow" and self.output[-1] == content:
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

