class InternalLinksManager:
    def __init__(self, parser):
        # This list containes the internal links created
        # in the text through a macro.
        self.links = []

        # This dictionary contains the headers
        # flagged with an id
        self.headers = {}

        # This is the parser that contains the manager
        self.parser = parser

    def add_header(self, header_id, node):
        if header_id in self.headers:
            self.parser._error(f"Duplicate header id detected: {header_id}")

        self.headers[header_id] = node

    def process_links(self):
        for link in self.links:
            try:
                link.header = self.headers[link.header_id]
            except KeyError:
                self.parser._error(f"Cannot find header with id {link.header_id}")

    def update(self, other):
        self.update_links(other.links)
        self.headers.update(other.headers)

    def update_links(self, links):
        self.links.extend(links)
