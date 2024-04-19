import hashlib

from mau.nodes.footnotes import FootnotesNode


class FootnotesManager:
    def __init__(self, parser):
        # This dictionary containes the footnotes created
        # in the text through a macro.
        self.mentions = {}

        # This dictionary contains the content of each
        # footnote created through blocks.
        # This is a helper dictionary that will be merged
        # with self.footnotes once the parsing is completed.
        self.data = {}

        # This list contains all the footnote entries
        # that will be shown by a footnotes command.
        self.footnotes = []

        # This is the list of ::footnotes commands
        # that need to be updated once footnotes
        # have been processed
        self.command_nodes = []

        # This is the parser that contains the manager
        self.parser = parser

    def create_node(self, subtype, args, kwargs, tags):
        # This creates an empty FootnotesNode
        # that will be stored in the parser
        # and in the command_nodes list.
        # The method process_footnotes will
        # eventually update all these nodes
        # with the right entries.
        node = FootnotesNode(
            subtype=subtype,
            args=args,
            kwargs=kwargs,
            tags=tags,
        )

        self.command_nodes.append(node)
        self.parser.save(node)

    def add_data(self, name, content):
        self.data[name] = content

    def process_footnotes(self):
        self.footnotes = create_footnotes(
            self.mentions,
            self.data,
        )

        for node in self.command_nodes:
            # create_footnotes is called
            # multiple times to create new
            # entries for each command.
            # If we don't do it, all commands
            # will share the same entries and in case
            # of multiple ::footnotes: the parent
            # of all entries will be the last
            # command footnotes.
            node.add_children(
                create_footnotes(
                    self.mentions,
                    self.data,
                )
            )

            # node.children = create_footnotes(
            #     self.mentions,
            #     self.data,
            # )

            # for child in node.children:
            #     child.parent = node

    def update(self, other):
        self.update_mentions(other.mentions)
        self.data.update(other.data)
        self.command_nodes.extend(other.command_nodes)

    def update_mentions(self, mentions):
        # Retrieve the footnotes
        # The format of this dictionary is
        # {name: node}
        text_footnotes = set(mentions.keys())
        existing_footnotes = set(self.mentions.keys())
        duplicate_footnotes = set.intersection(existing_footnotes, text_footnotes)

        if duplicate_footnotes:
            duplicates_list = ", ".join(duplicate_footnotes)
            self.parser._error(f"Duplicate footnotes detected: {duplicates_list}")

        self.mentions.update(mentions)


def footnote_anchor(content):
    return hashlib.md5(str(content).encode("utf-8")).hexdigest()[:8]


def create_footnotes(footnote_mentions, footnote_data):
    footnotes = []

    for num, footnote in enumerate(footnote_mentions.values(), start=1):
        footnote.number = num

    for key, footnote in footnote_mentions.items():
        data = footnote_data[key]
        footnote.children = data
        anchor = footnote_anchor(footnote.children)

        footnote.reference_anchor = f"ref-footnote-{footnote.number}-{anchor}"
        footnote.content_anchor = f"cnt-footnote-{footnote.number}-{anchor}"

        footnotes.append(footnote.to_entry())

    return footnotes
