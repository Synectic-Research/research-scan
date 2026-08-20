# SPDX-License-Identifier: Apache-2.0
"""`evidence.md` and `evidence.bib` (spec §9.8) — the human-readable end of the scan.

The Markdown is written to be read top-down by someone deciding what to open: a table first, then
one block per paper answering "what did it find, and what does that mean for this project". An
unverified paper is never quietly dropped and never quietly presented as sound — it carries
`[UNVERIFIED — check manually]` in both the table and its block.
"""

from __future__ import annotations

import re
from datetime import date

from research_scan.schema import CoverageFile, Evidence, EvidencePacket

UNVERIFIED_MARKER = "[UNVERIFIED — check manually]"

_BIB_KEY_STRIP = re.compile(r"[^A-Za-z0-9]+")
_BIB_TYPES = {
    "preprint": "misc",
    "book-chapter": "incollection",
}


def render_markdown(
    evidence: Evidence,
    *,
    generated_on: date | None = None,
    criterion_names: dict[str, str] | None = None,
    coverage: CoverageFile | None = None,
) -> str:
    """The table, then one block per paper, then the alternates (§9.8).

    `criterion_names` maps sub-criterion ids to their names from `queries.json`, so the why-line
    can say `C1 default effect size` rather than a bare `C1`. Optional — old runs render fine.

    `coverage` adds one section saying what each sub-criterion was covered by and what the gap
    round recovered. Also optional: without it the page is byte-identical to V1's.
    """
    run = evidence.run
    lines = [
        f"# Evidence scan — {run.slug}",
        "",
        f"Run `{run.run_dir}` · brief `{run.brief_path}`"
        + (f" · rendered {generated_on.isoformat()}" if generated_on else ""),
        "",
    ]

    unverified = [packet for packet in evidence.packets if not packet.verification.verified]
    if unverified:
        lines += [
            f"> {len(unverified)} of {len(evidence.packets)} papers could not be verified against a"
            " live record. They are marked below; check them by hand before citing.",
            "",
        ]

    lines += ["| # | Paper | Year | Venue | Evidence | Verified |", "|---|---|---|---|---|---|"]
    for packet in evidence.packets:
        lines.append(
            f"| {packet.rank} | {_paper_cell(packet)} | {packet.year or '—'} |"
            f" {_escape(packet.venue or '—')} | {packet.evidence_level.value} |"
            f" {'yes' if packet.verification.verified else UNVERIFIED_MARKER} |"
        )
    lines.append("")

    for packet in evidence.packets:
        lines += _packet_block(packet, criterion_names or {})

    if coverage and coverage.rounds:
        lines += _coverage_block(coverage)

    if evidence.alternates:
        lines += ["## Alternates", "", "Next in order, not selected:", ""]
        for packet in evidence.alternates:
            label = _escape(packet.title)
            link = f"[{label}]({packet.url})" if packet.url else label
            lines.append(f"- {link} ({packet.year or 'n.d.'}) — overall {packet.overall}/3")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _coverage_block(coverage: CoverageFile) -> list[str]:
    """What the scan looked for and what it found — the part a reader cannot check themselves.

    A thin criterion is not a failure to report quietly. It says "on this dimension the scan found
    little", which a reader has to know before treating the list as an answer.
    """
    first, latest = coverage.rounds[0], coverage.rounds[-1]
    gap_round = latest.round > first.round
    lines = ["## Coverage", ""]
    header = "| Criterion | Papers kept |" + (" Gap round added |" if gap_round else "")
    lines += [header, "|---|---|" + ("---|" if gap_round else "")]

    before = {criterion.id: criterion.hits for criterion in first.criteria}
    for criterion in latest.criteria:
        row = f"| {criterion.id} {_escape(criterion.name)} | {criterion.hits}"
        if gap_round:
            row += f" | +{criterion.hits - before.get(criterion.id, 0)}"
        lines.append(row + " |")
    lines.append("")

    thin = [f"{c.id} {c.name}" for c in latest.criteria if c.thin]
    if thin:
        lines += [
            f"Still thin after {'the gap round' if gap_round else 'round 1'}: "
            + ", ".join(_escape(name) for name in thin)
            + ". Treat conclusions on those dimensions as under-evidenced.",
            "",
        ]
    if latest.unattributed_ge2:
        lines += [
            f"{latest.unattributed_ge2} kept paper(s) carry no criterion attribution, so the counts"
            " above are a lower bound.",
            "",
        ]
    return lines


def _paper_cell(packet: EvidencePacket) -> str:
    """The title, linked when the packet has a url — a table row you can click is the point.

    The DOI rides alongside as plain text when there is one. It is usually the same target the
    link already points at, but a link is for clicking and a DOI is for pasting into a reference
    manager, and the packet block prints neither in a form you can copy from a table.
    """
    label = _escape(packet.title)
    cell = f"[{label}]({packet.url})" if packet.url else label
    if packet.ids.doi:
        cell += f" · {_escape(packet.ids.doi)}"
    return cell


