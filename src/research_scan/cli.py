# SPDX-License-Identifier: Apache-2.0
"""Typer entry point.

S0 registered `doctor` and `schema`; S1 added `init` and `retrieve`; S2 added `expand`,
`shortlist`, `verify` and `emit`; S4 adds `eval`. Every registered command works — `--help` never
advertises a command that does not.

Commands stay thin here — parse arguments, call into the stage module, choose an exit code.

Exit codes (spec §6): 0 ok · 1 runtime failure · 2 input/schema error · 3 doctor mandatory fail.
"""

import getpass
import importlib.util
import json
import logging
import os
import platform
import sys
from pathlib import Path

import typer
from typer import completion

from research_scan import (
    __version__,
    config,
    doctor,
    evalrun,
    expand,
    log,
    profiles,
    run,
    schema,
    select,
    shortlist,
)
from research_scan import coverage as coverage_module
from research_scan import deployment as deployment_module
from research_scan import render as render_module
from research_scan import retrieve as retrieve_module
from research_scan import verify as verify_module
from research_scan.http import HttpClient
from research_scan.schema import (
    CandidatesFile,
    CoverageFile,
    Defaults,
    Domain,
    Evidence,
    Profile,
    QueryPlan,
    Ranked,
    ScreenBatch,
    ScreenFile,
    SourceName,
    Window,
)
from research_scan.sources.crossref import CrossrefSource
from research_scan.sources.openalex import OpenAlexSource
from research_scan.sources.s2 import S2Source

logger = log.get_logger(__name__)

# `add_completion=False` below keeps `--install-completion` / `--show-completion` off the root,
# but it also skips registering the per-shell completion classes. The shell's callback re-invokes
# this binary with `_RESEARCH_SCAN_COMPLETE` set and click intercepts it before any command runs,
# so registration has to happen here, at import. It adds no option to any command.
completion.completion_init()

#: Module-level singleton: ruff B008 forbids a call in a default, and Typer needs one here.
PROFILE_OPTION = typer.Option(
    Profile.standard,
    "--profile",
    help="quick (cheap) · standard · deep (widest). Sets per-query depth, pool cap, "
    "out-of-window total and whether the gap round runs.",
)
DOMAIN_OPTION = typer.Option(Domain.general, "--domain", help="Routing domain.")

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    # Without this Typer demands a subcommand before the callback runs, so the advertised
    # `--version` exited 2 with "Missing command" — `--help` must never advertise vapour.
    invoke_without_command=True,
    help="Verified evidence scans for a project brief. The agent reasons; this CLI retrieves.",
)


@app.callback()
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", help="Print the version and exit."),
) -> None:
    if version:
        typer.echo(__version__)
        raise typer.Exit(0)
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(0)


#: What `configure` asks for, in order. `secret` decides echo; `required` decides whether an
#: empty answer on a first run is acceptable. The wording matches what `doctor` reports, so the
#: two never disagree about which keys actually matter.
CREDENTIAL_PROMPTS: tuple[tuple[str, bool, bool, str], ...] = (
    ("OPENALEX_API_KEY", True, True, "the primary source; free key at openalex.org"),
    ("OPENALEX_MAILTO", False, False, "your email; raises OpenAlex to 5 req/s, Crossref polite"),
    ("S2_API_KEY", True, False, "arrives by email — skip it and re-run configure later"),
    ("NCBI_API_KEY", True, False, "biomedical topics only"),
)


@app.command("configure")
@app.command("setup", hidden=True)
def configure_(
    quiet: bool = typer.Option(False, "--quiet", help="Silence the stderr log."),
    log_level: str = typer.Option("INFO", "--log-level", help="Stderr log level."),
) -> None:
    """Set up credentials interactively, then prove they work. Alias: `setup`.

    Writes ~/.config/research-scan/.env (0600, in a 0700 directory), merging into whatever is
    already there — comments and variables this command does not ask about are left alone.
    Safe to re-run: every variable shows its current state, Enter keeps it, typing replaces it.
    Ends by running `doctor`.
    """
    settings = config.load()
    log.configure(log_level, quiet=quiet, settings=settings)
    target = config.config_env_path()

    if not _interactive():
        # A prompt with nothing to read from is a hang. Say what to write, and get out.
        typer.echo(f"stdin is not a terminal, so there is nothing to prompt. Write {target}:")
        typer.echo("")
        width = max(len(name) for name, *_ in CREDENTIAL_PROMPTS)
        for name, _secret, required, why in CREDENTIAL_PROMPTS:
            label = "required" if required else "optional"
            typer.echo(f"  {(name + '=').ljust(width + 1)}   # {label} — {why}")
        typer.echo("")
        typer.echo("Then run: research-scan doctor")
        raise typer.Exit(2)

    typer.echo(f"Credentials are written to {target}")
    typer.echo("Enter keeps the current value. Ctrl-C aborts without writing.\n")

    answers: dict[str, str] = {}
    for name, secret, required, why in CREDENTIAL_PROMPTS:
        current = settings.values.get(name)
        state = (
            f"set, {config.mask(current)} (from {settings.origin_of(name)})" if current else "unset"
        )
        typer.echo(f"{name} — {why}")
        typer.echo(f"  currently {state}")
        # getpass keeps a key off the screen and out of the scrollback; the mailto is not a secret.
        entered = (
            getpass.getpass("  > ")
            if secret
            # Same prompt shape as getpass's, so the two do not look like different questions.
            else typer.prompt("  >", default="", show_default=False, prompt_suffix=" ")
        ).strip()
        if entered:
            answers[name] = entered
        elif required and not current:
            _fail(
                f"{name} is required — get one at openalex.org, then run configure again",
                False,
                code=2,
            )
        typer.echo("")

    if answers:
        written = config.write_env(answers)
        typer.echo(f"wrote {', '.join(sorted(answers))} to {written}\n")
    else:
        typer.echo("nothing changed\n")

    # Through HttpClient like every other caller: doctor proves a source by invoking it.
    settings = config.load()
    with HttpClient(settings, cache=False, timeout=20.0, max_retries=1) as client:
        report = doctor.run_checks(settings, client)
    typer.echo(doctor.render_compact(report))
    raise typer.Exit(report.exit_code)


