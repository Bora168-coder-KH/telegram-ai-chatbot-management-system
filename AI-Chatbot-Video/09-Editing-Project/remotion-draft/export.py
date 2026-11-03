"""Export scene timing + subtitle cues (same rules as build.py) to src/data/scenes.json."""
import json, math, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "01-Scripts" / "_generator"))
import importlib.util
spec = importlib.util.spec_from_file_location("b", sys.path[0] + "/build.py")
src = Path(spec.origin).read_text(encoding="utf-8")
# run only the helper part of build.py (everything before the first document is written)
helpers = src[: src.index("# ---------------------------------------------------------------- 1–2 concept")]
ns = {"__file__": spec.origin}
sys.argv = ["x", "/tmp/unused"]
exec(compile(helpers, "build_helpers", "exec"), ns)
out = []
for s in ns["SCENES"]:
    def cues(key):
        parts = [ns["plain"](p) for p in s[key].split(" | ") if ns["plain"](p)] if s[key] else []
        start, end = s["start"] + 0.5, s["end"] - 0.4
        total = sum(len(p) for p in parts) or 1
        res, t0 = [], start
        for i, p in enumerate(parts):
            t1 = end if i == len(parts) - 1 else t0 + (end - start) * len(p) / total
            res.append({"from": round(t0 - s["start"], 3), "to": round(t1 - 0.05 - s["start"], 3), "text": p})
            t0 = t1
        return res
    out.append({"id": s["id"], "ch": s["ch"], "title": s["title"], "dur": s["dur"], "start": s["start"],
                "capKh": s["cap_kh"], "capEn": s["cap_en"], "subKh": cues("kh"), "subEn": cues("en")})
Path("src/data/scenes.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(out), "scenes", ns["TOTAL"], "s")
