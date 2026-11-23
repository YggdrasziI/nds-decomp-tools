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

The tools run from inside the project, whose root holds a `decomp.toml` (see
decomp-tools: `versions`, the first one being the default, and `[compiler] path` /
`flags` of the game units). The DS settings are in its `[nds]` table (see
`nds_config.py`):

```toml
[nds]
include_dirs = ["include", "libs/nitro/include"]  # optional
ghidra_project = "game"            # Ghidra project game_<version>
ghidra_env = "GAME_GHIDRA_PROJECT" # variable holding the Ghidra project folder

[nds.absolute_symbols]             # lcf_keep.py: NitroSDK link-time constants
SDK_IRQ_STACKSIZE = 0x400

[nds.candidates.eur]               # unit_candidates.py: game code per module
main = [[0x02000BA0, 0x02073ED0]]  # [start, end) ranges
ov001 = "text"                     # or the module's whole .text
```

`mwcc_blocks.py` also imports the project's own `tools/permute.py`.

Tools
=====

| Tool | Purpose |
|---|---|
| `nds_config.py` | Settings of these tools, from `decomp.toml` |
| `lcf_keep.py` | Run `dsd lcf`, then keep `.exception` in the dead-stripping link, define the NitroSDK link-time constants and list the functions of sourced units in FORCE_ACTIVE |
| `objdiff_prune.py` | Run `dsd objdiff`, then drop the base object of units that have no source yet, so objdiff counts them as not decompiled instead of failing |
| `unit_candidates.py` | Small functions of the game regions not delinked yet, by module (overlays included), with their calls and callers |
| `compiler_sweep.py` | Compile sources with several mwccarm versions and find their functions in the ROM (main, ITCM, DTCM, overlays), relocated words masked |
| `decl_search.py` | Search declaration orders, splits and local types of near-match functions |
| `mwcc_irdump.py` | Dump mwccarm 2.0/sp1p5's IRO optimizer flowgraph for one source (patched copy of the compiler) |
| `mwcc_blocks.py` | Trace where mwccarm 2.0/sp1p5 splits code into basic blocks (Windows debugger) |
| `mwcc_sched.py` | Trace mwccarm 2.0/sp1p5's instruction scheduler on one function |
| `mangle.py` | Mangled names of the functions and data of a source, from the game compiler |
| `gdb_trace.py` | Minimal GDB remote client for an emulator's ARM9 stub: memory reads, call traces |
| `ghidra_sync.py` | Push the dsd symbols to a Ghidra project headless (dsd-ghidra's SyncDsd) |
| `m2ctx.py` | Preprocess the includes of a source into a context for decomp.me or m2c |
| `transform_dep.py` | Turn the Windows paths of the `.d` files written by mwccarm under Wine into host paths |
| `download_tool.py`, `get_platform.py` | Download dsd, objdiff-cli and the other build tools (retries on a failed or empty response) |

Provenance
==========

- `get_platform.py`, `download_tool.py`, `mangle.py`, `m2ctx.py` and
  `transform_dep.py` come from [Yotona/twewy](https://github.com/Yotona/twewy)
  (CC0-1.0); `transform_dep.py` comes from
  [encounter/dtk-template](https://github.com/encounter/dtk-template) (CC0-1.0)
  through it (its notice is kept). Modified: download retries (`download_tool.py`),
  project root, compiler and include directories from `decomp.toml` (`mangle.py`,
  `m2ctx.py`).
- `ghidra_sync.py` patches, at run time, the `SyncDsd.java` script of the installed
  [dsd-ghidra](https://github.com/AetiasHax/dsd-ghidra) extension; no code of it is
  kept here.
- Everything else is original work released under CC0-1.0 (`LICENSE`).
