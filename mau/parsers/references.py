import hashlib

from mau.nodes.references import ReferencesEntryNode, ReferencesNode


class ReferencesManager:
    def __init__(self, parser):
        # This dictionary containes the references created
        # in the text through a macro.
        self.mentions = {}

        # This dictionary contains the content of each
        # reference created through blocks.
        self.data = {}

        # This list contains all the references contained
        # in this parser in the form
        # {content_type:[references]}.
        self.references = {}

        # This is the list of ::references commands
        # that need to be updated once references
        # have been processed
        self.command_nodes = []

        # This is the parser that contains the manager
        self.parser = parser

    def create_node(self, content_type, subtype, args, kwargs, tags):
        node = ReferencesNode(
            content_type=content_type,
            subtype=subtype,
            args=args,
            kwargs=kwargs,
            tags=tags,
        )

        self.command_nodes.append(node)
        self.parser.save(node)

    def add_data(self, content_type, name, content):
        self.data[(content_type, name)] = content

    def process_references(self):
        references = create_references(
            self.mentions,
            self.data,
        )

        # Filter references according to the node parameters
        for node in self.command_nodes:
            node.children = [
                i for i in references.values() if i.content_type == node.content_type
            ]

        return references

    def update(self, other):
        self.update_mentions(other.mentions)
        self.data.update(other.data)

    def update_mentions(self, mentions):
        self.mentions.update(mentions)


def reference_anchor(content):
    return hashlib.md5(str(content).encode("utf-8")).hexdigest()[:8]


def create_references(reference_mentions, reference_data):
    # Example of stored content
    # reference_mentions = {
    #  (type1, name1) = node1
    #  (type1, name2) = node2
    #  (type2, name3) = node3
    # }
    #
    # reference_data = {
    #  (type1, name1) = content
    #  (type1, name2) = content
    #  (type2, name3) = content
    # }

    references = {}

    for num, reference in enumerate(reference_mentions.values(), start=1):
        reference.number = num

    for key, reference in reference_mentions.items():
        reference.children = reference_data[key]
        anchor = reference_anchor(reference.children)
        content_type = reference.content_type

        reference.reference_anchor = f"ref-{content_type}-{reference.number}-{anchor}"
        reference.content_anchor = f"cnt-{content_type}-{reference.number}-{anchor}"

        references[key] = ReferencesEntryNode(
            content_type=reference.content_type,
            children=reference.children,
            number=reference.number,
            title=reference.title,
            reference_anchor=reference.reference_anchor,
            content_anchor=reference.content_anchor,
        )

    return references