@app.command("version")
def version_(
    json_output: bool = typer.Option(False, "--json", help="Machine-readable stdout."),
) -> None:
    """Print the version, and what this install can actually do.

    `--version` on the root stays the bare number for scripts that already parse it.
    """
    # `mcp` reports whether the server can actually start. Since v0.5 its dependencies ship by
    # default, so this is "enabled" on any intact install — and "disabled" is the signal that
    # something is missing, which is worth a published key saying out loud.
    extra = "enabled" if importlib.util.find_spec("fastmcp") else "disabled"
    if json_output:
        typer.echo(
            json.dumps(
                {
                    "version": __version__,
                    "python": platform.python_version(),
                    "platform": platform.platform(),
                    "mcp": extra,
                },
                indent=2,
            )
        )
    else:
        typer.echo(f"research-scan {__version__}")
        typer.echo(f"python       {platform.python_version()}")
        typer.echo(f"platform     {platform.platform()}")
        typer.echo(f"mcp          {extra}")


@app.command("init")
def init_(
    brief: str = typer.Argument(..., metavar="BRIEF", help="Path to a brief.md, or a question."),
    slug: str | None = typer.Option(None, "--slug", help="Run name. Default: derived from BRIEF."),
    from_: str | None = typer.Option(None, "--from", help="Window start, YYYY-MM."),
    to: str | None = typer.Option(None, "--to", help="Window end, YYYY-MM. Default: today."),
    top: int = typer.Option(10, "--top", help="Papers to emit."),
    foundational: int = typer.Option(2, "--foundational", help="Out-of-window slots within --top."),
    domain: Domain = DOMAIN_OPTION,
    profile: Profile = PROFILE_OPTION,
    json_output: bool = typer.Option(False, "--json", help="Print RunInfo as JSON."),
    quiet: bool = typer.Option(False, "--quiet", help="Silence the stderr log."),
    log_level: str = typer.Option("INFO", "--log-level", help="Stderr log level."),
) -> None:
    """Create a run directory and print the RunInfo the planning agent must respect."""
    settings = config.load()
    log.configure(log_level, quiet=quiet, settings=settings)

    window = run.default_window()
    if from_ or to:
        try:
            window = Window(from_=from_ or window.from_, to=to)
        except Exception as exc:
            _fail(f"invalid window: {exc}", json_output, code=2)

    defaults = Defaults(
        window=window,
        top=top,
        foundational=foundational,
        domain=domain,
        sources=list(retrieve_module.ROUTING[domain]),
        profile=profile,
    )
    try:
        info = run.create_run(brief, slug=slug, defaults=defaults)
    except OSError as exc:
        _fail(f"cannot create the run directory: {exc}", json_output, code=1)

    if json_output:
        typer.echo(json.dumps(info.model_dump(mode="json", by_alias=True), indent=2))
    else:
        typer.echo(f"run_dir     {info.run_dir}")
        typer.echo(f"brief       {info.brief_path}")
        typer.echo(f"window      {window.from_ or '(36 months back)'} → {window.to or 'today'}")
        typer.echo(f"domain      {domain.value}")
        typer.echo(f"sources     {', '.join(source.value for source in defaults.sources)}")
        typer.echo(f"top / found {top} / {foundational}")
        typer.echo(f"\nnext: write {info.run_dir}/queries.json, then `research-scan retrieve`")


