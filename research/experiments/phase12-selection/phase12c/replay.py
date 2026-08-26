"""Phase-1.2C — replay the shipped selection over every recorded rerank run, varying ONLY the
ordering key.

The slot rules are not re-implemented. `research_scan.select.select` is called unchanged, with
`select.order_key` swapped for the ladder under test — which is exactly "the slot rules replayed
unchanged, only the ordering key varies", because `select`, `presentation_order` and
`_lowest_displaceable` all reach the key through that one module-level name.

$0. No model call. Nothing outside `research/experiments/` is written.
"""
from __future__ import annotations

import contextlib
import json
import logging
from dataclasses import dataclass

import common12c as C
import ladders
from research_scan import select
from research_scan.schema import CandidatesFile, Ranked

logging.getLogger("research_scan.select").setLevel(logging.ERROR)


@contextlib.contextmanager
def ordering_key(fn):
    """Swap the one module-level name every selection rule reaches the ordering through."""
    original = select.order_key
    select.order_key = fn
    try:
        yield
    finally:
        select.order_key = original


@dataclass
class Replay:
    run: C.Run
    key_name: str
    emitted: list[str]
    reasons: list[str]
    alternates: list[str]
    merit_order: list[str]           # in-window rows, best first, under this key
    in_window_emitted: list[str]
    boundary_cid: str | None         # weakest in-window row actually emitted


def pairs_for(run: C.Run):
    """(candidate, entry) in `ranked.json` order — exactly what `cli.emit` builds (cli.py:762)."""
    ranked = Ranked.model_validate(run.load("ranked.json"))
    candidates = CandidatesFile.model_validate(run.load("candidates.json"))
    by_cid = {c.cid: c for c in candidates.candidates}
    return [(by_cid[e.cid], e) for e in ranked.root]


def replay(run: C.Run, key_name: str, key_fn, top: int, foundational: int) -> Replay:
    pairs = pairs_for(run)
    with ordering_key(key_fn):
        result = select.select(pairs, top=top, foundational=foundational,
                               contradicting=select.CONTRADICTING_SLOTS)
        ordered = sorted(pairs, key=key_fn, reverse=True)
    in_window = [e.cid for c, e in ordered if not c.outside_window]
    emitted = [p.cid for p in result.packets]
    reasons = [p.selection_reason.value for p in result.packets]
    outside = {c.cid for c, _ in pairs if c.outside_window}
    inw_emitted = [cid for cid in emitted if cid not in outside]
    boundary = min(inw_emitted, key=lambda cid: in_window.index(cid)) if inw_emitted else None
    if inw_emitted:
        boundary = max(inw_emitted, key=lambda cid: in_window.index(cid))
    return Replay(run, key_name, emitted, reasons, [p.cid for p in result.alternates],
                  in_window, inw_emitted, boundary)


def resolve_depth(key_fn, tiers: tuple[str, ...], a, b) -> tuple[int, str]:
    """First tier index at which two rows differ. len(tiers)-1 means the terminal tie-break."""
    ka, kb = key_fn(a), key_fn(b)
    for i, (x, y) in enumerate(zip(ka, kb, strict=False)):
        if x != y:
            return i, tiers[i]
    return len(ka) - 1, tiers[-1]


def main() -> None:
    out = {}
    for run in C.runs():
        feats = C.shortlist_features(run.topic)
        ranks = C.t1_rank(run.topic)
        keys = ladders.make_keys(feats, ranks)
        manifest = run.load("manifest.json")
        top = manifest["defaults"]["top"]
        foundational = manifest["defaults"]["foundational"]
        recorded = [p["cid"] for p in run.load("evidence.json")["packets"]]
        row = {"topic": run.topic, "arm": run.arm, "ordering": run.ordering, "rep": run.rep,
               "top": top, "foundational": foundational, "recorded_emitted": recorded,
               "keys": {}}
        for name, fn in keys.items():
            r = replay(run, name, fn, top, foundational)
            row["keys"][name] = {
                "emitted": r.emitted, "reasons": r.reasons, "alternates": r.alternates,
                "in_window_merit": r.merit_order, "in_window_emitted": r.in_window_emitted,
                "boundary_cid": r.boundary_cid,
                "reproduces_recorded": r.emitted == recorded,
                "same_set_as_recorded": set(r.emitted) == set(recorded),
            }
        out[run.key] = row
    (C.HERE / "results" / "replays.json").write_text(json.dumps(out, indent=1))

    k0_exact = sum(1 for r in out.values() if r["keys"]["K0"]["reproduces_recorded"])
    k0_set = sum(1 for r in out.values() if r["keys"]["K0"]["same_set_as_recorded"])
    print(f"K0 validation: {k0_exact}/{len(out)} runs reproduce the recorded top-10 "
          f"cid-for-cid in order; {k0_set}/{len(out)} as a set")
    for k, r in out.items():
        if not r["keys"]["K0"]["reproduces_recorded"]:
            print("  MISMATCH", k)
            print("   recorded:", r["recorded_emitted"])
            print("   replayed:", r["keys"]["K0"]["emitted"])


if __name__ == "__main__":
    main()
