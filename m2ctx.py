#!/usr/bin/env python3

import sys
import pyperclip
import subprocess
import os
from pathlib import Path
import argparse
import re
import tempfile
import tomllib

parser = argparse.ArgumentParser(description="Generates a context for decomp.me")
parser.add_argument('file', help="Input file to preprocess")
parser.add_argument('-f', type=str, dest='out_file', required=False, help='Output context file')
parser.add_argument('-c', action=argparse.BooleanOptionalAction, dest='clipboard', required=False, help='Copy output to clipboard')
parser.add_argument('-e', type=str, dest='encoding', required=False, default="shift-jis", help='Input file encoding')
parser.add_argument('-v', action=argparse.BooleanOptionalAction, dest='verbose', required=False, help='Verbose error output')
parser.add_argument('-D', action='append', dest='defines', default=[], metavar='MACRO', help='Define a macro for the preprocessor (e.g. -D REGION_USA)')
args = parser.parse_args()

def find_root() -> Path:
    '''Project root: the nearest directory holding a decomp.toml, from the current one up.'''
    here = Path.cwd().resolve()
    for d in (here, *here.parents):
        if (d / "decomp.toml").is_file():
            return d
    sys.exit("decomp.toml not found (run from inside the project)")

root_dir = find_root()

# Include directories, relative to the project root: [m2ctx] include_dirs of decomp.toml
DEFAULT_INCLUDE_DIRS = [
    'include',
    'libs/c/include',
    'libs/cpp/include',
    'libs/cri/include',
    'libs/nitro/include',
    'libs/runtime/include',
]
config = tomllib.loads((root_dir / "decomp.toml").read_text(encoding="utf-8"))
include_dirs = config.get("m2ctx", {}).get("include_dirs", DEFAULT_INCLUDE_DIRS)

CXX_FLAGS = ['-nostdinc', *[f'-I{d}' for d in include_dirs]]

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

# Finds all lines starting with #include followed by <...> or "..."
INCLUDE_REGEX = r'^\s*#\s*include\s*([<"][\S ]+[>"])\s*$'
# Finds all line comments and multiline comments
COMMENT_REGEX = r'\/\/.*$|\/\*(?:.|\r|\n)+?\*\/'

with open(args.file, 'r', encoding=args.encoding) as f:
    contents = f.read()
contents = re.sub(COMMENT_REGEX, '', contents, count=0, flags=re.MULTILINE)
includes = re.findall(INCLUDE_REGEX, contents, flags=re.MULTILINE)

_, suffix = os.path.splitext(args.file)

try:
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        # Write includes
        for include in includes:
            tmp_file.write(f'#include {include}\n'.encode())
        tmp_file.flush()

        # Ensure the file is written to disk
        os.fsync(tmp_file.fileno())

        # Close the file so GCC can access it
        tmp_file.close()

        # Run preprocessor
        try:
            ctx: str = subprocess.check_output([
                'gcc',
                '-E', '-P', '-fworking-directory', '-undef', '-dD',
                *CXX_FLAGS,
                *[f'-D{d}' for d in args.defines],
                tmp_file.name
            ], cwd=root_dir, encoding=args.encoding)
        except subprocess.CalledProcessError as e:
            eprint(f"Failed to preprocess '{args.file}'")
            if args.verbose: eprint(e)
            else: eprint("Use -v for more verbose error output")
            exit(1)

finally:
    # Clean up the temporary file
    try:
        if 'tmp_file' in locals():
            os.unlink(tmp_file.name)
    except:
        pass  # Ignore cleanup errors

lines = ctx.splitlines(True)
for i in reversed(range(len(lines))):
    if lines[i].startswith('#define __cplusplus'): lines.pop(i)
    elif lines[i].startswith('#define __STDC_HOSTED__'): lines.pop(i)
    elif lines[i].startswith('#define __STDC__'): lines.pop(i)
    elif lines[i].startswith('#define __STDC_VERSION__'): lines.pop(i)

ctx = ''.join(lines)

if args.out_file:
    try:
        with open(args.out_file, "w",  encoding="utf-8") as file:
            file.write(ctx)
    except OSError as e:
        eprint(f"Failed to write file '{args.out_file}'")
        if args.verbose: eprint(e)
        else: eprint("Use -v for more verbose error output")
        exit(1)
if args.clipboard:
    pyperclip.copy(ctx)
    eprint("Copied context to clipboard")
if args.out_file is None and not args.clipboard:
    print(ctx)