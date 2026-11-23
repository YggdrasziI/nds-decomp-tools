nds-decomp-tools
================

> [!IMPORTANT]
> AI Disclosure:
> AI was used for the following tasks:
> - Writing commentary (primarily translating into English and formatting).
> - Documenting and citing the various sources used in the project.
> - Writing code (C, C++, Python, etc.—I used it as a tool) and reviewing my own work (yes, some code was written by AI, but it was verified by a human; I didn't simply type "Claude, decompile this for me").

Shared tooling for matching decompilations of Nintendo DS games built with
[ds-decomp](https://github.com/AetiasHax/ds-decomp) (`dsd`), mwccarm and
[objdiff](https://github.com/encounter/objdiff). It is meant to be used as a git
submodule at `tools/nds/` of a project, next to
[decomp-tools](https://github.com/YggdrasziI/decomp-tools) at `tools/common/`, which
holds what does not depend on the platform (function comparison, report gate,
progress card, trace guard, checksum, ninja writer).

Projects using it:

- [ts2-castaway-decomp](https://github.com/YggdrasziI/ts2-castaway-decomp): The Sims 2: Castaway
- [dqmj2-decomp](https://github.com/YggdrasziI/dqmj2-decomp): Dragon Quest Monsters: Joker 2
- [dqmj2p-decomp](https://github.com/YggdrasziI/dqmj2p-decomp): Dragon Quest Monsters: Joker 2 Professional

Setup
=====

```sh
git submodule add https://github.com/YggdrasziI/nds-decomp-tools.git tools/nds
git submodule add https://github.com/YggdrasziI/decomp-tools.git tools/common
```

The tools run from the project root, which holds a `decomp.toml` (see
decomp-tools).

Tools
=====

| Tool | Purpose |
|---|---|
| `objdiff_prune.py` | Run `dsd objdiff`, then drop the base object of units that have no source yet, so objdiff counts them as not decompiled instead of failing |
| `m2ctx.py` | Preprocess the includes of a source into a context for decomp.me or m2c; include directories from `[m2ctx] include_dirs` of `decomp.toml` |
| `transform_dep.py` | Turn the Windows paths of the `.d` files written by mwccarm under Wine into host paths |
| `get_platform.py` | Host system, architecture and executable suffix, for the tool downloads |

Provenance
==========

- `get_platform.py`, `m2ctx.py` and `transform_dep.py` come from
  [Yotona/twewy](https://github.com/Yotona/twewy) (CC0-1.0); `transform_dep.py`
  comes from [encounter/dtk-template](https://github.com/encounter/dtk-template)
  through it (its notice is kept). `m2ctx.py` is modified: project root from
  `decomp.toml`, include directories from its settings.
- Everything else is original work released under CC0-1.0 (`LICENSE`).
