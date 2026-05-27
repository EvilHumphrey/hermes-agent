from __future__ import annotations

import importlib
import sys
import types
from types import SimpleNamespace

# Stub optional heavy imports so run_agent/agent imports stay lightweight.
sys.modules.setdefault("fire", types.SimpleNamespace(Fire=lambda *a, **k: None))
sys.modules.setdefault("firecrawl", types.SimpleNamespace(Firecrawl=object))
sys.modules.setdefault("fal_client", types.SimpleNamespace())


def test_import_installs_openai_parse_response_guard():
    from agent import codex_runtime

    parsing = importlib.import_module("openai.lib._parsing._responses")
    streaming = importlib.import_module("openai.lib.streaming.responses._responses")
    resources = importlib.import_module("openai.resources.responses.responses")

    assert getattr(parsing.parse_response, "_hermes_none_output_guard", False) is True
    assert streaming.parse_response is parsing.parse_response
    assert resources.parse_response is parsing.parse_response
    assert codex_runtime._patch_openai_parse_response_none_output_guard() is True


def test_guard_coerces_none_output_before_calling_original():
    from agent import codex_runtime

    seen = {}

    def original_parse_response(*args, **kwargs):
        seen["response"] = kwargs.get("response") if "response" in kwargs else args[2]
        return "ok"

    guarded = codex_runtime._build_openai_parse_response_none_output_guard(original_parse_response)
    response = SimpleNamespace(output=None, marker="preserved")

    result = guarded(text_format=None, input_tools=None, response=response)

    assert result == "ok"
    assert seen["response"].output == []
    assert seen["response"].marker == "preserved"
