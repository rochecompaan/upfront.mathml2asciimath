import re
import sys
from xml import sax
from xml.sax.saxutils import XMLGenerator
from cStringIO import StringIO

class Element:

    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        self.children = []


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
        parent = self.stack and self.stack[-1] or None
        e = Element(name, parent)
        self.currentNode = e
        if parent:
            parent.children.append(e)
        self.stack.append(e)
        if name == 'mrow':
            self.output += "("
        if name == "msqrt":
            self.output += "sqrt"
        if self.previousNode:
            if name == 'mi' and self.previousNode.name == 'mfrac':
                self.output += " "
            

    def endElementNS(self, name, qname): 
        name = name[-1]
        currentNode = self.stack.pop()
        self.previousNode = currentNode
        parent = currentNode.parent
        parentname = parent and parent.name or ""
        if name in ('mrow',):
            self.output += ")"
        if parentname == "msup" and len(parent.children) == 1:
            self.output += "^"
        if parentname == "mfrac":
            if len(parent.children) == 1:
                self.output += "/"

    def characters(self, content):
        if content in "()":
            return
        if self.currentNode.name == 'mo' and content.encode('utf-8') == '±':
            self.output += "+-"
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



if __name__ == "__main__":

    output = convert("""\
<math title="x^2+b/a x+(b/(2a))^2-(b/(2a))^2+c/a=0">
    <msup>
        <mi>x</mi>
        <mn>2</mn>
    </msup>
    <mo>+</mo>
    <mfrac>
        <mi>b</mi>
        <mi>a</mi>
    </mfrac>
    <mi>x</mi>
    <mo>+</mo>
    <msup>
        <mrow>
            <mo>(</mo>
            <mfrac>
                <mi>b</mi>
                <mrow>
                    <mn>2</mn>
                    <mi>a</mi>
                </mrow>
            </mfrac>
            <mo>)</mo>
        </mrow>
        <mn>2</mn>
    </msup>
    <mo>-</mo>
    <msup>
        <mrow>
            <mo>(</mo>
            <mfrac>
                <mi>b</mi>
                <mrow>
                    <mn>2</mn>
                    <mi>a</mi>
                </mrow>
            </mfrac>
            <mo>)</mo>
        </mrow>
        <mn>2</mn>
    </msup>
    <mo>+</mo>
    <mfrac>
        <mi>c</mi>
        <mi>a</mi>
    </mfrac>
    <mo>=</mo>
    <mn>0</mn>
</math>""")
    expected = "x^2+b/a x+(b/(2a))^2-(b/(2a))^2+c/a=0"
    print output
    assert output == expected

    output = convert("""\
<math title="(x+b/(2a))^2=(b^2)/(4a^2)-c/a.">
    <msup>
        <mrow>
            <mo>(</mo>
            <mi>x</mi>
            <mo>+</mo>
            <mfrac>
                <mi>b</mi>
                <mrow>
                    <mn>2</mn>
                    <mi>a</mi>
                </mrow>
            </mfrac>
            <mo>)</mo>
        </mrow>
        <mn>2</mn>
    </msup>
    <mo>=</mo>
    <mfrac>
        <mrow>
            <msup>
                <mi>b</mi>
                <mn>2</mn>
            </msup>
        </mrow>
        <mrow>
            <mn>4</mn>
            <msup>
                <mi>a</mi>
                <mn>2</mn>
            </msup>
        </mrow>
    </mfrac>
    <mo>-</mo>
    <mfrac>
        <mi>c</mi>
        <mi>a</mi>
    </mfrac>
    <mo>.</mo>
</math>""")
    print output
    assert output == "(x+b/(2a))^2=(b^2)/(4a^2)-c/a."

    output = convert("""\
<math title="x+b/(2a)=+-sqrt((b^2)/(4a^2)-c/a). ">
    <mi>x</mi>
    <mo>+</mo>
    <mfrac>
        <mi>b</mi>
        <mrow>
            <mn>2</mn>
            <mi>a</mi>
        </mrow>
    </mfrac>
    <mo>=</mo>
    <mo>±</mo>
    <msqrt>
        <mrow>
            <mfrac>
                <mrow>
                    <msup>
                        <mi>b</mi>
                        <mn>2</mn>
                    </msup>
                </mrow>
                <mrow>
                    <mn>4</mn>
                    <msup>
                        <mi>a</mi>
                        <mn>2</mn>
                    </msup>
                </mrow>
            </mfrac>
            <mo>-</mo>
            <mfrac>
                <mi>c</mi>
                <mi>a</mi>
            </mfrac>
        </mrow>
    </msqrt>
    <mo>.</mo>
</math>""")
    print output
    assert output == "x+b/(2a)=+-sqrt((b^2)/(4a^2)-c/a)."

    output = convert("""\
<math title="(x+b/(2a))^2=(b^2)/(4a^2)-c/a.">
  <mstyle mathsize="1em" mathcolor="blue" fontfamily="serif" displaystyle="true">
    <msup>
      <mrow>
        <mo>(</mo>
        <mi>x</mi>
        <mo>+</mo>
        <mfrac>
          <mi>b</mi>
          <mrow>
            <mn>2</mn>
            <mi>a</mi>
          </mrow>
        </mfrac>
        <mo>)</mo>
      </mrow>
      <mn>2</mn>
    </msup>
    <mo>=</mo>
    <mfrac>
      <mrow>
        <msup>
          <mi>b</mi>
          <mn>2</mn>
        </msup>
      </mrow>
      <mrow>
        <mn>4</mn>
        <msup>
          <mi>a</mi>
          <mn>2</mn>
        </msup>
      </mrow>
    </mfrac>
    <mo>-</mo>
    <mfrac>
      <mi>c</mi>
      <mi>a</mi>
    </mfrac>
    <mo>.</mo>
  </mstyle>
</math>""")
    print output
    assert output == "(x+b/(2a))^2=(b^2)/(4a^2)-c/a."

    output = convert("""\
<math title="x_(1,2)=(-b+-sqrt(b^2-4a c))/(2a) ">
  <mstyle mathsize="1em" mathcolor="blue" fontfamily="serif" displaystyle="true">
    <msub>
      <mi>x</mi>
      <mrow>
        <mn>1</mn>
        <mo>,</mo>
        <mn>2</mn>
      </mrow>
    </msub>
    <mo>=</mo>
    <mfrac>
      <mrow>
        <mo>-</mo>
        <mi>b</mi>
        <mo>&#xB1;</mo>
        <msqrt>
          <mrow>
            <msup>
              <mi>b</mi>
              <mn>2</mn>
            </msup>
            <mo>-</mo>
            <mn>4</mn>
            <mi>a</mi>
            <mi>c</mi>
          </mrow>
        </msqrt>
      </mrow>
      <mrow>
        <mn>2</mn>
        <mi>a</mi>
      </mrow>
    </mfrac>
  </mstyle>
</math>""")
    print output
    assert output == "x_(1,2)=(-b+-sqrt(b^2-4a c))/(2a) "
