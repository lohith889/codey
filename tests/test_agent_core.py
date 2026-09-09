import pytest
from Agent.agent_core import _group_into_turns, prune_messages, TOOL_FUNCTIONS


def test_group_into_turns():
    messages = [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hi"},
        {"role": "user", "content": "task 1"},
        {"role": "assistant", "content": "calling tool", "tool_calls": ["call1"]},
        {"role": "tool", "content": "result 1"},
    ]
    turns = _group_into_turns(messages)
    assert len(turns) == 3
    assert turns[0] == [{"role": "user", "content": "hello"}]
    assert turns[1] == [{"role": "assistant", "content": "hi"}, {"role": "user", "content": "task 1"}]
    assert len(turns[2]) == 2


def test_prune_messages_preserves_anchors():
    anchor1 = {"role": "system", "content": "system prompt"}
    anchor2 = {"role": "user", "content": "original user task"}

    history = []
    for i in range(15):
        history.append({"role": "assistant", "content": f"step {i}"})
        history.append({"role": "user", "content": f"user response {i}"})

    messages = [anchor1, anchor2] + history
    assert len(messages) == 32

    pruned = prune_messages(messages, max_messages=10)
    assert pruned[0] == anchor1
    assert pruned[1] == anchor2
    assert len(pruned) <= 10


def test_prune_messages_no_op_when_under_limit():
    messages = [
        {"role": "system", "content": "sys"},
        {"role": "user", "content": "task"},
        {"role": "assistant", "content": "reply"},
    ]
    pruned = prune_messages(messages, max_messages=20)
    assert pruned == messages


def test_tool_functions_dispatch(tmp_path, monkeypatch):
    monkeypatch.setattr("Agent.tools.ROOT_PATH", tmp_path)

    write_fn = TOOL_FUNCTIONS["write_file"]
    res = write_fn({"path": "sample.txt", "content": "hello tool"})
    assert "Successfully wrote" in res

    read_fn = TOOL_FUNCTIONS["read_file"]
    assert read_fn({"path": "sample.txt"}) == "hello tool"
