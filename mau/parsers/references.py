import hashlib

from mau.nodes.references import ReferencesEntryNode


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
        data = reference_data[key]
        reference.content = data["content"]
        anchor = reference_anchor(reference.content)
        content_type = reference.content_type

        reference.reference_anchor = f"ref-{content_type}-{reference.number}-{anchor}"
        reference.content_anchor = f"cnt-{content_type}-{reference.number}-{anchor}"

        references[key] = ReferencesEntryNode(
            content_type=reference.content_type,
            content=reference.content,
            number=reference.number,
            title=reference.title,
            reference_anchor=reference.reference_anchor,
            content_anchor=reference.content_anchor,
        )

    return references