@app.command("retrieve")
def retrieve_(
    run_dir: str | None = typer.Option(None, "--run", help="Run directory. Default: the newest."),
    per_query: int | None = typer.Option(None, "--per-query", help="Hits per query per source."),
    max_candidates: int | None = typer.Option(None, "--max-candidates", help="Hard pool cap."),
    sources: str | None = typer.Option(
        None, "--sources", help="Comma-separated override of the domain routing map."
    ),
    include_preprints: bool = typer.Option(
        True, "--include-preprints/--no-include-preprints", help="Keep preprints in the pool."
    ),
    include_all_types: bool = typer.Option(
        False, "--include-all-types", help="Keep paratext, errata and datasets."
    ),
    round_: int = typer.Option(
        1, "--round", min=1, max=2, help="2 runs the gap round: `queries.json.round2`, appended."
    ),
    json_output: bool = typer.Option(False, "--json", help="Machine-readable stdout."),
    quiet: bool = typer.Option(False, "--quiet", help="Silence the stderr log."),
    log_level: str = typer.Option("INFO", "--log-level", help="Stderr log level."),
    no_cache: bool = typer.Option(False, "--no-cache", help="Bypass the 7-day HTTP cache."),
) -> None:
    """Query every routed source, then dedup, filter, cap and write the screening batches."""
    settings = config.load()
    log.configure(log_level, quiet=quiet, settings=settings)
    started = run.now()

    try:
        directory = run.resolve_run_dir(run_dir, settings)
        manifest = run.read_manifest(directory)
        plan = run.read_model(directory / "queries.json", QueryPlan)
        source_names = _parse_sources(sources)
        existing = (
            run.read_model(directory / "candidates.json", CandidatesFile).candidates
            if round_ == 2
            else []
        )
    except run.StageInputError as exc:
        _fail_stage(exc, json_output)
    except ValueError as exc:
        _fail(str(exc), json_output, code=2)

    if round_ == 2 and not plan.round2:
        _fail(
            "the gap round needs `round2` queries in queries.json — run `coverage` first, then"
            " write one or two queries per thin sub-criterion",
            json_output,
            code=2,
        )

    domain = run.resolve(plan.domain, manifest.defaults.domain)
    window = run.resolve(plan.window, manifest.defaults.window)
    routed = retrieve_module.route(domain, plan, source_names)
    bounds = run.window_bounds(window)

    built = sum(1 for name in routed if name in retrieve_module.IMPLEMENTED_SOURCES)
    tuning = profiles.settings_for(manifest.defaults.profile)
    options = retrieve_module.RetrieveOptions(
        per_query=per_query or tuning.per_query,
        max_candidates=max_candidates
        or tuning.max_candidates
        or retrieve_module.scaled_max_candidates(built),
        include_preprints=include_preprints,
        include_all_types=include_all_types,
        cache=False if no_cache else None,
        round=round_,
    )
    stage = "retrieval" if round_ == 1 else "retrieval-r2"

    with log.StageLog(directory, stage, settings=settings) as stage_log:
        stage_log.event(
            "plan",
            domain=domain.value,
            window=[bounds[0].isoformat(), bounds[1].isoformat()],
            sources=[name.value for name in routed],
            queries=len(plan.round2 if round_ == 2 else plan.queries),
            per_query=options.per_query,
            max_candidates=options.max_candidates,
            profile=manifest.defaults.profile.value,
        )
        with HttpClient(settings, cache=not no_cache) as client:
            try:
                result = retrieve_module.run_retrieve(
                    directory,
                    manifest.run,
                    plan,
                    client,
                    sources=routed,
                    window=bounds,
                    options=options,
                    on_event=stage_log.event,
                    existing=existing,
                )
            except retrieve_module.AllSourcesFailed as exc:
                stage_log.event("failed", error=str(exc))
                _fail(str(exc), json_output, code=1)
            stage_log.event("http", **client.stats.to_dict())

    section = "retrieval" if round_ == 1 else "retrieval_round2"
    counts = (
        result.counts
        if round_ == 1
        else manifest.counts.model_copy(
            update={
                "retrieved": manifest.counts.retrieved + result.counts.retrieved,
                "deduped": result.counts.deduped,
            }
        )
    )
    run.upsert_manifest(
        directory,
        counts=counts,
        timestamps=run.stamp(
            manifest.timestamps, "retrieve" if round_ == 1 else "retrieve-r2", started, run.now()
        ),
        **{section: result.stats},
    )

    payload = {
        "ok": True,
        "run_dir": str(directory),
        "round": round_,
        "retrieval": result.stats.model_dump(mode="json"),
        "counts": counts.model_dump(mode="json"),
        "per_query_hits": result.per_query_hits,
        "added": len(result.added),
        "batches": result.batches,
        "abstract_ratio": round(result.stats.abstracts_present / len(result.candidates), 3)
        if result.candidates
        else 0.0,
    }
    if json_output:
        typer.echo(json.dumps(payload, indent=2))
    else:
        typer.echo(_render_retrieve(payload))


@app.command("expand")
def expand_(
    run_dir: str | None = typer.Option(None, "--run", help="Run directory. Default: the newest."),
    seeds: int | None = typer.Option(None, "--seeds", help="Max seeds to expand from."),
    max_new: int | None = typer.Option(None, "--max-new", help="Cap on in-window additions."),
    max_outside_window: int | None = typer.Option(
        None, "--max-outside-window", help="Cap on out-of-window additions."
    ),
    round_: int = typer.Option(
        1, "--round", min=1, max=2, help="2 seeds the gap round from what the gap queries found."
    ),
    json_output: bool = typer.Option(False, "--json", help="Machine-readable stdout."),
    quiet: bool = typer.Option(False, "--quiet", help="Silence the stderr log."),
    log_level: str = typer.Option("INFO", "--log-level", help="Stderr log level."),
    no_cache: bool = typer.Option(False, "--no-cache", help="Bypass the 7-day HTTP cache."),
) -> None:
    """Walk the citation graph out from every screened-relevant paper (§8.5)."""
    settings, directory, manifest, started = _stage_setup(log_level, quiet, run_dir, json_output)
    try:
        plan = run.read_model(directory / "queries.json", QueryPlan)
        screen = run.read_model(directory / "screen.json", ScreenFile)
        candidates = run.read_model(directory / "candidates.json", CandidatesFile)
        # The gap round's own additions, straight from the batches `retrieve --round 2` wrote.
        new_cids: set[str] = set()
        if round_ == 2:
            for path in sorted((directory / "screen-batches").glob("r[0-9][0-9].json")):
                new_cids |= {item.cid for item in run.read_model(path, ScreenBatch).items}
    except run.StageInputError as exc:
        _fail_stage(exc, json_output)

    attribution = coverage_module.validate_criteria_hit(plan, screen)
    if not attribution.ok:
        _fail_stage(
            run.StageInputError(
                "screen.json names sub-criteria that queries.json does not define",
                lines=attribution.lines(),
            ),
            json_output,
        )

    window = run.window_bounds(run.resolve(plan.window, manifest.defaults.window))
    tuning = profiles.settings_for(manifest.defaults.profile)
    # The out-of-window cap is a total for the run, so the gap round inherits what round 1 left.
    spent = expand.outside_window_spent(directory, round_)
    budget = max_outside_window if max_outside_window is not None else tuning.max_outside_window
    options = expand.ExpandOptions(
        seeds=seeds or expand.DEFAULT_SEEDS,
        max_new=max_new or expand.DEFAULT_MAX_NEW,
        max_outside_window=max(0, budget - spent),
        cache=False if no_cache else None,
        round=round_,
    )

    with (
        log.StageLog(
            directory, "expansion" if round_ == 1 else "expansion-r2", settings=settings
        ) as stage_log,
        HttpClient(settings, cache=not no_cache) as client,
    ):
        try:
            result = expand.run_expand(
                directory,
                manifest.run,
                plan,
                candidates.candidates,
                screen,
                S2Source(client),
                OpenAlexSource(client),
                settings=client.settings,
                window=window,
                options=options,
                on_event=stage_log.event,
                new_cids=new_cids,
            )
        except expand.NoSeeds as exc:
            stage_log.event("failed", error=str(exc))
            _fail(str(exc), json_output, code=1)
        stage_log.event("http", **client.stats.to_dict())

    counts = manifest.counts.model_copy(
        update={"expanded": manifest.counts.expanded + len(result.expanded.added)}
        if round_ == 2
        else {"expanded": len(result.expanded.added)}
    )
    run.upsert_manifest(
        directory,
        counts=counts,
        timestamps=run.stamp(
            manifest.timestamps, "expand" if round_ == 1 else "expand-r2", started, run.now()
        ),
        **{("expansion" if round_ == 1 else "expansion_round2"): result.stats},
    )

    payload = {
        "ok": True,
        "run_dir": str(directory),
        "round": round_,
        **result.expanded.model_dump(mode="json"),
        "candidates_total": result.total_candidates,
    }
    if json_output:
        typer.echo(json.dumps(payload, indent=2))
    else:
        typer.echo(
            f"seeds {len(result.expanded.seeds)} → added {len(result.expanded.added)} in-window, "
            f"{len(result.expanded.added_outside_window)} outside · "
            f"batches {', '.join(result.expanded.batches) or 'none'}"
        )


