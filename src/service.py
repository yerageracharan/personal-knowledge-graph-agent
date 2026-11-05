"""Application service shared by Streamlit and MCP interfaces."""
from src.extraction import extract_entities, extract_relationships
from src.ingestion import extract_text
from src.llm import LLMClient, LLMConfig
from src.search import retrieve
from src.store import KnowledgeStore

class KnowledgeService:
    def __init__(self, db_path="data/knowledge.db", llm_config=None):
        self.store=KnowledgeStore(db_path)
        self.llm=LLMClient(llm_config or LLMConfig.from_env())
    def ingest(self, filename, content):
        text=extract_text(filename,content)
        if not text: raise ValueError("No text could be extracted from this document.")
        return self.ingest_text(filename,text)
    def ingest_text(self, filename, text):
        if not text.strip(): raise ValueError("Document text is empty.")
        entities=extract_entities(text); relationships=extract_relationships(text,entities); mode="heuristic"
        if self.llm.enabled:
            try:
                graph=self.llm.extract_graph(text)
                candidates=graph.get("entities",[])
                valid={str(x.get("name","")).strip() for x in candidates if str(x.get("name","")).strip()}
                entities=list(valid)[:80]; relationships=[]
                for edge in graph.get("relationships",[])[:120]:
                    source,target=str(edge.get("source","")).strip(),str(edge.get("target","")).strip()
                    evidence=str(edge.get("evidence","")).strip()
                    if source in valid and target in valid and source!=target and evidence and evidence in text:
                        relationships.append({"source":source,"target":target,"label":str(edge.get("label","RELATED_TO"))[:40],"evidence":evidence[:500],"count":1})
                mode="llm"
            except Exception as exc: mode=f"heuristic_fallback: {type(exc).__name__}: {exc}"
        added=self.store.add_document(filename,text,entities,relationships)
        return {"added":added,"filename":filename,"characters":len(text),"entities":len(entities),"relationships":len(relationships),"extraction":mode}
    def search(self, query, limit=6): return retrieve(query,self.store.get_document_texts(),limit=limit)
    def ask(self, question):
        evidence=self.search(question,8)
        if not evidence: return {"answer":"I couldn't find relevant evidence in the indexed documents.","evidence":[]}
        if self.llm.enabled:
            try: return {"answer":self.llm.answer(question,evidence),"evidence":evidence,"mode":"llm"}
            except Exception as exc: mode=f"retrieval_fallback: {exc}"
        else: mode="retrieval_only"
        excerpts="\n\n".join(f"[{i+1}] {x['source']}: {x['text']}" for i,x in enumerate(evidence))
        return {"answer":"No usable LLM response. Here are the best matching source excerpts:\n\n"+excerpts,"evidence":evidence,"mode":mode}
    def graph(self):
        return {"entities":[dict(x) for x in self.store.all_entities()],"relationships":[dict(x) for x in self.store.all_relationships()],"stats":self.store.stats()}
