"""Turn results/*.json into results/COMPARISON.md (side-by-side, per question)."""
import json, os
here = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(here, "results")
def load(n):
    p = os.path.join(R, n + ".json")
    return {r["id"]: r for r in json.load(open(p))["results"]} if os.path.exists(p) else {}
cols = [("BEFORE (original code)", "{s}_1_before"), ("AFTER: A only (retrieval quality)", "{s}_2_A_only"),
        ("AFTER: B only (security)", "{s}_3_B_only"), ("AFTER: A + B", "{s}_4_A_plus_B")]
out = ["# Before / after comparison", "",
       "Same questions, same 3 scraped pages, same free local models (MiniLM + FAISS + Qwen2.5-0.5B, greedy decoding).",
       "Answer quality here says nothing about GPT-3.5. What matters is what was retrieved, what each check did, and what reached the user.", ""]
for s in ("main", "poison"):
    data = [(t, load(f.format(s=s))) for t, f in cols]
    ids = list(data[0][1].keys()) or list(data[3][1].keys())
    for i in ids:
        q = next((d[i]["q"] for _, d in data if i in d), "")
        out += [f"## {i}", f"**Question:** {q}", ""]
        for title, d in data:
            if i not in d: out += [f"### {title}", "_not run_", ""]; continue
            r = d[i]
            out += [f"### {title}", f"- Retrieved (top 3 from the index, before any check): " + "; ".join(f"{t} #{c} dist {sc}" for t, c, sc, _ in r["raw_top3"]),
                    f"- Source links shown: {len(r['sources'])}" + ("" if not r["sources"] else " (" + ", ".join(sorted({u for _, u in r['sources']})) + ")")]
            if r.get("trace"):
                out += ["- Checks: " + " | ".join(f"{t['step']}: {t['detail']}" for t in r["trace"])]
            out += ["- Answer:", "", "  > " + r["answer"].replace("\n", "\n  > "), ""]
open(os.path.join(R, "COMPARISON.md"), "w", encoding="utf-8").write("\n".join(out))
print("wrote", os.path.join(R, "COMPARISON.md"))