@app.command("shortlist")
def shortlist_(
    run_dir: str | None = typer.Option(None, "--run", help="Run directory. Default: the newest."),
    max_in_window: int | None = typer.Option(
        None, "--max-in-window", help="Cap on in-window rows."
    ),
    max_outside_window: int | None = typer.Option(
        None, "--max-outside-window", help="Cap on out-of-window rows."
    ),
    json_output: bool = typer.Option(False, "--json", help="Machine-readable stdout."),
    quiet: bool = typer.Option(False, "--quiet", help="Silence the stderr log."),
    log_level: str = typer.Option("INFO", "--log-level", help="Stderr log level."),
) -> None:
    """Check that every candidate was screened, then order and cut for the reranker."""
    _settings, directory, manifest, started = _stage_setup(log_level, quiet, run_dir, json_output)
    try:
        screen = run.read_model(directory / "screen.json", ScreenFile)
        candidates = run.read_model(directory / "candidates.json", CandidatesFile)
    except run.StageInputError as exc:
        _fail_stage(exc, json_output)

    coverage = shortlist.validate_coverage(candidates.candidates, screen)
    if not coverage.ok:
        _fail_stage(
            run.StageInputError(
                "screen.json does not cover candidates.json exactly once", lines=coverage.lines()
            ),
            json_output,
        )

    result = shortlist.build(
        candidates.candidates,
        screen,
        max_in_window=max_in_window or shortlist.DEFAULT_MAX_IN_WINDOW,
        max_outside_window=max_outside_window or shortlist.DEFAULT_MAX_OUTSIDE_WINDOW,
    )
    run.write_model(directory / "shortlist.json", result)

    scored = sum(1 for entry in screen.scores if entry.score >= shortlist.SHORTLIST_SCORE_THRESHOLD)
    counts = manifest.counts.model_copy(
        update={
            "screened_ge2": scored,
            "shortlisted": len(result.in_window) + len(result.outside_window),
        }
    )
    run.upsert_manifest(
        directory,
        counts=counts,
        timestamps=run.stamp(manifest.timestamps, "shortlist", started, run.now()),
    )

    payload = {
        "ok": True,
        "run_dir": str(directory),
        "screened": len(screen.scores),
        "screened_ge2": scored,
        "in_window": len(result.in_window),
        "outside_window": len(result.outside_window),
    }
    if json_output:
        typer.echo(json.dumps(payload, indent=2))
    else:
        typer.echo(
            f"screened {payload['screened']} · ≥2 {scored} · shortlist "
            f"{payload['in_window']} in-window + {payload['outside_window']} outside"
        )


@app.command("coverage")
def coverage_(
    run_dir: str | None = typer.Option(None, "--run", help="Run directory. Default: the newest."),
    gap_round: bool = typer.Option(
        False, "--gap-round", help="Force the gap round whatever the profile and counts say."
    ),
    json_output: bool = typer.Option(False, "--json", help="Machine-readable stdout."),
    quiet: bool = typer.Option(False, "--quiet", help="Silence the stderr log."),
    log_level: str = typer.Option("INFO", "--log-level", help="Stderr log level."),
) -> None:
    """Count how well each sub-criterion is covered, so the gap round has something to aim at."""
    _settings, directory, manifest, started = _stage_setup(log_level, quiet, run_dir, json_output)
    try:
        plan = run.read_model(directory / "queries.json", QueryPlan)
        screen = run.read_model(directory / "screen.json", ScreenFile)
        candidates = run.read_model(directory / "candidates.json", CandidatesFile)
    except run.StageInputError as exc:
        _fail_stage(exc, json_output)

    attribution = coverage_module.validate_criteria_hit(plan, screen)
    if not attribution.ok:
        _fail_stage(
            run.StageInputError(
                "screen.json names sub-criteria that queries.json does not define",
                lines=attribution.lines(),
            ),
            json_output,
        )

    path = directory / "coverage.json"
    previous = None
    if path.exists():
        try:
            previous = run.read_model(path, CoverageFile)
        except run.StageInputError:
            # A coverage file from an older contract is history, not an input worth failing on.
            previous = None

    result = coverage_module.build(
        manifest.run,
        plan,
        candidates.candidates,
        screen,
        previous=previous,
        profile=manifest.defaults.profile,
        forced=gap_round,
    )
    run.write_model(path, result)
    run.upsert_manifest(
        directory,
        timestamps=run.stamp(manifest.timestamps, "coverage", started, run.now()),
    )

    latest = result.rounds[-1]
    if attribution.missing:
        logger.warning(
            "%d paper(s) scored ≥ 2 with no criteria_hit — they count as unattributed",
            len(attribution.missing),
        )
    payload = {
        "ok": True,
        "run_dir": str(directory),
        "round": latest.round,
        "thin": coverage_module.thin_criteria(latest),
        "gap_round": result.gap_round.model_dump(mode="json") if result.gap_round else None,
        **latest.model_dump(mode="json"),
    }
    if json_output:
        typer.echo(json.dumps(payload, indent=2))
    else:
        typer.echo(coverage_module.render(result))


