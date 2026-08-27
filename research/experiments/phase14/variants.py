"""Phase-1.4 — the four rubric variants, built as patches over the shipped rerank rubric.

**Nothing under `skills/` is touched.** The shipped rubric at
`skills/research-scan/references/rerank-rubric.md` is read, never written; each variant is that
text with one factor's edits applied, and `C0` is the text itself, asserted byte-identical.
Adoption of any winner is a separate maintainer-ratified step that would edit the shipped file —
this module only produces the candidate texts a ratification would read.

FACTOR S — discrimination contract. Two edit sites, because the current rubric decides `overall` in
two places and patching one leaves a self-contradictory rubric:

  S1  `### overall — holistic 0-3`  ->  absolute anchors (0/1/2/3) + the `priority_rank` contract.
  S2  the `relation` paragraph's `**Any of the first four earns overall=3 …**` quota -> a sentence
      saying `relation` records how the paper stands to the brief and does not set `overall`. The
      paragraph's other content (do not score down non-actionable or neighbouring-setting work) is
      carried across unchanged; only the quota goes. Leaving the quota in would force `overall=3`
      on three of the five `relation` values, which is the saturation S exists to test.

  S does NOT touch the off-domain cap. That is C's site, and keeping them apart is what makes the
  2x2 a factorial rather than two names for one edit.

FACTOR C — content correction. Two edit sites, for the same reason:

  C1  a new `### What counts as decision-changing value` subsection in `## Scoring`, in language
      derived from the purpose taxonomy's own `research` definition (`plan-rubric.md:77` — "the
      answer changes what we believe, what we would test, or how we would measure it", and "the
      claim under test … in either direction").
  C2  one paragraph appended to the off-domain cap's **existing single exception**, extending it
      from "explicit method transfer" to the same five roles, at the identical bar: name what
      carries across or it does not carry.

  C2 is a pre-registration interpretation, made and recorded before any call was issued. The slice
  names Berk as the disagreement to fix; Berk is `relation: closely-related` — one of the four the
  quota already forces to 3 — and it is scored 2 in every recorded replicate. The only rubric clause
  that can produce that is the off-domain cap, which is an explicit override of `overall`
  ("whatever the other criteria scored and whatever `relation` you chose"). A content correction
  that cannot reach the cap cannot move Berk, and a factor that is inert by construction makes the
  cell it labels uninformative. So C is expressed where it has to be to operate — as an extension of
  an exception the rubric already has, in the factor's own language, with no new mechanism.

CONTAMINATION RULE, enforced by `check_contamination()`: no golden paper is named, quoted or
paraphrased in any variant text. The check is mechanical — golden titles, author surnames and
distinctive title tokens are searched for in every generated variant — and it runs in the test
suite and again at the top of every run.
"""

from __future__ import annotations

import difflib
import hashlib
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SHIPPED = REPO / "skills/research-scan/references/rerank-rubric.md"

CELLS = ("C0", "S", "C", "SC")

#: Which factors each cell turns on. C0 is the fresh control: both off.
FACTORS = {
    "C0": (False, False),
    "S": (True, False),
    "C": (False, True),
    "SC": (True, True),
}


# ------------------------------------------------------------- the patch texts

#: The eight patch texts live in `patches/` as markdown, not as Python string literals. Two
#: reasons: the report has to quote them verbatim and a reader should be able to open the exact
#: file the run used, and a rubric table row is longer than any Python line limit — keeping them
#: in source would mean either reflowing the text the model sees or suppressing the check.
#:
#: S1/S2 are FACTOR S's two edit sites, C1/C2 are FACTOR C's. `.find` is the anchor that must occur
#: exactly once in the shipped rubric; `.replace` is what takes its place; `C1.anchor` is the
#: heading `C1.insert` is placed above.
PATCHES = HERE / "patches"


def patch(name: str) -> str:
    return (PATCHES / f"{name}.md").read_text(encoding="utf-8")


S1_FIND = patch("S1.find")           # the `overall` section, as shipped
S1_REPLACE = patch("S1.replace")     # absolute anchors + the `priority_rank` contract
S2_FIND = patch("S2.find")           # the relation paragraph's "any of the first four earns 3"
S2_REPLACE = patch("S2.replace")     # relation records standing; it does not set `overall`
C1_ANCHOR = patch("C1.anchor")       # the `### relation` heading the new subsection sits above
C1_INSERT = patch("C1.insert")       # what counts as decision-changing value
C2_FIND = patch("C2.find")           # the off-domain cap's single existing exception
C2_REPLACE = patch("C2.replace")     # the same exception, extended to the five roles


# --------------------------------------------------------------------- assembly


def shipped_text() -> str:
    return SHIPPED.read_text(encoding="utf-8")


def _replace_once(text: str, find: str, replace: str, label: str) -> str:
    """Substitute exactly one occurrence, or refuse. A patch that silently no-ops would produce a
    variant identical to the control and a cell that measures nothing."""
    count = text.count(find)
    if count != 1:
        raise AssertionError(f"{label}: expected exactly 1 occurrence of the anchor, found {count}")
    return text.replace(find, replace, 1)


def _insert_before(text: str, anchor: str, insert: str, label: str) -> str:
    count = text.count(anchor)
    if count != 1:
        raise AssertionError(f"{label}: expected exactly 1 occurrence of the anchor, found {count}")
    return text.replace(anchor, insert + anchor, 1)


