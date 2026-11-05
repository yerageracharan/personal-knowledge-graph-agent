"""Provider-agnostic LLM client: OpenAI, Anthropic, Ollama and compatible APIs."""
from __future__ import annotations
import json, os, re
from dataclasses import dataclass
from typing import Any

@dataclass
class LLMConfig:
    provider: str = "none"
    model: str = ""
    api_key: str = ""
    base_url: str = ""
    temperature: float = 0.1
    @classmethod
    def from_env(cls):
        return cls(os.getenv("LLM_PROVIDER","none"),os.getenv("LLM_MODEL",""),
                   os.getenv("LLM_API_KEY",""),os.getenv("LLM_BASE_URL",""))

def _json_from_text(text: str) -> dict[str, Any]:
    text = re.sub(r"^\x60{3}(?:json)?\s*|\s*\x60{3}$", "", text.strip(), flags=re.I)
    try: value = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.S)
        if not match: raise ValueError("The model did not return valid JSON.")
        value = json.loads(match.group(0))
    if not isinstance(value, dict): raise ValueError("Expected a JSON object from the model.")
    return value

class LLMClient:
    def __init__(self, config: LLMConfig): self.config = config
    @property
    def enabled(self): return self.config.provider.lower() not in {"","none","heuristic"}
    def _openai_client(self):
        from openai import OpenAI
        provider, base, key = self.config.provider.lower(), self.config.base_url.strip() or None, self.config.api_key.strip()
        if provider == "ollama":
            base = base or "http://localhost:11434/v1"
            key = key or "ollama"
        if not key and provider != "ollama": raise ValueError("An API key is required for this provider.")
        return OpenAI(api_key=key or "not-needed", base_url=base)
    def _chat(self, system: str, prompt: str) -> str:
        provider = self.config.provider.lower()
        if not self.config.model: raise ValueError("Select a model name before making an LLM request.")
        if provider == "anthropic":
            if not self.config.api_key: raise ValueError("An Anthropic API key is required.")
            import anthropic
            client = anthropic.Anthropic(api_key=self.config.api_key)
            result = client.messages.create(model=self.config.model,max_tokens=2500,temperature=self.config.temperature,
                system=system,messages=[{"role":"user","content":prompt}])
            return "\n".join(x.text for x in result.content if getattr(x,"type","")=="text")
        result = self._openai_client().chat.completions.create(model=self.config.model,temperature=self.config.temperature,
            messages=[{"role":"system","content":system},{"role":"user","content":prompt}])
        return result.choices[0].message.content or ""
    def extract_graph(self, text: str) -> dict[str, Any]:
        raw = self._chat("Extract a conservative knowledge graph. Return only valid JSON. Never invent facts.",
          """Extract entities and evidence-backed relationships from source text.
Return JSON: {"entities":[{"name":"...","type":"person|organization|technology|concept|place|event|other","description":"..."}],
"relationships":[{"source":"entity name","target":"entity name","label":"SHORT_VERB_LABEL","evidence":"exact sentence copied from source"}]}
Only explicit entities. Relationships must have exact supporting sentences. Do not infer causality. Max 40 entities and 60 relationships.
SOURCE TEXT:
""" + text[:18000])
        return _json_from_text(raw)
    def answer(self, question: str, evidence: list[dict]) -> str:
        context="\n\n".join(f"[{i+1}] Source: {x['source']}\nEvidence: {x['text']}" for i,x in enumerate(evidence))
        return self._chat("Answer only from supplied evidence. If insufficient, say so. Cite factual claims with [1], [2]. Never fabricate citations.",
                          f"Question: {question}\n\nEvidence:\n{context}\n\nAnswer concisely with citations.")

def config_from_values(provider, model, api_key="", base_url=""):
    return LLMConfig(provider=provider,model=model,api_key=api_key,base_url=base_url)
