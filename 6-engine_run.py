"""Run the real query() of one version for a list of questions, print JSON.
   python engine_run.py before|after questions.json out.json   (flags come from G_* env vars)"""
import json, os, sys, time
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
import local_backend
which, qfile, out = sys.argv[1:4]
qfile, out = os.path.abspath(qfile), os.path.abspath(out)
if os.getenv('DEMO_EXTRA_DOCS'): os.environ['DEMO_EXTRA_DOCS'] = os.path.abspath(os.environ['DEMO_EXTRA_DOCS'])
Engine, state = local_backend.install(os.path.join(here, which))
eng = Engine(); eng.load_existing_index()
res = []
for q in json.load(open(qfile)):
    t = time.time()
    r = eng.query(q["q"], temperature=0.3)
    # what retrieval returned for the model, independent of what the version then did with it
    raw = [(d.metadata.get("title", "")[:40], d.metadata.get("chunk_index"), round(float(s), 3), d.page_content[:90])
           for d, s in eng.vector_store.similarity_search_with_score(q["q"], k=3)]
    res.append({"id": q["id"], "q": q["q"], "answer": r["answer"], "sources": [(s["title"][:45], s["url"]) for s in r["sources"]],
                "trace": r.get("trace"), "raw_top3": raw, "seconds": round(time.time() - t, 1)})
    print(q["id"], res[-1]["seconds"], "s", flush=True)
json.dump({"which": which, "flags": {k: v for k, v in os.environ.items() if k.startswith("G_") or k.startswith("DEMO_")},
           "chunks": len(state.get("chunks", [])), "results": res}, open(out, "w"), indent=1, ensure_ascii=False)