@app.command("verify")
def verify_(
    run_dir: str | None = typer.Option(None, "--run", help="Run directory. Default: the newest."),
    strict: bool = typer.Option(False, "--strict", help="Require a 95 title match, not 90."),
    json_output: bool = typer.Option(False, "--json", help="Machine-readable stdout."),
    quiet: bool = typer.Option(False, "--quiet", help="Silence the stderr log."),
    log_level: str = typer.Option("INFO", "--log-level", help="Stderr log level."),
    no_cache: bool = typer.Option(False, "--no-cache", help="Bypass the 7-day HTTP cache."),
) -> None:
    """Check every ranked paper against the live record and record what did not match (§10.5)."""
    settings, directory, manifest, started = _stage_setup(log_level, quiet, run_dir, json_output)
    try:
        ranked = run.read_model(directory / "ranked.json", Ranked)
        candidates = run.read_model(directory / "candidates.json", CandidatesFile)
    except run.StageInputError as exc:
        _fail_stage(exc, json_output)

    by_cid = {candidate.cid: candidate for candidate in candidates.candidates}
    unknown = sorted({entry.cid for entry in ranked.root if entry.cid not in by_cid})
    if unknown:
        _fail_stage(
            run.StageInputError(
                "ranked.json contains cids that are not in candidates.json",
                lines=[f"unknown cid: {cid}" for cid in unknown[:10]],
            ),
            json_output,
        )

    options = verify_module.VerifyOptions(strict=strict, cache=False if no_cache else None)
    with (
        log.StageLog(directory, "verify", settings=settings) as stage_log,
        HttpClient(settings, cache=not no_cache) as client,
    ):
        result = verify_module.run_verify(
            list(ranked.root),
            by_cid,
            CrossrefSource(client),
            OpenAlexSource(client),
            S2Source(client),
            options=options,
            on_event=stage_log.event,
        )
        stage_log.event("http", **client.stats.to_dict())

    run.write_model(directory / "ranked.json", Ranked(result.entries))
    counts = manifest.counts.model_copy(
        update={"ranked": len(result.entries), "verified": result.stats.verified}
    )
    run.upsert_manifest(
        directory,
        verification=result.stats,
        counts=counts,
        timestamps=run.stamp(manifest.timestamps, "verify", started, run.now()),
    )

    payload = {
        "ok": True,
        "run_dir": str(directory),
        "verification": result.stats.model_dump(mode="json"),
        "unverified": [
            {"title": title, "mismatches": [item.value for item in mismatches]}
            for title, mismatches in result.unverified
        ],
    }
    if json_output:
        typer.echo(json.dumps(payload, indent=2))
    else:
        typer.echo(
            f"verified {result.stats.verified}/{len(result.entries)} · "
            f"unverified {result.stats.unverified} · retracted {result.stats.dropped_retracted}"
            + (" · crossref skipped" if result.stats.crossref_skipped else "")
        )


