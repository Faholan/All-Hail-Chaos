"""MIT License

Copyright (c) 2020 Faholan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""

from discord.utils import find

from html.parser import HTMLParser

class MarkdownParser(HTMLParser):
    def feed(self, input):
        """Feeds text to the process"""
        self.output = ""
        self.a_end = ""
        super().feed(input)
        return self.output

    def handle_starttag(self, tag, attrs):
        """Converts the opening tag to markdown."""
        if tag == 'a':
            href = find(lambda h:h[0] == 'href', attrs)
            if not href:
                return
            self.output += "[__"
            self.a_end = f"__]({href[1]}"
            title = find(lambda h:h[0] == 'title', attrs)
            if title:
                self.a_end += f' "{title[1]}"'
            self.a_end += ")"
        elif tag == 'b':
            self.output += "**"
        elif tag == "i" or tag == "em":
            self.output += "*"
        elif tag == "script":
            self.output += "```\n"

    def handle_endtag(self, tag):
        """Converts the closing tag to markdown"""
        if tag == "a":
            self.output += self.a_end
            self.a_end = ""
        elif tag == 'b':
            self.output += "**"
        elif tag == "i" or tag == "em":
            self.output += "*"
        elif tag == "script":
            self.output += "\n```"

    def handle_startendtag(self, tag, attrs):
        """Converts an empty tag to markdown"""
        if tag == "img":
            src = find(lambda h:h[0] == 'src', attrs)
            if not src:
                return
            self.output += f"[__Image__]({src}"
            alt = find(lambda h:h[0] == 'alt', attrs)
            if alt:
                self.output += f' "{alt}"'
            self.output += ')'
        elif tag == "br":
            self.output += "\n"

    def handle_data(self, data):
        """Just a stupid ass copy-paste"""
        self.output += data

def setup(bot):
    bot.markdownhtml = MarkdownParser
