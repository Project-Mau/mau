from mau.test_helpers import generate_context
from mau.text_buffer import Context, adjust_context, adjust_context_dict


def test_context():
    ctx = Context(
        start_line=1, start_column=7, end_line=5, end_column=10, source="main"
    )

    assert ctx.asdict() == {
        "start_line": 1,
        "start_column": 7,
        "end_line": 5,
        "end_column": 10,
        "source": "main",
    }

    assert str(ctx) == "main:1,7-5,10"


def test_context_empty():
    ctx = Context.empty()

    assert ctx.asdict() == {
        "start_line": 0,
        "start_column": 0,
        "end_line": 0,
        "end_column": 0,
        "source": None,
    }


def test_context_merge():
    ctx1 = generate_context(1, 7, 5, 10)
    ctx2 = generate_context(100, 107, 105, 110)

    context = Context.merge_contexts(ctx1, ctx2)

    assert context == generate_context(1, 7, 105, 110)


def test_context_merge_overlapping():
    ctx1 = generate_context(1, 7, 5, 10)
    ctx2 = generate_context(4, 9, 105, 110)

    context = Context.merge_contexts(ctx1, ctx2)

    assert context == generate_context(1, 7, 105, 110)


def test_context_merge_included():
    ctx1 = generate_context(1, 2, 3, 4)
    ctx2 = generate_context(0, 0, 5, 6)

    context = Context.merge_contexts(ctx1, ctx2)

    assert context == ctx2


def test_context_clone():
    ctx1 = generate_context(1, 7, 5, 10)
    ctx2 = ctx1.clone()

    assert ctx1 == ctx2


def test_context_clones_are_independent():
    ctx1 = generate_context(1, 7, 5, 10)
    ctx2 = ctx1.clone()

    ctx2.start_line = 200

    assert ctx1.start_line == 1


def test_context_position_attributes():
    ctx = Context(
        start_line=1, start_column=7, end_line=5, end_column=10, source="main"
    )

    assert ctx.start_position == (1, 7)
    assert ctx.end_position == (5, 10)


def test_context_move_to():
    ctx = Context(
        start_line=0, start_column=0, end_line=5, end_column=10, source="main"
    )

    ctx = ctx.move_to(3, 5)

    assert ctx.asdict() == {
        "start_line": 3,
        "start_column": 5,
        "end_line": 8,
        "end_column": 15,
        "source": "main",
    }


def test_adjust_context():
    context = generate_context(1, 2, 3, 4)

    assert adjust_context(context) == generate_context(2, 2, 4, 4)


def test_adjust_context_dict():
    context_dict = generate_context(1, 2, 3, 4).asdict()

    assert adjust_context_dict(context_dict) == generate_context(2, 2, 4, 4)
