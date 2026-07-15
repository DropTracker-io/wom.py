# DropTracker fork of wom.py

Fork of [`Jonxslays/wom.py`](https://github.com/Jonxslays/wom.py) branched from
the **1.0.0** release (`3b7cd0e`). DropTracker pins this instead of PyPI `wom.py`
so the whole team, CI, and prod run identical, versioned code — no more
hand-patching `site-packages`.

Branch: `droptracker`. Pin it in `requirements.txt`:

```
wom.py @ git+https://github.com/DropTracker-io/wom.py@<commit-sha>
```

Upstream is unmaintained at the 1.0.0 line (current release is 3.x, a breaking
change we haven't migrated to).

## What diverges from upstream 1.0.0

### 1. Metric-tolerant decoding (the important one)

`wom.py` decodes API responses with **msgspec typed decoders**. Response fields
holding a metric were typed as the `Metric` enum, and msgspec's strict enum
decoding **fails the entire response** on any value not in the enum. WOM adds
new metrics (bosses, skills) to the live API continuously, so a single unknown
boss in one player's snapshot broke `get_details` / `update_player` /
`get_gains` calls outright — and enums can't be extended at runtime, so no
downstream shim could fix it.

Fix: metric-bearing **response** fields are now typed `MetricValue` (`== str`),
so unknown metrics pass through as their slug string instead of raising. Applies
to `Achievement`, `Gains`, snapshot `skills`/`bosses`/`activities`/`computed`
dict keys, `Record`, `Competition`, `MetricLeaders`, etc. `Metric` remains a
str-valued enum, so:

- `snapshot.bosses[Metric.Zulrah]` still works (the enum's `__hash__`/`__eq__`
  are value-based, so a str-keyed dict is indexable by the enum constant), and
- **request**-side params (`service.get_gains(metric=Metric.Zulrah)`) are
  unchanged — those still take the enum and use `.value`.

Regression test: `tests/test_dt_metric_tolerance.py` (decodes a metric
deliberately absent from the enum, so it protects even when the enum is current).

### 2. Enum kept current with the live API

`wom/enums.py` and `wom/models/players/enums.py` carry metrics/countries the
live WOM service tracks beyond upstream 1.0.0: Sailing, CollectionsLogged, the
bosses Amoxliatl, Brutus, Doom of Mokhaiotl, The Hueycoatl, Maggot King,
Shellbane Gryphon, The Royal Titans, Yama; country codes GB_SCT / GB_WLS.

Thanks to (1) this is now **best-effort, not load-bearing** — an out-of-date
enum no longer crashes anything; it only means new metrics come back as plain
strings and DropTracker's `utils/wiseoldman.py` family-mapping (skill-vs-boss)
doesn't recognize them until added. When you add a metric here, also mirror the
boss/skill slug into the `_WOM_*_SLUGS` block in the app's `utils/wiseoldman.py`.

## Maintenance

- **A new boss/skill appears and things keep working?** Nothing is on fire —
  decoding is tolerant. Add the enum member here (and the app slug) when you want
  WOM-hybrid event tracking to recognize it; the app logs a warning naming what's
  unmapped. Then bump the `requirements.txt` pin.
- **Rebuilding a prod venv:** just `pip install -r requirements.txt` — it pulls
  this fork. No manual `site-packages` patching, ever again.
