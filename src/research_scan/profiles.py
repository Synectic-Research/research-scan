# SPDX-License-Identifier: Apache-2.0
"""Run profiles (v0.2.1) — the cost/recall dial, chosen once at `init`.

V1 had one setting and V1.1 added a second retrieval round to it, so the cheapest possible scan and
the most thorough one were the same scan. That is fine for a golden-set experiment and wrong for a
tool somebody runs on a Tuesday: a `quick` scan should cost a fraction of a `deep` one and say so,
rather than being a `deep` scan with flags remembered by hand.

Three knobs and one policy, and nothing else. Every value here is already a documented default
somewhere in the codebase; the profile only decides which one applies. A flag still wins over the
profile — `--per-query 60` means 60 whatever the profile says — because the profile is a starting
point, not a lock.

`max_outside_window` is a **total for the run**, not a per-stage allowance. Out-of-window classics
are the one part of the pool that grows every time a stage runs, and V1.1's gap round quietly
doubled them by taking a second full allowance of its own.
"""

from __future__ import annotations

from dataclasses import dataclass

from research_scan.schema import Profile


@dataclass(frozen=True)
class ProfileSettings:
    """What a profile decides. `max_candidates` of `None` means scale by built-source count."""

    per_query: int
    max_candidates: int | None
    max_outside_window: int
    gap_round: str

    def label(self) -> str:
        cap = "scaled" if self.max_candidates is None else str(self.max_candidates)
        return f"per_query {self.per_query} · cap {cap} · outside {self.max_outside_window}"


#: `gap_round` is one of `never`, `conditional` (the `coverage` trigger decides), `always`.
PROFILES: dict[Profile, ProfileSettings] = {
    Profile.quick: ProfileSettings(
        per_query=20, max_candidates=250, max_outside_window=12, gap_round="never"
    ),
    Profile.standard: ProfileSettings(
        per_query=40, max_candidates=450, max_outside_window=20, gap_round="conditional"
    ),
    Profile.deep: ProfileSettings(
        per_query=40, max_candidates=None, max_outside_window=30, gap_round="always"
    ),
}


def settings_for(profile: Profile) -> ProfileSettings:
    return PROFILES[profile]
