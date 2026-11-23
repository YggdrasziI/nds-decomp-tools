"""Settings of the Nintendo DS tools, read from the project's `decomp.toml`.

Built on `decomp_config.py` of decomp-tools (submodule `tools/common/`, next to this
one): project root, versions (the first one is the default), `[compiler]`. Keys read
here:

    [nds]
    include_dirs = ["include", "libs/nitro/include"]   # optional; default: the
                                                      # DEFAULT_INCLUDE_DIRS that exist
    ghidra_project = "game"          # optional: Ghidra project name before _<version>
                                     # (default: root folder's name)
    ghidra_env = "GAME_GHIDRA_PROJECT"   # optional: environment variable holding the
                                     # Ghidra project folder (default DECOMP_GHIDRA_PROJECT)

    [nds.absolute_symbols]           # optional: lcf_keep.py, link-time constants
    SDK_IRQ_STACKSIZE = 0x400

    [nds.candidates.<version>]       # optional: unit_candidates.py, game code per
    main = [[0x02000BA0, 0x02073ED0]]   # module: [start, end) ranges, or "text" for
    ov001 = "text"                   # the module's whole .text
"""

import os
import re
import sys
from pathlib import Path

sys.path.insert(1, str(Path(__file__).resolve().parent.parent / "common"))
import decomp_config  # noqa: E402
from decomp_config import CONFIG, DEFAULT_VERSION, ROOT, VERSIONS  # noqa: E402,F401

NDS = CONFIG.get("nds", {})

DEFAULT_INCLUDE_DIRS = [
    "include",
    "libs/c/include",
    "libs/cpp/include",
    "libs/cri/include",
    "libs/nitro/include",
    "libs/runtime/include",
]


def include_dirs() -> list[str]:
    """Include directories, relative to the root (`[nds] include_dirs`, or the default
    ones that exist)."""
    if "include_dirs" in NDS:
        return list(NDS["include_dirs"])
    return [d for d in DEFAULT_INCLUDE_DIRS if (ROOT / d).is_dir()]


def compiler_path() -> str:
    """The game compiler, relative to the root (`[compiler] path` of decomp.toml)."""
    cc = CONFIG.get("compiler", {})
    if "path" not in cc:
        sys.exit("decomp.toml: [compiler] path is needed")
    return cc["path"]


def compiler_flags() -> list[str]:
    """Code generation flags of the game units (`[compiler] flags`)."""
    return CONFIG.get("compiler", {}).get("flags", "").split()


def region_define(version: str) -> str:
    """The version's preprocessor symbol (REGION_EUR for eur), as tools/configure.py sets it."""
    return "REGION_" + re.sub(r"\W", "_", version).upper()


def absolute_symbols() -> dict[str, int]:
    return dict(NDS.get("absolute_symbols", {}))


def candidate_regions(version: str) -> dict:
    """{module: [(start, end), ...] or None (whole .text)} of unit_candidates.py."""
    out = {}
    for module, value in NDS.get("candidates", {}).get(version, {}).items():
        out[module] = None if value == "text" else [tuple(r) for r in value]
    return out


GHIDRA_PROJECT: str = NDS.get("ghidra_project", ROOT.name.replace("-", "_"))
GHIDRA_ENV: str = NDS.get("ghidra_env", "DECOMP_GHIDRA_PROJECT")


def ghidra_project_dir() -> str | None:
    return os.environ.get(GHIDRA_ENV)
