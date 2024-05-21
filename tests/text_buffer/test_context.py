from mau.text_buffer.text_buffer import Context


def test_text_buffer_current_line():
    ctx = Context(line=1, column=7, source="main")

    assert ctx.asdict() == {
        "line": 1,
        "column": 7,
        "source": "main",
    }
    assert ctx == Context(line=1, column=7, source="main")
    assert ctx != (1, 7)
