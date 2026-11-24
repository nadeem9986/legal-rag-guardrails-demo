"""
Free local stand-ins for the paid parts, so both versions can run with no API keys.

  OpenAI embeddings (ada-002, 1536-dim)  ->  sentence-transformers all-MiniLM-L6-v2 (384-dim)
  Pinecone index                          ->  FAISS in memory (score = distance, LOWER is closer)
  gpt-3.5-turbo                           ->  Qwen2.5-0.5B-Instruct on CPU (much weaker than GPT-3.5)

Only the engine's constructor and index methods are swapped. The query() logic in each app
folder (before/ or after/) is that folder's own code. The index is built from data/docs.json
(a one-time scrape of 3 legaldesk.com pages) using each folder's own DocumentProcessor.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_models = {}


def _get_models():
    if not _models:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from langchain_community.embeddings import HuggingFaceEmbeddings
        name = os.getenv("DEMO_LLM", "Qwen/Qwen2.5-0.5B-Instruct")
        _models["emb"] = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        _models["tok"] = AutoTokenizer.from_pretrained(name)
        _models["lm"] = AutoModelForCausalLM.from_pretrained(name, dtype=torch.bfloat16)
    return _models


class _Msg:
    def __init__(self, content):
        self.content = content


class LocalLLM:
    """Looks like the small part of ChatOpenAI that the engine uses: bind(temperature).invoke(prompt)."""

    def __init__(self, temperature=0.3):
        self.t = temperature

    def bind(self, temperature=0.3):
        return LocalLLM(temperature)

    def invoke(self, prompt):
        m = _get_models()
        tok, lm = m["tok"], m["lm"]
        if isinstance(prompt, str):
            msgs = [{"role": "user", "content": prompt}]
        else:  # list of langchain messages
            role = {"system": "system", "human": "user", "ai": "assistant"}
            msgs = [{"role": role.get(x.type, "user"), "content": x.content} for x in prompt]
        ids = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt", return_dict=True)
        greedy = os.getenv("DEMO_GREEDY", "0") == "1"
        kw = dict(max_new_tokens=int(os.getenv("DEMO_MAX_NEW_TOKENS", "220")))
        if greedy or self.t <= 0:
            kw.update(do_sample=False)
        else:
            kw.update(do_sample=True, temperature=max(self.t, 0.01))
        out = lm.generate(**ids, pad_token_id=tok.eos_token_id, **kw)
        text = tok.decode(out[0][ids["input_ids"].shape[1]:], skip_special_tokens=True)
        return _Msg(text)


def load_docs():
    docs = json.load(open(os.path.join(HERE, "data", "docs.json"), encoding="utf-8"))
    extra = os.getenv("DEMO_EXTRA_DOCS")  # a json file of extra documents (used by the injection test)
    if extra:
        docs = docs + json.load(open(extra, encoding="utf-8"))
    return docs


def install(app_dir):
    """Point at before/ or after/, and swap the engine's OpenAI/Pinecone parts for local ones."""
    app_dir = os.path.abspath(app_dir)
    sys.path.insert(0, app_dir)
    os.chdir(app_dir)
    os.environ.update(OPENAI_API_KEY="local-demo", PINECONE_API_KEY="local-demo", PINECONE_ENVIRONMENT="local-demo")
    from src.models.rag_engine import PineconeRAGEngine
    from src.models.document_processor import DocumentProcessor
    from langchain_community.vectorstores import FAISS

    state = {}

    def _init(self, *a, **k):
        self.vector_store = None
        self.llm = LocalLLM()
        self.index_name = "local-faiss"
        self.score_kind = "distance"   # FAISS: lower is closer. Pinecone cosine would be 'similarity'.

    def _load(self):
        if "vs" not in state:
            chunks = DocumentProcessor().process_documents(load_docs())
            state["chunks"] = chunks
            state["vs"] = FAISS.from_texts([c["text"] for c in chunks], _get_models()["emb"],
                                           metadatas=[c["metadata"] for c in chunks])
        self.vector_store = state["vs"]
        return True

    PineconeRAGEngine.__init__ = _init
    PineconeRAGEngine.load_existing_index = _load
    PineconeRAGEngine.get_index_stats = lambda self: {"total_vector_count": len(state.get("chunks", []))}
    return PineconeRAGEngine, state
