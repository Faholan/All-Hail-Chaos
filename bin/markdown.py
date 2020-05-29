from html.parser import HTMLParser
from discord.utils import find

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
        elif tag == "i":
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
        elif tag == "i":
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