def apply_s(text: str) -> str:
    text = _replace_once(text, S1_FIND, S1_REPLACE, "S1 (overall anchors)")
    return _replace_once(text, S2_FIND, S2_REPLACE, "S2 (relation quota)")


def apply_c(text: str) -> str:
    text = _insert_before(text, C1_ANCHOR, C1_INSERT, "C1 (decision-changing value)")
    return _replace_once(text, C2_FIND, C2_REPLACE, "C2 (cap exception)")


def variant(cell: str) -> str:
    """The full rubric text for one cell. `C0` is the shipped file, byte for byte."""
    if cell not in FACTORS:
        raise KeyError(cell)
    s_on, c_on = FACTORS[cell]
    text = shipped_text()
    if s_on:
        text = apply_s(text)
    if c_on:
        text = apply_c(text)
    return text


def digest(cell: str) -> str:
    return hashlib.sha256(variant(cell).encode("utf-8")).hexdigest()[:16]


def uses_priority_rank(cell: str) -> bool:
    """Only the S factor puts `priority_rank` on the wire."""
    return FACTORS[cell][0]


# --------------------------------------------------------------- contamination


def _golden_terms() -> list[str]:
    """Every token a golden paper could be recognised by: title words and author surnames.

    Read from `eval/golden/*.yaml` as text rather than parsed, so the check keeps working if the
    golden files gain fields, and so it also sweeps the prose `why` lines where author names live.
    """
    stop = {
        "the", "and", "for", "with", "from", "that", "this", "what", "when", "why", "how", "a",
        "an", "of", "in", "on", "to", "is", "are", "be", "it", "as", "at", "by", "or", "not",
        "effects", "effect", "evidence", "using", "into", "more", "than", "we", "search",
        "review", "scientific", "literature", "retrieval", "benchmark", "agent", "llm", "paper",
        "papers", "savings", "saving", "default", "defaults", "decisions", "decision", "active",
        "behavior", "behavioral", "economics", "options", "accounts", "rate", "toolkit", "human",
        "deep", "research", "helps", "lists", "ground", "truth", "open", "environments", "taxonomy",
        "guided", "academic", "comprehensive", "synthesizing", "augmented", "lms", "increase",
        "employee", "better", "worse", "power", "suggestion", "inertia", "participation",
        "automatic", "enrollment", "contribution", "employer", "based", "short", "term",
        "retirement", "dynamics", "smaller", "thought", "policies", "influence", "meta", "analysis",
        "optimal", "passive", "crowd", "out", "denmark", "tomorrow", "save",
        "rethinking", "evaluation", "citation", "agentic",
    }
    terms: set[str] = set()
    for path in sorted((REPO / "eval/golden").glob("*.yaml")):
        raw = path.read_text(encoding="utf-8")
        for title in re.findall(r"^\s*title:\s*(.+)$", raw, flags=re.M):
            for token in re.findall(r"[A-Za-z][A-Za-z'-]{3,}", title):
                if token.lower() not in stop:
                    terms.add(token.lower())
        # Author surnames as the `why` lines spell them: "Choukhmane 2025", "Choi et al 2024".
        for surname in re.findall(r"\b([A-Z][a-z]{2,})(?:\s+(?:et al|&|\d{4}))", raw):
            if surname.lower() not in stop:
                terms.add(surname.lower())
    return sorted(terms)


#: Words that a golden title happens to share with ordinary rubric English and that appear in the
#: SHIPPED text already. A contamination check that fires on the control is measuring nothing.
def check_contamination(cells: tuple[str, ...] = CELLS) -> dict[str, list[str]]:
    """Terms a variant introduces that the shipped control does not already contain.

    Only *introduced* terms count. The shipped rubric's own worked example quotes a golden paper
    (the `32831b736c11` block), and that text is present in every cell including the control — it is
    part of what is being held constant, not contamination this slice added.
    """
    base = shipped_text().lower()
    findings: dict[str, list[str]] = {}
    for cell in cells:
        text = variant(cell).lower()
        hits = [
            term
            for term in _golden_terms()
            if re.search(rf"\b{re.escape(term)}\b", text)
            and not re.search(rf"\b{re.escape(term)}\b", base)
        ]
        if hits:
            findings[cell] = hits
    return findings


# --------------------------------------------------------------------- outputs


def write_all() -> None:
    """Emit the four variant texts and the three diffs — the ratification artefact."""
    out = HERE / "rubrics"
    out.mkdir(parents=True, exist_ok=True)
    base = shipped_text()
    assert variant("C0") == base, "C0 must be the shipped rubric byte for byte"
    for cell in CELLS:
        text = variant(cell)
        (out / f"{cell}.md").write_text(text, encoding="utf-8")
        if cell == "C0":
            continue
        diff = "".join(
            difflib.unified_diff(
                base.splitlines(keepends=True),
                text.splitlines(keepends=True),
                fromfile="skills/research-scan/references/rerank-rubric.md (C0)",
                tofile=f"phase14/rubrics/{cell}.md",
                n=3,
            )
        )
        (out / f"{cell}.diff").write_text(diff, encoding="utf-8")

    bad = check_contamination()
    status = "clean" if not bad else f"CONTAMINATED {bad}"
    print(f"contamination check: {status}")
    for cell in CELLS:
        text = variant(cell)
        print(f"  {cell:3s} sha256[:16]={digest(cell)}  {len(text):6d} chars  "
              f"priority_rank={'yes' if uses_priority_rank(cell) else 'no '}")
    if bad:
        raise SystemExit(2)


if __name__ == "__main__":
    write_all()
