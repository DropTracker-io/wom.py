#!/usr/bin/env python3
"""Keep ``wom/enums.py`` current with the live Wise Old Man metric catalogue.

WOM adds skills/bosses/activities to its API continuously. Thanks to the
metric-tolerant decoding in this fork, an out-of-date enum never *crashes*
anything — but recognising a new metric (for DropTracker's WOM-hybrid event
tracking family separation, and for `Metric.X` ergonomics) still means adding
the enum member. This does that mechanically, so no human is needed for the
common case.

Source of truth: ``@wise-old-man/utils`` — the package WOM's own API is built
on. Its published type defs expose the authoritative Skill/Activity/Boss slug
lists as ``readonly NAME: "slug";`` constants; we diff those against our enum
and append any missing members (additive only — never renames or removes).

Exit codes:
  0  enum already current, no changes.
  10 new metrics were added (files modified) — CI commits + tests them.
  1  something went wrong (unreachable source / unparseable / anchor missing) —
     CI fails loudly so a human looks. This is the ONLY path that needs us.

Run: ``python tools/sync_metrics.py`` (add ``--check`` to only report, no write).
"""
from __future__ import annotations

import pathlib
import re
import sys
import urllib.request

SOURCE = "https://unpkg.com/@wise-old-man/utils@latest/dist/index.d.ts"
ENUMS = pathlib.Path(__file__).resolve().parents[1] / "wom" / "enums.py"

# (authoritative const in the .d.ts, enum section header, frozenset docstring)
FAMILIES = [
    ("Skill", "    # Skills\n", '"""Set containing skills."""'),
    ("Activity", "    # Activities\n", '"""Set containing activities."""'),
    ("Boss", "    # Bosses\n", '"""Set containing bosses."""'),
]


def _fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "dt-wom-sync"})
    with urllib.request.urlopen(req, timeout=45) as resp:  # noqa: S310 (fixed https URL)
        return resp.read().decode("utf-8")


def _authoritative(dts: str, const: str) -> list[str]:
    """Ordered slug list for one metric family from the .d.ts const object."""
    m = re.search(rf"declare const {const}: {{([^}}]*)}}", dts)
    if not m:
        raise RuntimeError(f"could not locate `declare const {const}` in the source")
    slugs = re.findall(r'readonly \w+: "([^"]+)";', m.group(1))
    if not slugs:
        raise RuntimeError(f"`{const}` block parsed but held no slugs (format change?)")
    return slugs


def _member_name(slug: str, taken: set[str]) -> str:
    name = "".join(part.capitalize() for part in slug.split("_"))
    if not name or name[0].isdigit():
        name = "M" + name
    base, i = name, 2
    while name in taken:
        name, i = f"{base}{i}", i + 1
    taken.add(name)
    return name


def main(check_only: bool) -> int:
    dts = _fetch(SOURCE)
    text = ENUMS.read_text()
    existing = set(re.findall(r'^    \w+ = "([^"]+)"$', text, re.M))
    taken = set(re.findall(r'^    (\w+) = "[^"]+"$', text, re.M))

    added: dict[str, list[tuple[str, str]]] = {}
    for const, section_anchor, set_docstring in FAMILIES:
        new_slugs = [s for s in _authoritative(dts, const) if s not in existing]
        if not new_slugs:
            continue
        pairs = [(_member_name(s, taken), s) for s in new_slugs]
        added[const] = pairs

        member_lines = "".join(f'    {name} = "{slug}"\n' for name, slug in pairs)
        if section_anchor not in text:
            raise RuntimeError(f"enum section anchor missing: {section_anchor!r}")
        text = text.replace(section_anchor, section_anchor + member_lines, 1)

        set_anchor = f'    }}\n)\n{set_docstring}'
        if set_anchor not in text:
            raise RuntimeError(f"frozenset anchor missing for {const}")
        set_lines = "".join(f"        Metric.{name},\n" for name, _ in pairs)
        text = text.replace(set_anchor, set_lines + set_anchor, 1)

    # Defensive: guarantee every frozenset element carries a trailing comma, so
    # a comma-less last element (e.g. left by an old hand-edit) can never make
    # the next inserted element a syntax error.
    text = re.sub(r"^(        Metric\.\w+)$", r"\1,", text, flags=re.M)

    if not added:
        print("wom enums already current with @wise-old-man/utils — no changes.")
        return 0

    summary = "; ".join(
        f"{const}: " + ", ".join(f"{n}={s!r}" for n, s in pairs)
        for const, pairs in added.items()
    )
    print(f"New metrics: {summary}")
    if check_only:
        print("(--check: not writing)")
        return 10
    ENUMS.write_text(text)
    print(f"Updated {ENUMS}")
    return 10


if __name__ == "__main__":
    try:
        sys.exit(main(check_only="--check" in sys.argv[1:]))
    except Exception as exc:  # noqa: BLE001 — surface any failure as exit 1 for CI
        print(f"sync_metrics FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
