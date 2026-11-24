"""Pick the FAISS distance bar from CALIBRATION questions (different from the test questions)."""
import json, os, sys
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here)
import local_backend
Engine, state = local_backend.install(os.path.join(here, "after"))
e = Engine(); e.load_existing_index()
IN = ["What clauses should a lease agreement include?", "Is a digital signature valid on a tenancy contract?",
      "Who can act as my agent under a power of attorney?", "What is a confidentiality agreement used for?",
      "How long does it take to get my agreement?", "What does the premium package include?"]
OUT = ["How do I file for divorce?", "What is the capital of France?", "How do I register a trademark?",
       "What is the punishment for theft?", "How do I apply for a passport?", "Explain quantum computing."]
res = {}
for name, qs in (("in_scope", IN), ("out_of_scope", OUT)):
    res[name] = []
    for q in qs:
        top = e.vector_store.similarity_search_with_score(q, k=3)
        res[name].append({"q": q, "top3_distance": [round(float(s), 3) for _, s in top]})
        print(name, round(float(top[0][1]), 3), round(float(top[-1][1]), 3), q)
json.dump(res, open(os.path.join(here, "results", "calibration.json"), "w"), indent=1)
