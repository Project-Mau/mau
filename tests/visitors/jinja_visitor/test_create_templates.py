# from mau.visitors.jinja_visitor import _create_templates


# def test_create_templates_basic_templates():
#     result = _create_templates("ntype", "ext")

#     assert result == ["ntype.ext"]


# def test_create_templates_empty_extension():
#     result = _create_templates("ntype")

#     assert result == ["ntype"]


# def test_create_templates_type_and_subtype():
#     result = _create_templates("ntype", extension="ext", node_subtype="nstype")

#     assert result == [
#         "ntype.nstype.ext",
#         "ntype.ext",
#     ]


# def test_create_templates_prefixes():
#     result = _create_templates(
#         "ntype",
#         extension="ext",
#         node_subtype="nstype",
#         parent_prefix="pprefix",
#         global_prefixes=["gp1", "gp2"],
#     )

#     assert result == [
#         "gp1.pprefix.ntype.nstype.ext",
#         "gp1.pprefix.ntype.ext",
#         "gp1.ntype.nstype.ext",
#         "gp1.ntype.ext",
#         "gp2.pprefix.ntype.nstype.ext",
#         "gp2.pprefix.ntype.ext",
#         "gp2.ntype.nstype.ext",
#         "gp2.ntype.ext",
#         "pprefix.ntype.nstype.ext",
#         "pprefix.ntype.ext",
#         "ntype.nstype.ext",
#         "ntype.ext",
#     ]


# def test_create_templates_tags():
#     result = _create_templates(
#         "ntype",
#         extension="ext",
#         node_subtype="nstype",
#         node_tags=["tag1", "tag2"],
#     )

#     assert result == [
#         "ntype.nstype#tag1.ext",
#         "ntype.nstype#tag2.ext",
#         "ntype.nstype.ext",
#         "ntype#tag1.ext",
#         "ntype#tag2.ext",
#         "ntype.ext",
#     ]