@app.command("emit")
def emit_(
    run_dir: str | None = typer.Option(None, "--run", help="Run directory. Default: the newest."),
    top: int | None = typer.Option(None, "--top", help="Papers to emit."),
    foundational: int | None = typer.Option(
        None, "--foundational", help="Of --top, slots for out-of-window classics."
    ),
    contradicting: int = typer.Option(
        select.CONTRADICTING_SLOTS,
        "--contradicting",
        help="Slots reserved for counter-results, capped at half of --top. 0 disables.",
    ),
    bib: bool = typer.Option(True, "--bib/--no-bib", help="Also write evidence.bib."),
    json_output: bool = typer.Option(False, "--json", help="Machine-readable stdout."),
    quiet: bool = typer.Option(False, "--quiet", help="Silence the stderr log."),
    log_level: str = typer.Option("INFO", "--log-level", help="Stderr log level."),
) -> None:
    """Apply the selection rules and render the deliverable (§10.4, §9.8)."""
    _settings, directory, manifest, started = _stage_setup(log_level, quiet, run_dir, json_output)
    try:
        ranked = run.read_model(directory / "ranked.json", Ranked)
        candidates = run.read_model(directory / "candidates.json", CandidatesFile)
    except run.StageInputError as exc:
        _fail_stage(exc, json_output)

    by_cid = {candidate.cid: candidate for candidate in candidates.candidates}
    missing = sorted({entry.cid for entry in ranked.root if entry.cid not in by_cid})
    if missing:
        _fail_stage(
            run.StageInputError(
                "ranked.json contains cids that are not in candidates.json",
                lines=[f"unknown cid: {cid}" for cid in missing[:10]],
            ),
            json_output,
        )

    pairs = [(by_cid[entry.cid], entry) for entry in ranked.root]
    try:
        result = select.select(
            pairs,
            top=top or manifest.defaults.top,
            foundational=(
                foundational if foundational is not None else manifest.defaults.foundational
            ),
            contradicting=contradicting,
        )
    except select.NotVerified as exc:
        _fail_stage(run.StageInputError(str(exc), lines=exc.lines()), json_output)

    evidence = Evidence(run=manifest.run, packets=result.packets, alternates=result.alternates)
    run.write_model(directory / "evidence.json", evidence)

    # The why-line names sub-criteria when queries.json is present; a bare id otherwise.
    criterion_names: dict[str, str] = {}
    try:
        plan = run.read_model(directory / "queries.json", QueryPlan)
        criterion_names = {criterion.id: criterion.name for criterion in plan.sub_criteria}
    except run.StageInputError:
        pass

    # Same best-effort contract: a run that never ran `coverage` renders exactly as it did in V1.
    coverage_file: CoverageFile | None = None
    if (directory / "coverage.json").exists():
        try:
            coverage_file = run.read_model(directory / "coverage.json", CoverageFile)
        except run.StageInputError:
            coverage_file = None

    (directory / "evidence.md").write_text(
        render_module.render_markdown(
            evidence,
            generated_on=run.today(),
            criterion_names=criterion_names,
            coverage=coverage_file,
        ),
        encoding="utf-8",
    )
    if bib:
        (directory / "evidence.bib").write_text(
            render_module.render_bib(evidence), encoding="utf-8"
        )

    stats = schema.EmitStats(
        top=top or manifest.defaults.top,
        foundational=(foundational if foundational is not None else manifest.defaults.foundational),
        contradicting=contradicting,
        emitted=len(result.packets),
        alternates=len(result.alternates),
        dropped_retracted=result.dropped_retracted,
    )
    # emit closes the run, so it is the stage that can finally say how long the whole thing took.
    timestamps = run.stamp(manifest.timestamps, "emit", started, run.now())
    counts = manifest.counts.model_copy(
        update={
            "emitted": len(result.packets),
            "wall_clock_s": run.wall_clock_seconds(timestamps),
        }
    )
    run.upsert_manifest(directory, emit=stats, counts=counts, timestamps=timestamps)

    payload = {
        "ok": True,
        "run_dir": str(directory),
        "evidence_json": str(directory / "evidence.json"),
        "emit": stats.model_dump(mode="json"),
        "counts": counts.model_dump(mode="json"),
        "top": [
            {
                "rank": packet.rank,
                "title": packet.title,
                "year": packet.year,
                "doi": packet.ids.doi,
                "evidence_level": packet.evidence_level.value,
                "verified": packet.verification.verified,
                "selection_reason": packet.selection_reason.value,
            }
            for packet in result.packets
        ],
    }
    if json_output:
        typer.echo(json.dumps(payload, indent=2))
    else:
        typer.echo(
            f"emitted {len(result.packets)} papers ({result.dropped_retracted} retracted dropped) "
            f"→ {directory / 'evidence.md'}"
        )


@app.command("eval")
def eval_(
    topic: str = typer.Option(..., "--topic", help="Golden topic name, e.g. defaults-savings."),
    run_dir: str | None = typer.Option(None, "--run", help="Run directory. Default: the newest."),
    golden: str | None = typer.Option(
        None, "--golden", help="Golden directory. Default: eval/golden."
    ),
    judge: str | None = typer.Option(None, "--judge", help="Judge output to merge in."),
    stage: str = typer.Option(
        "full",
        "--stage",
        help="`full` scores emit + rerank; `candidates` scores retrieval alone.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Machine-readable stdout."),
    quiet: bool = typer.Option(False, "--quiet", help="Silence the stderr log."),
    log_level: str = typer.Option("INFO", "--log-level", help="Stderr log level."),
) -> None:
    """Score a run against a curated golden topic, and merge an independent judge's scores (§13)."""
    settings = config.load()
    log.configure(log_level, quiet=quiet, settings=settings)

    if stage not in {"full", "candidates"}:
        _fail(f"--stage must be 'full' or 'candidates', not {stage!r}", json_output, code=2)

    try:
        directory = run.resolve_run_dir(run_dir, settings)
        golden_path = evalrun.find_topic(topic, Path(golden) if golden else None)
        golden_topic = evalrun.load_topic(golden_path)
        if stage == "candidates":
            pool, scores = evalrun.load_candidate_pool(directory)
        else:
            files = evalrun.load_run(directory)
    except run.StageInputError as exc:
        _fail_stage(exc, json_output)

    if golden_topic.status != "ratified":
        logger.warning(
            "golden topic %r is still %s — its numbers are provisional until the maintainer "
            "ratifies it",
            golden_topic.topic,
            golden_topic.status,
        )

    if stage == "candidates":
        _emit_candidates_recall(golden_topic, directory, pool, scores, json_output=json_output)
        return

    result = evalrun.score(golden_topic, directory, files)
    result = evalrun.with_cost(
        result,
        directory,
        pool_size=len(files.candidates),
        found=result.found_at_25,
        expected=result.expected,
    )
    if judge:
        try:
            result = evalrun.merge_judge(result, evalrun.load_judge(Path(judge)), files.evidence)
        except run.StageInputError as exc:
            _fail_stage(exc, json_output)

    written = evalrun.result_path(result, run.today().isoformat())
    evalrun.write_result(result, written)

    payload = result.model_dump(mode="json") | {
        "golden_status": golden_topic.status,
        "result_path": str(written),
    }
    if json_output:
        typer.echo(json.dumps(payload, indent=2))
    else:
        typer.echo(
            f"{result.topic}: recall@10 {result.recall_10:.2f}"
            f" ({result.found_at_10}/{result.expected})"
            f" · recall@25 {result.recall_25:.2f} ({result.found_at_25}/{result.expected})"
            + (
                f" · judged precision {result.judged.precision_ge2:.2f}"
                if result.judged and result.judged.precision_ge2 is not None
                else ""
            )
            + (
                f" · in-window {result.judged.precision_ge2_in_window:.2f}"
                if result.judged and result.judged.precision_ge2_in_window is not None
                else ""
            )
        )
        for miss in result.misses:
            typer.echo(f"  miss  {miss.doi} — {miss.why}")
        typer.echo(f"\nwritten to {written} (golden status: {golden_topic.status})")


