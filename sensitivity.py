"""How sensitive is the distance bar? Retrieval only (no LLM). Also records how scores are computed.
   Uses the CLEANED index (A1 on). 'false refusal' = an in-scope question whose best chunk is farther than the bar.
   'false pass' = an out-of-scope question whose best chunk is within the bar."""
import json, os, sys
import numpy as np
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here)
import local_backend
Engine, state = local_backend.install(os.path.join(here, "after"))
e = Engine(); e.load_existing_index()
emb = local_backend._get_models()["emb"]
v = np.array(emb.embed_query("What is a rental agreement?"))
info = {"embedding_dim": int(v.shape[0]), "embedding_L2_norm": round(float(np.linalg.norm(v)), 4),
        "faiss_index": type(e.vector_store.index).__name__, "score_returned": "FAISS distance (lower = closer)", "k": 3}
cal = json.load(open(os.path.join(here, "results", "calibration.json")))
IN_T = ["What is a rental agreement?", "What documents are required for a rental agreement?", "Is e-stamp paper legally recognised for rental agreements?",
        "What does a general power of attorney do?", "What is a non-disclosure agreement for?"]
OUT_T = ["What documents do I need for a name change?", "What is the notice period to evict a tenant in Karnataka?", "What is the weather in Bengaluru today?"]
def top1(q): return round(float(e.vector_store.similarity_search_with_score(q, k=1)[0][1]), 3)
sets = {"calibration_in": [c["top3_distance"][0] for c in cal["in_scope"]], "calibration_out": [c["top3_distance"][0] for c in cal["out_of_scope"]],
        "test_in": [top1(q) for q in IN_T], "test_out": [top1(q) for q in OUT_T]}
rows = []
for bar in (0.9, 1.0, 1.1, 1.2, 1.3, 1.4):
    rows.append({"bar": bar, **{f"false_refusals_{k}": sum(d > bar for d in sets[k]) for k in ("calibration_in", "test_in")},
                 **{f"false_passes_{k}": sum(d <= bar for d in sets[k]) for k in ("calibration_out", "test_out")}})
json.dump({"scoring": info, "top1_distances": sets, "by_bar": rows}, open(os.path.join(here, "results", "sensitivity.json"), "w"), indent=1)
print(json.dumps(info)); print(sets)
for r in rows: print(r)
