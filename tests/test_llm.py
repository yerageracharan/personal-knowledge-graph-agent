import pytest
from src.llm import LLMClient, LLMConfig, _json_from_text

def test_none_provider_is_disabled():
    assert not LLMClient(LLMConfig(provider="none")).enabled

def test_ollama_enabled_without_api_key():
    assert LLMClient(LLMConfig(provider="ollama",model="llama3.1")).enabled

def test_parse_json_object():
    assert _json_from_text('{"entities": []}') == {"entities":[]}

def test_reject_json_array():
    with pytest.raises(ValueError): _json_from_text('[1,2]')
