import hashlib


def footnote_anchor(content):
    return hashlib.md5(str(content).encode("utf-8")).hexdigest()[:8]


def create_footnotes(footnote_mentions, footnote_data):
    footnotes = []

    for num, footnote in enumerate(footnote_mentions.values(), start=1):
        footnote.number = num

    for key, footnote in footnote_mentions.items():
        data = footnote_data[key]
        footnote.content = data["content"]
        anchor = footnote_anchor(footnote.content)

        footnote.reference_anchor = f"ref-footnote-{footnote.number}-{anchor}"
        footnote.content_anchor = f"cnt-footnote-{footnote.number}-{anchor}"

        footnotes.append(footnote.to_entry())

    return footnotes
