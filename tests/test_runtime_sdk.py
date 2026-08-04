from __future__ import annotations

from horo_agent.runtime import EmbeddedRuntime, RunEvent, RunRequest


def test_runtime_types_keep_webui_compatible_aliases():
    request = RunRequest(session_id="s1", message="hello", source="webui")

    assert request.session_id == "s1"
    assert request.message == "hello"
    assert request.attachments == []
    assert request.toolsets == []


def test_run_event_legacy_dict_shape_is_webui_friendly():
    event = RunEvent(
        "message.delta",
        {"text": "hi"},
        run_id="r1",
        event_id="r1:1",
        seq=1,
    )

    assert event.to_legacy_dict() == {
        "type": "message.delta",
        "data": {"text": "hi"},
        "run_id": "r1",
        "event_id": "r1:1",
        "seq": 1,
    }


def test_embedded_runtime_run_uses_callback_first_hot_path():
    events = []

    class FakeAgent:
        def run_conversation(self, **kwargs):
            kwargs["stream_callback"]("hel")
            kwargs["stream_callback"]("lo")
            return {"final_response": "hello", "messages": []}

    runtime = EmbeddedRuntime(agent_factory=lambda request: FakeAgent())
    result = runtime.run(
        RunRequest(
            session_id="s1",
            message="hello",
            metadata={"run_id": "r1", "conversation_history": [{"role": "user", "content": "prior"}]},
        ),
        event_sink=events.append,
    )

    assert result["final_response"] == "hello"
    assert [event.type for event in events] == [
        "run.started",
        "message.delta",
        "message.delta",
        "run.completed",
    ]
    assert [event.payload.get("text") for event in events if event.type == "message.delta"] == ["hel", "lo"]
    assert runtime.status("r1").status == "completed"
