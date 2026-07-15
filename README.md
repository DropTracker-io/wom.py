<div align="center">
    <h1>wom.py</h1>
    <a href="https://pypi.org/project/wom.py"><img height="20" alt="Stable version" src="https://img.shields.io/pypi/v/wom.py?label=stable&logo=pypi"></a>
    <a href="https://github.com/Jonxslays/wom.py/blob/master/LICENSE"><img height="20" alt="License" src="https://img.shields.io/pypi/l/wom-py?label=license"></a>
    <a href="https://python.org"><img height="20" alt="Python versions" src="https://img.shields.io/pypi/pyversions/wom-py?label=python&logo=python"></a>
    <a href="https://codeclimate.com/github/Jonxslays/wom.py/maintainability"><img height="20" alt="Maintainability" src="https://api.codeclimate.com/v1/badges/367fb667ef372064fe5a/maintainability" /></a>
    <a href="https://codeclimate.com/github/Jonxslays/wom.py/test_coverage"><img height="20" alt="Coverage" src="https://api.codeclimate.com/v1/badges/367fb667ef372064fe5a/test_coverage" /></a>
</div>

An asynchronous wrapper for the [Wise Old Man API](https://docs.wiseoldman.net/).

The library aims to make it easy to interact with the Wise Old Man API by
providing service methods matching all available endpoints and model classes
for data consistency.

---

> ### ℹ️ This is the DropTracker fork of wom.py
>
> A maintained fork of upstream [`wom.py`](https://github.com/Jonxslays/wom.py)
> **1.0.0** with one goal: **new Old School RuneScape content never breaks the
> client.** All credit for wom.py goes to
> [@Jonxslays](https://github.com/Jonxslays); this fork stays MIT-licensed.
>
> - **Metric-tolerant decoding.** Upstream decodes metric fields as a strict
>   enum, so a metric WOM added that the pinned client didn't know (a new
>   boss/skill) failed the *entire* response — one unknown boss in a snapshot
>   broke `get_details`. Here, metric-bearing response fields decode as `str`,
>   so unknown metrics — and any new fields WOM adds — pass through instead of
>   raising. `Metric` is still a str-valued enum, so
>   `snapshot.bosses[Metric.Zulrah]` and `metric=Metric.X` params work exactly
>   as before.
> - **Self-updating enum.** A weekly GitHub Action diffs the enum against WOM's
>   authoritative [`@wise-old-man/utils`](https://www.npmjs.com/package/@wise-old-man/utils)
>   catalogue and commits any new metrics automatically — a human is pinged
>   only if that job fails.
>
> So you don't track WOM's releases by hand, and new game content can't take
> the client down. Guarantees + caveats: **[DROPTRACKER_FORK.md](DROPTRACKER_FORK.md)**.
>
> **Install (floats with our updates):**
> ```
> pip install "wom.py @ git+https://github.com/DropTracker-io/wom.py@droptracker"
> ```
> Pin a specific commit instead of `@droptracker` for a reproducible build.

---

## Documentation

- [Stable](https://jonxslays.github.io/wom.py/)
- [Development](https://jonxslays.github.io/wom.py/dev/)

## Getting started

If you're new to using wom.py, check out our
[getting started guide](https://jonxslays.github.io/wom.py/stable/getting-started/installation/).

## Problems

If you're experiencing a problem with the library, please open an issue
[here](https://github.com/Jonxslays/wom.py/issues), after first confirming
a similar issue was not already created.

## What is Wise Old Man

Wise Old Man is an open source Oldschool Runescape player progress tracker.

If you're interested in learning more about the Wise Old Man project, consider checking out any of these links:

- [Website](https://wiseoldman.net/)
- [API documentation](https://docs.wiseoldman.net/)
- [Github repository](https://wiseoldman.net/github)
- [Discord community](https://wiseoldman.net/discord)
- [Support the developers on Patreon](https://wiseoldman.net/patreon)

Some of the popular features include:

- Experience tracking
- Boss killcounts
- Player achievements
- Group competitions
- Global leaderboards
- A discord bot for interacting with the API

## Contributing

wom.py is open to contributions. Check out the
[contributing guide](https://github.com/Jonxslays/wom.py/blob/master/CONTRIBUTING.md) to learn how.

## License

wom.py is licensed under the
[MIT License](https://github.com/Jonxslays/wom.py/blob/master/LICENSE).
