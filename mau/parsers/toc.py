from mau.nodes.toc import TocEntryNode


def create_toc(headers, exclude_tag=None):
    # Create the TOC from the list of headers.

    nodes = []
    latest_by_level = {}

    for header_node in headers:
        # This is the current node
        node = TocEntryNode(
            header_node.value,
            header_node.anchor,
            args=header_node.args,
            kwargs=header_node.kwargs,
            tags=header_node.tags,
        )
        level = int(header_node.level)

        # This collects the latest node added with a given level
        latest_by_level[level] = node

        try:
            # Simplest case, add it to the latest one
            # with a level just 1 step lower
            latest_by_level[level - 1].children.append(node)
        except KeyError:
            # Find all the latest ones added with a level lower than this
            latest = [latest_by_level.get(i, None) for i in range(1, level)]

            # Get the children list of each one, plus nodes for the root
            children = [nodes] + [i.children for i in latest if i is not None]

            # Get the nearest one and append to that
            children[-1].append(node)

    if exclude_tag:
        nodes = exclude_entries(nodes, exclude_tag)

    return nodes


def exclude_entries(entries, exclude_tag):
    valid_entries = [i for i in entries if exclude_tag not in i.tags]

    for entry in valid_entries:
        entry.children = exclude_entries(entry.children, exclude_tag)

    return valid_entries
