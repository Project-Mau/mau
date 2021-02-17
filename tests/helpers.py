import textwrap


def dedent(text):
    return textwrap.dedent(text).strip()


def remove_indentation(text):
    # This removes indentation and newlines completely
    return "".join([i.strip() for i in textwrap.dedent(text).split("\n")])


def listasdict(nodes):
    return [i.asdict() for i in nodes]


def init_parser_factory(parser_class):
    def _init_parser(text, *args, **kwargs):
        p = parser_class(*args, **kwargs)

        p.load(text)

        return p

    return _init_parser


def parser_test_factory(parser_class):

    init_parser = init_parser_factory(parser_class)

    def _test(source, expected):
        p = init_parser(textwrap.dedent(source))
        p.parse()

        assert listasdict(p.nodes) == expected

        return p

    return _test


def init_ast_factory(parser_class):
    def _init_ast(text, *args, **kwargs):
        init_parser = init_parser_factory(parser_class)

        p = init_parser(text, *args, **kwargs)
        p.parse()

        return listasdict(p.nodes)

    return _init_ast


def visitlist_factory(visitor_class):
    def _visitlist(nodes, *args, **kwargs):
        v = visitor_class(*args, **kwargs)

        return [v.visit(node) for node in nodes]

    return _visitlist


def ast_test_factory(parser_class, visitor_class):
    init_ast = init_ast_factory(parser_class)
    visitlist = visitlist_factory(visitor_class)

    def _test(source, expected):
        ast = init_ast(source)
        result = visitlist(ast)

        assert result == expected

    return _test
