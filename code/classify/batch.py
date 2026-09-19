"""Print one batch of masked passages for in-conversation coding, and append codes to output/coding/codes_heads.csv.
usage: python3 code/classify/batch.py show <start> <n>
       python3 code/classify/batch.py save "<id>:<topic 0/1>:<pos -1/0/1 or .>:<retro 0/1>" ...
"""
import csv, json, os, sys
Q = json.load(open("output/coding/queue_heads.json"))
OUT = "output/coding/codes_heads.csv"
if sys.argv[1] == "show":
    s, n = int(sys.argv[2]), int(sys.argv[3])
    done = set()
    if os.path.exists(OUT):
        done = {r["id"] for r in csv.DictReader(open(OUT))}
    shown = 0
    for it in Q[s:]:
        if it["id"] in done: continue
        print(f"### {it['id']}\n{it['text']}\n")
        shown += 1
        if shown >= n: break
elif sys.argv[1] == "save":
    new = os.path.exists(OUT)
    with open(OUT, "a", newline="") as f:
        w = csv.writer(f)
        if not new: w.writerow(["id","topic","position","retrospective","coder","codebook"])
        for a in sys.argv[2:]:
            i, t, p, r = a.split(":")
            w.writerow([i, t, "" if p == "." else p, r, "model-in-conversation", "PAPv2-Y4-p2"])
    print("saved", len(sys.argv) - 2, "codes; total", sum(1 for _ in open(OUT)) - 1)
