"""Combine scraped CSVs, drop org/company channels, rank individual coaches as ICP."""
import csv, glob, re
from pathlib import Path

ORG_WORDS = re.compile(r"\b(school|academy|alliance|feed|labs?|inc|llc|university|"
                       r"college|institute|igotanoffer|glencoco|better|hq|team|"
                       r"official|tv|media|systems?|interview$|careers?$)\b", re.I)

def is_individual(name: str) -> bool:
    toks = name.split()
    if ORG_WORDS.search(name):
        return False
    return 2 <= len(toks) <= 3  # "First Last" / "First M. Last"

rows, seen = [], set()
for f in glob.glob("scraped/*.csv"):
    if "snapshot" in f:
        continue
    for r in csv.DictReader(open(f)):
        url = r.get("channel_url", "")
        if not url or url in seen:
            continue
        seen.add(url)
        rows.append(r)

for r in rows:
    r["icp"] = "individual-coach" if is_individual(r["channel"]) else "org/skip"
    r["followers_int"] = int(r["followers"]) if str(r.get("followers","")).isdigit() else 0

rows.sort(key=lambda r: (r["icp"] != "individual-coach", -r["followers_int"]))
out = Path("outreach-shortlist.csv")
with out.open("w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["channel","followers","sub_vertical","icp","channel_url","needs"])
    for r in rows:
        w.writerow([r["channel"], r["followers"], r["sub_vertical"], r["icp"],
                    r["channel_url"], "resolve website + enrich email"])
ind = sum(1 for r in rows if r["icp"]=="individual-coach")
print(f"Total unique: {len(rows)} | individual-coach ICP: {ind} | org/skip: {len(rows)-ind}")
print("Wrote outreach-shortlist.csv (individuals ranked first)\n")
print("Top 15 ICP-fit prospects:")
for r in [x for x in rows if x["icp"]=="individual-coach"][:15]:
    print(f"  {r['followers_int']:>7,}  {r['sub_vertical']:<18} {r['channel']}")