@app.command("doctor")
def doctor_(
    sources: str | None = typer.Option(
        None,
        "--sources",
        help="Comma-separated subset of openalex,s2,crossref,arxiv,pubmed. Default: all.",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", help="The full per-check table instead of the summary."
    ),
    json_output: bool = typer.Option(
        False, "--json", help="Machine-readable stdout. This is the CI/agent interface."
    ),
    quiet: bool = typer.Option(False, "--quiet", help="Silence the stderr log."),
    log_level: str = typer.Option("INFO", "--log-level", help="Stderr log level."),
) -> None:
    """Invoke every source live (cache bypassed) and report readiness. Exit 3 if unusable.

    The default is a summary; `--verbose` is the per-check table with timings and paths.
    Whichever you pick, the checks and the exit code are the same.
    """
    settings = config.load()
    log.configure(log_level, quiet=quiet, settings=settings)

    try:
        selected = doctor.normalise_sources(sources)
    except ValueError as exc:
        _fail(str(exc), json_output, code=2)

    # Retries stay short: doctor is a gate, not a scan, and a hanging check is a failed check.
    with HttpClient(settings, cache=False, timeout=20.0, max_retries=1) as client:
        report = doctor.run_checks(settings, client, selected)

    if json_output:
        typer.echo(json.dumps(report.to_dict(), indent=2))
    elif verbose:
        typer.echo(doctor.render_table(report))
    else:
        typer.echo(doctor.render_compact(report))
    raise typer.Exit(report.exit_code)


#: Typer generates the script; this is only the line that installs it, per shell.
COMPLETION_HINTS: dict[str, str] = {
    "bash": 'eval "$(research-scan completion bash)"   # add to ~/.bashrc',
    "zsh": 'eval "$(research-scan completion zsh)"    # add to ~/.zshrc',
    "fish": "research-scan completion fish > ~/.config/fish/completions/research-scan.fish",
}


@app.command("completion")
def completion_(
    shell: str = typer.Argument(..., metavar="SHELL", help="bash, zsh or fish."),
) -> None:
    """Print the completion script for SHELL. Evaluate it, or write it where the shell looks.

    \b
    bash   eval "$(research-scan completion bash)"   # add to ~/.bashrc
    zsh    eval "$(research-scan completion zsh)"    # add to ~/.zshrc
    fish   research-scan completion fish > ~/.config/fish/completions/research-scan.fish
    """
    if shell not in COMPLETION_HINTS:
        _fail(f"unknown shell {shell!r}; known: {', '.join(COMPLETION_HINTS)}", False, code=2)
    # Typer's own generator. Writing completion logic by hand would mean maintaining a second
    # description of the command surface, guaranteed to drift from the one Typer already has.
    from typer.completion import get_completion_script

    sys.stdout.write(
        get_completion_script(
            prog_name="research-scan", complete_var="_RESEARCH_SCAN_COMPLETE", shell=shell
        )
    )


