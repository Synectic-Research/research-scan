"""Phase-1.2C step 1 — inventory exactly what `ranked.json` records per candidate, and what
the joinable 1.1/1.2A artefacts add. Tie-break keys may use ONLY what this script finds.

Nothing is invented and nothing numeric is derived: this reports presence, cardinality and
observed value sets, per run, so a missing or partial field is visible rather than assumed.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict

import common12c as C


def main() -> None:
    per_run = {}
    field_presence: Counter = Counter()
    criteria_ids: dict[str, Counter] = defaultdict(Counter)
    criteria_complete = Counter()
    value_sets: dict[str, Counter] = defaultdict(Counter)
    total_rows = 0

    for run in C.runs():
        ranked = run.load("ranked.json")
        ids_here: set[str] = set()
        rows_missing_criteria = 0
        for entry in ranked:
            total_rows += 1
            for k, v in entry.items():
                field_presence[k] += 1
                if k in ("overall", "evidence_level", "relation"):
                    value_sets[k][v] += 1
                if k == "flags":
                    for fk, fv in (v or {}).items():
                        value_sets[f"flags.{fk}"][fv] += 1
            crit = entry.get("criteria") or {}
            if not crit:
                rows_missing_criteria += 1
            ids_here |= set(crit)
            for cid_key, grade in crit.items():
                criteria_ids[run.topic][cid_key] += 1
                value_sets["criteria.grade"][grade] += 1
        # every row carries the same criterion ids?
        widths = Counter(len(e.get("criteria") or {}) for e in ranked)
        criteria_complete[f"{run.topic}:{sorted(widths)}"] += 1
        per_run[run.key] = {
            "rows": len(ranked),
            "criterion_ids": sorted(ids_here),
            "criteria_widths": {str(k): v for k, v in sorted(widths.items())},
            "rows_missing_criteria": rows_missing_criteria,
        }

    feats = {t: C.shortlist_features(t) for t in C.SLUGS}
    joinable = {}
    for topic, fmap in feats.items():
        cover = Counter()
        for row in fmap.values():
            for k, v in row.items():
                if v is not None:
                    cover[k] += 1
        joinable[topic] = {"rows": len(fmap), "non_null": dict(cover),
                           "t1_rank_unique": len(set(C.t1_rank(topic).values())) == len(fmap)}

    out = {
        "runs": len(per_run),
        "ranked_rows_total": total_rows,
        "ranked_field_presence": dict(field_presence.most_common()),
        "ranked_field_presence_pct": {k: round(100 * v / total_rows, 1)
                                      for k, v in field_presence.most_common()},
        "criterion_ids_seen": {t: sorted(c) for t, c in criteria_ids.items()},
        "criteria_width_by_run": dict(criteria_complete),
        "observed_values": {k: {str(a): b for a, b in sorted(v.items(), key=lambda x: str(x[0]))}
                            for k, v in value_sets.items()},
        "per_run": per_run,
        "joinable_shortlist_features": joinable,
    }
    (C.HERE / "results" / "inventory.json").write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps({k: v for k, v in out.items() if k != "per_run"}, indent=1, default=str))


if __name__ == "__main__":
    main()