def _packet_block(packet: EvidencePacket, criterion_names: dict[str, str]) -> list[str]:
    heading = f"## {packet.rank}. {packet.title}"
    if not packet.verification.verified:
        heading += f" {UNVERIFIED_MARKER}"

    authors = ", ".join(author.name for author in packet.authors[:4])
    if len(packet.authors) > 4:
        authors += " et al."

    lines = [
        heading,
        "",
        f"{authors or 'Unknown authors'} · {packet.year or 'n.d.'} · {packet.venue or 'no venue'}"
        f" · {packet.evidence_level.value} · overall {packet.overall}/3",
        "",
    ]
    if packet.url:
        lines += [f"<{packet.url}>", ""]

    lines += [
        f"**Key finding.** {packet.key_finding}",
        "",
        f"**Why it made the cut.** {why_it_made_the_cut(packet, criterion_names)}",
        "",
        f"**Why it matters here.** {packet.why_it_matters}",
        "",
        f"**Method.** {packet.methodology}",
        "",
    ]
    if packet.limitations:
        lines += ["**Limitations.**", ""]
        lines += [f"- {item}" for item in packet.limitations]
        lines.append("")

    flag_names = ("review", "contradicts", "methods_paper")
    flags = [name for name in flag_names if getattr(packet.flags, name)]
    criteria = " · ".join(f"{key} {value}/3" for key, value in sorted(packet.criteria.items()))
    trail = [f"selected: {packet.selection_reason.value}", f"criteria: {criteria}"]
    if flags:
        trail.append("flags: " + ", ".join(flags))
    trail.append(_verification_note(packet))
    lines += [f"<sub>{' · '.join(trail)}</sub>", ""]
    return lines


def why_it_made_the_cut(packet: EvidencePacket, criterion_names: dict[str, str]) -> str:
    """Fuse relation, selection reason and the strongest sub-criterion into one line (S4.5).

    Distinct from "Why it matters here": that is the design consequence; this is the
    meta-justification — what kind of paper it is and what earned it the slot.
    """
    parts: list[str] = []
    if packet.relation is not None:
        parts.append(packet.relation.value)
    parts.append(f"selected by {packet.selection_reason.value}")
    if packet.criteria:
        # Highest score wins; ties go to the lowest id, since C1 is usually the problem-match axis.
        best_id = min(packet.criteria, key=lambda key: (-packet.criteria[key], key))
        label = criterion_names.get(best_id)
        strongest = f"{best_id} {label}" if label else best_id
        parts.append(f"strongest on {strongest} ({packet.criteria[best_id]}/3)")
    lead = " · ".join(parts)
    return f"{lead}. {packet.relevance_reason}"


def _verification_note(packet: EvidencePacket) -> str:
    verification = packet.verification
    if verification.verified:
        sources = ", ".join(item.value for item in verification.verified_by) or "no source"
        return f"verified {verification.verified_on} via {sources}"
    problems = ", ".join(item.value for item in verification.mismatches) or "no record"
    return f"UNVERIFIED ({problems})"


def render_bib(evidence: Evidence) -> str:
    """search-lit-compatible entries carrying the verification trail (§9.8)."""
    entries = [_bib_entry(packet) for packet in evidence.packets]
    return "\n".join(entries)


def _bib_entry(packet: EvidencePacket) -> str:
    fields: list[tuple[str, str]] = [
        ("title", packet.title),
        ("author", " and ".join(author.name for author in packet.authors)),
    ]
    if packet.year:
        fields.append(("year", str(packet.year)))
    if packet.venue:
        fields.append(("journal", packet.venue))
    if packet.ids.doi:
        fields.append(("doi", packet.ids.doi))
    if packet.ids.arxiv:
        fields.append(("eprint", packet.ids.arxiv))
    if packet.url:
        fields.append(("url", packet.url))
    fields += [
        ("verified", "true" if packet.verification.verified else "false"),
        ("verified_by", ", ".join(item.value for item in packet.verification.verified_by)),
        ("verified_on", packet.verification.verified_on),
    ]
    if packet.verification.mismatches:
        note = ", ".join(m.value for m in packet.verification.mismatches)
        fields.append(("verification_note", note))

    body = ",\n".join(f"  {name} = {{{_bib_escape(value)}}}" for name, value in fields if value)
    return f"@{_bib_type(packet)}{{{_bib_key(packet)},\n{body}\n}}\n"


def _bib_type(packet: EvidencePacket) -> str:
    return _BIB_TYPES.get(packet.type.value, "article")


def _bib_key(packet: EvidencePacket) -> str:
    author = packet.authors[0].name.split()[-1] if packet.authors else "anon"
    word = next((part for part in _BIB_KEY_STRIP.split(packet.title) if len(part) > 3), "paper")
    return f"{_BIB_KEY_STRIP.sub('', author).lower()}{packet.year or 'nd'}{word.lower()}"


def _bib_escape(value: str) -> str:
    return value.replace("{", "(").replace("}", ")")


def _escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")