@app.command("mcp")
def mcp_(
    http: bool = typer.Option(
        False, "--http", help="Serve over Streamable HTTP with token auth instead of stdio."
    ),
    host: str | None = typer.Option(None, "--host", help="--http only. Default: 127.0.0.1."),
    port: int | None = typer.Option(None, "--port", help="--http only. Default: 8765."),
) -> None:
    """Serve the scan pipeline as an MCP server. Four tools, the same ones the skill drives.

    Default transport is stdio: the server talks MCP on stdin/stdout and nothing else, which is
    what Claude Desktop, Claude Code and other local agent runners launch. There is no token in
    this mode and none is read — the process is trusted because you started it.

    `--http` serves the same four tools over Streamable HTTP with bearer-token auth, for hosting
    the server somewhere a local process cannot reach. It binds loopback and rejects every
    request unless RESEARCH_SCAN_MCP_TOKEN is configured. Putting the token in a URL puts it in
    browser history and proxy logs; see SECURITY.md before exposing it beyond loopback.

    Examples:

        research-scan mcp
        research-scan mcp --http --port 8765
    """
    # Imported here, never at module scope: fastmcp is a heavy import and no other command
    # needs it, so the whole CLI would pay for it on every invocation.
    try:
        from research_scan import mcp_server
    except ImportError as exc:
        # fastmcp ships as a core dependency, so reaching this means a broken install rather
        # than a missing extra.
        _fail(
            f"the MCP server could not be imported ({exc}) — reinstall research-scan",
            False,
            code=2,
        )

    settings = config.load()
    settings.mcp_data_dir.mkdir(parents=True, exist_ok=True)

    if http:
        mcp_server.main(
            host=host or os.environ.get("RESEARCH_SCAN_MCP_HOST", mcp_server.DEFAULT_HOST),
            port=port if port is not None else None,
        )
        return

    if host is not None or port is not None:
        _fail("--host and --port apply to --http only", False, code=2)

    # stdout carries the MCP protocol and nothing else, so every diagnostic goes to stderr and
    # FastMCP's startup banner is suppressed. A stray byte here breaks the handshake.
    logging.basicConfig(
        stream=sys.stderr,
        level=os.environ.get("RESEARCH_SCAN_MCP_LOG", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    # Same line the HTTP transport writes, for the same reason: a stdio server is launched by an
    # agent runner and lives as long as the session, so its log has to say which build it is.
    # stderr only — stdout is the protocol.
    sys.stderr.write(f"{deployment_module.banner()}\n")
    mcp_server.mcp.run(transport="stdio", show_banner=False)


@app.command("schema")
def schema_(
    name: str | None = typer.Option(
        None, "--name", help="One model, e.g. ScanSummary. Default: every model."
    ),
    md: bool = typer.Option(False, "--md", help="Render references/schemas.md instead of JSON."),
) -> None:
    """Print the data contracts. `schema.py` is the source of truth for every file on disk."""
    if md:
        sys.stdout.write(schema.markdown())
        return

    if name is None:
        typer.echo(json.dumps(schema.all_schemas(), indent=2))
        return

    try:
        document = schema.json_schema(name)
    except KeyError:
        _fail(f"unknown model {name!r}; known: {', '.join(schema.MODELS)}", False, code=2)
    typer.echo(json.dumps(document, indent=2))


# --- helpers ----------------------------------------------------------------


def _interactive() -> bool:
    """Whether there is a human on the other end of stdin.

    Its own function because a test runner replaces `sys.stdin` while a command runs, so this
    is the only place the probe can be substituted.
    """
    try:
        return sys.stdin.isatty()
    except (AttributeError, ValueError):  # a closed or exotic stream is not a terminal
        return False


def _stage_setup(log_level: str, quiet: bool, run_dir: str | None, json_output: bool):
    """Every stage after `init` starts the same way: settings, logging, run dir, manifest, clock."""
    settings = config.load()
    log.configure(log_level, quiet=quiet, settings=settings)
    try:
        directory = run.resolve_run_dir(run_dir, settings)
        manifest = run.read_manifest(directory)
    except run.StageInputError as exc:
        _fail_stage(exc, json_output)
    return settings, directory, manifest, run.now()


def _parse_sources(raw: str | None) -> list[SourceName] | None:
    if not raw:
        return None
    names: list[SourceName] = []
    for item in raw.split(","):
        token = item.strip().lower()
        if not token:
            continue
        try:
            names.append(SourceName(token))
        except ValueError:
            known = ", ".join(source.value for source in SourceName)
            raise ValueError(f"unknown source {token!r}; known: {known}") from None
    return names or None


def _render_retrieve(payload: dict) -> str:
    stats = payload["retrieval"]
    lines = [f"run       {payload['run_dir']}"]
    for name, source in sorted(stats["per_source"].items()):
        if source.get("unavailable"):
            lines.append(f"  {name:<10} not built in this version — skipped")
        else:
            lines.append(
                f"  {name:<10} {source['hits']:>4} hits from {source['queried']} queries"
                + (f", {source['failed']} failed" if source["failed"] else "")
            )
    drops = [f"{key} {value}" for key, value in stats["dropped"].items() if value]
    dropped = ", ".join(drops) or "none"
    lines += [
        f"deduped   {stats['deduped_remaining']}",
        f"dropped   {dropped}",
        f"kept      {payload['counts']['deduped']}"
        f"  ({payload['abstract_ratio']:.0%} with abstracts)",
        f"batches   {len(payload['batches'])} × ≤25 in screen-batches/",
        f"cost      ${stats['cost_estimate_usd']:.4f} in {stats['duration_s']:.1f}s",
    ]
    return "\n".join(lines)


def _emit_candidates_recall(
    golden_topic: schema.GoldenTopic,
    directory: Path,
    pool: dict,
    scores: dict | None,
    *,
    json_output: bool,
) -> None:
    """Print recall-at-candidates and write it beside the full result, under its own name."""
    recall = evalrun.score_candidates(golden_topic, pool, scores)
    result = schema.EvalResult(
        topic=golden_topic.topic,
        run_dir=str(directory),
        expected=recall.expected,
        found_at_10=0,
        found_at_25=0,
        recall_10=0.0,
        recall_25=0.0,
        candidates=recall,
    )
    result = evalrun.with_cost(
        result, directory, pool_size=len(pool), found=recall.found, expected=recall.expected
    )
    written = evalrun.result_path(result, f"{run.today().isoformat()}-candidates")
    evalrun.write_result(result, written)

    payload = {
        "topic": golden_topic.topic,
        "run_dir": str(directory),
        "stage": "candidates",
        "golden_status": golden_topic.status,
        "result_path": str(written),
        "profile": result.profile.value if result.profile else None,
        "pool_size": result.pool_size,
        "recall_per_100_screened": result.recall_per_100_screened,
        "candidates": recall.model_dump(mode="json"),
    }
    if json_output:
        typer.echo(json.dumps(payload, indent=2))
        return

    typer.echo(
        f"{golden_topic.topic}: recall@candidates {recall.recall:.2f}"
        f" ({recall.found}/{recall.expected})"
        + ("" if recall.screened else " · screen.json absent, scores unavailable")
    )
    for hit in recall.papers:
        label = hit.title or hit.doi
        if not hit.present:
            typer.echo(f"  MISS  {label}")
            continue
        score = "-" if hit.screen_score is None else str(hit.screen_score)
        typer.echo(
            f"  HIT   {label}\n"
            f"          cid {hit.cid} · matched by {hit.matched_by} · screen {score}\n"
            f"          origins: {', '.join(hit.origins) or '(none)'}"
        )
    typer.echo(f"→ {written}")


def _fail(message: str, json_output: bool, *, code: int) -> None:
    if json_output:
        typer.echo(json.dumps({"ok": False, "error": message}), err=True)
    else:
        typer.echo(f"error: {message}", err=True)
    raise typer.Exit(code)


def _fail_stage(exc: run.StageInputError, json_output: bool) -> None:
    """Exit 2 with the error list the agent needs to repair its file (§6)."""
    if json_output:
        typer.echo(json.dumps(exc.payload(), indent=2), err=True)
    else:
        typer.echo(f"error: {exc.message}", err=True)
        for line in exc.lines:
            typer.echo(f"  - {line}", err=True)
    raise typer.Exit(2)
